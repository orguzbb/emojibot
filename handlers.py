from __future__ import annotations
import time
import re
import json
import random
import logging
import asyncio
import urllib.parse
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

from aiogram import Bot, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    PreCheckoutQuery,
    LabeledPrice,
    InputSticker,
    BufferedInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter, TelegramAPIError

from config import BOT_USERNAME, TEMPLATES_DIR, FONTS_DIR, WEBAPP_URL
from lottie_processor import (
    process_tgs_template,
    process_all_templates,
    validate_and_clean_svg,
    cache_svg,
    get_cached_svg,
    to_svg_slug
)
from database import (
    add_or_update_user,
    increment_user_packs,
    save_user_pack,
    get_user_packs,
    get_user_balance,
    add_user_balance,
    deduct_user_balance,
    get_emoji_price,
    get_referral_bonus,
    get_referral_stats,
    use_promocode
)

logger = logging.getLogger(__name__)
router = Router()

DEFAULT_EMOJIS = ["⭐", "🔥", "⚡", "✨", "💎", "👑", "🚀", "❤️", "🌟", "💫", "🎯", "🍀", "🏆", "🌟"]
ACTIVE_USERS = set()

FONTS_MAP = {
    "stapel": {
        "name": "Stapel",
        "file": "stapel.ttf",
        "desc": "Qalin & Geometrik"
    },
    "inter": {
        "name": "Inter",
        "file": "inter.ttf",
        "desc": "Klassik & Toza"
    },
    "grobold": {
        "name": "Grobold",
        "file": "Grobold.ttf",
        "desc": "Qalin & Zamonaviy"
    },
    "svg": {
        "name": "SVG Vektor",
        "file": "stapel.ttf",
        "desc": "Vektor Grafikasi"
    }
}

CYRILLIC_TO_LATIN = {
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo', 'Ж': 'J', 'З': 'Z',
    'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R',
    'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'X', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sh',
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya', 'Ў': 'O', 'Қ': 'Q', 'Ғ': 'G', 'Ҳ': 'H'
}


class UserStates(StatesGroup):
    waiting_for_promocode = State()
    waiting_for_topup_amount = State()


def to_name_slug(text: str) -> str:
    res = []
    for ch in text.upper():
        res.append(CYRILLIC_TO_LATIN.get(ch, ch))
    slug = "".join(res)
    slug = re.sub(r'[^a-zA-Z0-9]', '', slug).lower()
    if not slug or not slug[0].isalpha():
        slug = f"e{slug}"
    return slug[:18]


async def create_unique_custom_emoji_set(
    bot_instance,
    user_id: int,
    base_slug: str,
    pack_title: str,
    stickers: list
) -> str:
    """
    Creates a new custom emoji set trying the cleanest name first:
    1. {clean_slug}_by_{BOT_USERNAME}
    2. {clean_slug}_1_by_{BOT_USERNAME}
    3. {clean_slug}_2_by_{BOT_USERNAME}
    ...
    Automatically detecting occupied names and falling back to next available index.
    """
    clean_slug = to_name_slug(base_slug) if base_slug else "emoji"
    if not clean_slug or not clean_slug[0].isalpha():
        clean_slug = f"e{clean_slug}"
    clean_slug = clean_slug[:24]

    candidates = [
        f"{clean_slug}_by_{BOT_USERNAME}",
        f"{clean_slug}_1_by_{BOT_USERNAME}",
        f"{clean_slug}_2_by_{BOT_USERNAME}",
        f"{clean_slug}_3_by_{BOT_USERNAME}",
        f"{clean_slug}_4_by_{BOT_USERNAME}",
        f"{clean_slug}_5_by_{BOT_USERNAME}"
    ]
    for n in range(6, 25):
        candidates.append(f"{clean_slug}_{n}_by_{BOT_USERNAME}")
    candidates.append(f"{clean_slug}_{random.randint(100, 99999)}_by_{BOT_USERNAME}")

    last_err = None
    for cand_name in candidates:
        try:
            await bot_instance.create_new_sticker_set(
                user_id=user_id,
                name=cand_name,
                title=pack_title,
                stickers=stickers,
                sticker_type="custom_emoji"
            )
            logger.info(f"Successfully created emoji set '{cand_name}' for user {user_id}")
            return cand_name
        except Exception as e:
            err_str = str(e).lower()
            if any(k in err_str for k in ["occupied", "already taken", "invalid_short_name", "short_name_occupied", "name_invalid", "already used", "bad request: shortname"]):
                logger.info(f"Pack name '{cand_name}' is occupied on Telegram. Trying next candidate...")
                last_err = e
                continue
            else:
                logger.error(f"Error creating sticker set '{cand_name}': {e}")
                raise e
    raise last_err or Exception("Barcha nomlar band, iltimos boshqa nom tanlang.")


def get_main_menu_markup(user_id: int) -> InlineKeyboardMarkup:
    balance = get_user_balance(user_id)
    ref_bonus = get_referral_bonus()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Web App ☰",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"💳 Hamyon ({balance} ⭐)",
                    callback_data="menu_wallet"
                ),
                InlineKeyboardButton(
                    text="🏷 Promokod",
                    callback_data="menu_promo"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"👥 Do'stlarni taklif qilish (+{ref_bonus} ⭐)",
                    callback_data="menu_referral"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📁 Mening To'plamlarim",
                    callback_data="cmd_mypacks_cb"
                ),
                InlineKeyboardButton(
                    text="ℹ️ Yordam & Narxlar",
                    callback_data="cmd_help_cb"
                )
            ]
        ]
    )


# ==================== /START & REFERRAL ====================

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    user = message.from_user
    args = message.text.split()
    ref_id = None

    if len(args) > 1:
        ref_arg = args[1].strip()
        digits = re.findall(r'\d+', ref_arg)
        if digits:
            try:
                candidate_id = int(digits[0])
                if candidate_id != user.id:
                    ref_id = candidate_id
            except (ValueError, TypeError):
                ref_id = None

    is_new, awarded_ref = add_or_update_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        referred_by=ref_id
    )

    if awarded_ref:
        ref_bonus = get_referral_bonus()
        new_ref_bal = add_user_balance(
            awarded_ref,
            ref_bonus,
            tx_type="referral_bonus",
            description=f"Yangi do'st taklif qilindi: {user.first_name or user.id}"
        )
        try:
            await bot.send_message(
                chat_id=awarded_ref,
                text=(
                    f"🎉 <b>Yangi do'stingiz botga qo'shildi!</b>\n\n"
                    f"👤 Foydalanuvchi: <b>{user.first_name or 'Do`stingiz'}</b>\n"
                    f"🎁 Balansingizga <b>+{ref_bonus} ⭐ Stars</b> qo'shildi!\n"
                    f"💰 Joriy balansingiz: <b>{new_ref_bal} ⭐ Stars</b>"
                ),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.warning(f"Referrer xabarnoma xatosi {awarded_ref}: {e}")

    price = get_emoji_price()
    balance = get_user_balance(user.id)

    welcome_text = (
        f"👋 <b>Assalomu alaykum, {user.first_name or 'Hurmatli foydalanuvchi'}!</b>\n\n"
        "✨ Ushbu bot orqali siz o'zingizning ismingiz bilan "
        "<b>Telegram Premium Animatsiyali Emoji Pack</b> yaratishingiz mumkin!\n\n"
        f"💰 <b>Sizning balansingiz:</b> <b>{balance} ⭐ Stars</b>\n"
        f"💎 <b>1 ta emoji narxi:</b> <b>{price} ⭐ Stars</b>\n\n"
        "🚀 <b>Mini App orqali foydalanish:</b>\n"
        "Pastdagi <b>📱 Mini App</b> tugmasini bosing va 100+ shablonlarni jonli prevyuda ko'ring!\n\n"
        "🔤 <b>Bot orqali yaratish:</b>\n"
        "Ismingizni botga yozing (masalan: <code>ASILBEK</code>)."
    )

    await message.answer(welcome_text, reply_markup=get_main_menu_markup(user.id), parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "menu_main")
async def cb_menu_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = callback.from_user
    price = get_emoji_price()
    balance = get_user_balance(user.id)

    text = (
        f"👋 <b>Bosh menyu</b>\n\n"
        f"💰 <b>Sizning balansingiz:</b> <b>{balance} ⭐ Stars</b>\n"
        f"💎 <b>1 ta emoji narxi:</b> <b>{price} ⭐ Stars</b>\n\n"
        "<i>Ismingizni yozib yuboring yoki quyidagi bo'limlardan birini tanlang:</i>"
    )
    await callback.message.edit_text(text, reply_markup=get_main_menu_markup(user.id), parse_mode=ParseMode.HTML)
    await callback.answer()


# ==================== WALLET & BALANCE (HAMYON) ====================

@router.callback_query(F.data == "menu_wallet")
@router.message(Command("balance"))
@router.message(Command("wallet"))
async def handle_wallet_menu(event: Union[Message, CallbackQuery], state: FSMContext):
    await state.clear()
    user_id = event.from_user.id
    balance = get_user_balance(user_id)
    price = get_emoji_price()
    packs = get_user_packs(user_id)
    ref_stats = get_referral_stats(user_id)

    text = (
        "💰 <b>Mening Hamyonim</b>\n\n"
        f"💳 <b>Joriy balans:</b> <b>{balance} ⭐ Stars</b>\n"
        f"💎 <b>1 ta emoji narxi:</b> <b>{price} ⭐ Stars</b>\n"
        f"📦 <b>Yaratilgan to'plamlar:</b> <b>{len(packs)} ta</b>\n"
        f"👥 <b>Taklif qilingan do'stlar:</b> <b>{ref_stats['count']} ta</b> (+{ref_stats['total_earned']} ⭐)\n\n"
        "💡 <i>Balansingizni Telegram Stars orqali to'ldirishingiz, promokod kiritishingiz yoki do'stlaringizni taklif qilib bepul Stars ishlashingiz mumkin!</i>"
    )

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Balansni to'ldirish (Stars)", callback_data="topup_menu")
            ],
            [
                InlineKeyboardButton(text="🎁 Promokod kiritish", callback_data="menu_promo"),
                InlineKeyboardButton(text="👥 Do'stlarni taklif qilish", callback_data="menu_referral")
            ],
            [
                InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="menu_main")
            ]
        ]
    )

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
        await event.answer()
    else:
        await event.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)


# ==================== TOPUP MENU & STARS INVOICE ====================

@router.callback_query(F.data == "topup_menu")
async def cb_topup_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    balance = get_user_balance(callback.from_user.id)
    price = get_emoji_price()

    text = (
        "⭐️ <b>Balansni to'ldirish (Telegram Stars)</b>\n\n"
        f"💳 <b>Joriy balansingiz:</b> <b>{balance} ⭐ Stars</b>\n"
        f"💎 <b>1 ta emoji narxi:</b> <b>{price} ⭐ Stars</b>\n\n"
        "Qancha miqdorda to'ldirmoqchisiz? Quyidagi tayyor paketlardan birini tanlang yoki o'zingiz istagan miqdorni kiriting: 👇"
    )

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐️ 10 Stars", callback_data="topup_pkg:10"),
                InlineKeyboardButton(text="⭐️ 25 Stars", callback_data="topup_pkg:25")
            ],
            [
                InlineKeyboardButton(text="⭐️ 50 Stars", callback_data="topup_pkg:50"),
                InlineKeyboardButton(text="⭐️ 100 Stars", callback_data="topup_pkg:100")
            ],
            [
                InlineKeyboardButton(text="⭐️ 250 Stars", callback_data="topup_pkg:250"),
                InlineKeyboardButton(text="⭐️ 500 Stars", callback_data="topup_pkg:500")
            ],
            [
                InlineKeyboardButton(text="✏️ Boshqa miqdor kiritish", callback_data="topup_custom")
            ],
            [
                InlineKeyboardButton(text="🔙 Hamyonga qaytish", callback_data="menu_wallet")
            ]
        ]
    )

    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data.startswith("topup_pkg:"))
async def handle_topup_package(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    amount_str = callback.data.split(":")[1]
    try:
        amount = int(amount_str)
    except ValueError:
        amount = 10

    user_id = callback.from_user.id
    payload = f"topup:{user_id}:{amount}:{int(time.time())}"

    try:
        await bot.send_invoice(
            chat_id=user_id,
            title="⭐️ Balansni to'ldirish",
            description=f"GnEmoji botidagi hisobingizni {amount} Stars ga to'ldirish.",
            payload=payload,
            currency="XTR",
            prices=[LabeledPrice(label=f"{amount} Stars Balans", amount=amount)]
        )
    except Exception as e:
        logger.error(f"Topup invoice send error: {e}", exc_info=True)
        await callback.message.answer(f"❌ To'lov hisobini yaratishda xatolik yuz berdi: {e}")


@router.callback_query(F.data == "topup_custom")
async def handle_topup_custom(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.waiting_for_topup_amount)
    text = (
        "✏️ <b>Ixtiyoriy miqdorni kiriting</b>\n\n"
        "Balansingizga qancha Stars qo'shmoqchisiz? Miqdorni faqat raqam shaklida yozib yuboring (masalan: <code>15</code> yoki <code>150</code>):\n\n"
        "<i>Minimal: 1 ⭐, Maksimal: 100,000 ⭐\nBekor qilish uchun /cancel yozing.</i>"
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="topup_menu")]]
    )
    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()


@router.message(UserStates.waiting_for_topup_amount)
async def handle_custom_amount_input(message: Message, state: FSMContext, bot: Bot):
    raw = message.text.strip()
    if raw.lower() in ("/cancel", "cancel", "bekor"):
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=get_main_menu_markup(message.from_user.id))
        return

    if not raw.isdigit():
        await message.answer("⚠️ Iltimos, faqat butun musbat son kiriting (masalan: <code>20</code>):")
        return

    amount = int(raw)
    if amount < 1 or amount > 100000:
        await message.answer("⚠️ Miqdor 1 va 100,000 Stars oralig'ida bo'lishi kerak.")
        return

    await state.clear()
    user_id = message.from_user.id
    payload = f"topup:{user_id}:{amount}:{int(time.time())}"

    try:
        await bot.send_invoice(
            chat_id=user_id,
            title="⭐️ Balansni to'ldirish",
            description=f"GnEmoji botidagi hisobingizni {amount} Stars ga to'ldirish.",
            payload=payload,
            currency="XTR",
            prices=[LabeledPrice(label=f"{amount} Stars Balans", amount=amount)]
        )
    except Exception as e:
        logger.error(f"Custom invoice send error: {e}", exc_info=True)
        await message.answer(f"❌ To'lov hisobini yaratishda xatolik: {e}")


# ==================== PROMOCODES ====================

@router.callback_query(F.data == "menu_promo")
@router.message(Command("promo"))
@router.message(Command("promokod"))
async def handle_promo_menu(event: Union[Message, CallbackQuery], state: FSMContext):
    # If sent via command with argument e.g. /promo START5
    if isinstance(event, Message):
        parts = event.text.split(maxsplit=1)
        if len(parts) > 1:
            code = parts[1].strip()
            user_id = event.from_user.id
            success, reward, msg = use_promocode(user_id, code)
            if success:
                new_bal = get_user_balance(user_id)
                await event.answer(
                    f"🎉 <b>Tabriklaymiz!</b>\n\n"
                    f"<code>{code.upper()}</code> promokodi muvaffaqiyatli faollashtirildi!\n"
                    f"💰 Balansingizga <b>+{reward} ⭐ Stars</b> qo'shildi.\n"
                    f"💳 Joriy balans: <b>{new_bal} ⭐ Stars</b>",
                    reply_markup=get_main_menu_markup(user_id),
                    parse_mode=ParseMode.HTML
                )
            else:
                await event.answer(f"❌ <b>Xatolik:</b> {msg}", parse_mode=ParseMode.HTML)
            return

    await state.set_state(UserStates.waiting_for_promocode)
    text = (
        "🎁 <b>Promokodni faollashtirish</b>\n\n"
        "Admin yoki kanallarda berilgan promokod matnini yozib yuboring (masalan: <code>START5</code>):\n\n"
        "<i>Bekor qilish uchun /cancel deb yozing.</i>"
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="menu_main")]]
    )

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
        await event.answer()
    else:
        await event.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)


@router.message(UserStates.waiting_for_promocode)
async def handle_promocode_input(message: Message, state: FSMContext):
    raw_code = message.text.strip()
    if raw_code.lower() in ("/cancel", "cancel", "bekor"):
        await state.clear()
        await message.answer("❌ Promokod kiritish bekor qilindi.", reply_markup=get_main_menu_markup(message.from_user.id))
        return

    user_id = message.from_user.id
    success, reward, msg = use_promocode(user_id, raw_code)
    await state.clear()

    if success:
        new_bal = get_user_balance(user_id)
        await message.answer(
            f"🎉 <b>Tabriklaymiz!</b>\n\n"
            f"<code>{raw_code.upper()}</code> promokodi muvaffaqiyatli faollashtirildi!\n"
            f"💰 Balansingizga <b>+{reward} ⭐ Stars</b> qo'shildi.\n"
            f"💳 Joriy balans: <b>{new_bal} ⭐ Stars</b>",
            reply_markup=get_main_menu_markup(user_id),
            parse_mode=ParseMode.HTML
        )
    else:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Qayta urinish", callback_data="menu_promo")],
                [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="menu_main")]
            ]
        )
        await message.answer(f"❌ <b>Xatolik:</b> {msg}", reply_markup=markup, parse_mode=ParseMode.HTML)


# ==================== REFERRAL SYSTEM ====================

@router.callback_query(F.data == "menu_referral")
@router.message(Command("ref"))
@router.message(Command("referral"))
async def handle_referral_menu(event: Union[Message, CallbackQuery]):
    user_id = event.from_user.id
    ref_bonus = get_referral_bonus()
    stats = get_referral_stats(user_id)
    ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"

    share_text = f"✨ Ismingiz bilan eksklyuziv animatsiyali Telegram emoji to'plamini yarating!\n{ref_link}"
    share_url = f"https://t.me/share/url?url={urllib.parse.quote(ref_link)}&text={urllib.parse.quote('✨ Ismingiz bilan eksklyuziv animatsiyali Telegram emoji to`plamini yarating!')}"

    text = (
        "👥 <b>Do'stlarni taklif qilish va Stars ishlash!</b>\n\n"
        f"Har bir siz taklif qilgan va botga qo'shilgan yangi do'stingiz uchun "
        f"sizning balansingizga <b>+{ref_bonus} ⭐ Stars</b> qo'shiladi!\n\n"
        f"🔗 <b>Sizning taklif havolangiz:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        f"📊 <b>Sizning statistikangiz:</b>\n"
        f"• Taklif qilingan do'stlar: <b>{stats['count']} ta</b>\n"
        f"• Ishlangan jami Stars: <b>{stats['total_earned']} ⭐</b>"
    )

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📲 Do'stlarga ulashish", url=share_url)
            ],
            [
                InlineKeyboardButton(text="💰 Hamyonim", callback_data="menu_wallet"),
                InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="menu_main")
            ]
        ]
    )

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
        await event.answer()
    else:
        await event.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)


# ==================== TELEGRAM STARS PAYMENT HANDLERS ====================

@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    """Answers pre-checkout queries within 10 seconds to approve Telegram payment."""
    try:
        await pre_checkout_query.answer(ok=True)
    except Exception as e:
        logger.error(f"Pre-checkout error: {e}")


@router.message(F.successful_payment)
async def process_successful_payment(message: Message, bot: Bot):
    payment = message.successful_payment
    total_amount = payment.total_amount
    payload = payment.invoice_payload
    user_id = message.from_user.id

    logger.info(f"Successful payment received from user {user_id}: {total_amount} Stars, payload={payload}")

    # 1. Top-up deposit handling
    if payload.startswith("topup:") or payload.startswith("topup_stars:"):
        new_balance = add_user_balance(
            user_id=user_id,
            amount=total_amount,
            tx_type="deposit_stars",
            description=f"Telegram Stars orqali hisob to'ldirildi (+{total_amount} ⭐)"
        )
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💰 Hamyonni ko'rish", callback_data="menu_wallet")],
                [InlineKeyboardButton(text="🎨 Yangi emoji yaratish", callback_data="menu_main")]
            ]
        )
        await message.answer(
            f"✅ <b>To'lov muvaffaqiyatli qabul qilindi!</b>\n\n"
            f"💰 Balansingizga <b>+{total_amount} ⭐ Stars</b> qo'shildi!\n"
            f"💳 Joriy balansingiz: <b>{new_balance} ⭐ Stars</b>\n\n"
            "Endi bemalol o'zingiz istagan emoji to'plamini yaratishingiz mumkin! 🎉",
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )
        return

    # 2. Direct Stars purchase for emoji pack
    if payload.startswith("buy_pack:") or payload.startswith("buy_single:"):
        parts = payload.split(":")
        _, p_uid, font_key, clean_text, action_type, extra_param = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]

        # Record payment transaction
        add_user_balance(
            user_id=user_id,
            amount=total_amount,
            tx_type="deposit_stars",
            description=f"Telegram Stars to'lovi: {clean_text}"
        )
        deduct_user_balance(
            user_id=user_id,
            amount=total_amount,
            tx_type="purchase_stars_direct",
            description=f"Stars to'lovi orqali emoji yaratildi: {clean_text}"
        )

        await message.answer(
            f"✅ <b>To'lov qabul qilindi ({total_amount} ⭐)!</b>\n"
            f"🎨 <b>\"{clean_text}\"</b> uchun emoji yaratish boshlanmoqda...",
            parse_mode=ParseMode.HTML
        )

        # Dispatch generation with full pack/destination support
        await execute_generation_by_params(bot, user_id, clean_text, font_key, action_type, extra_param, message.chat.id)


# ==================== EMOJI GENERATION LOGIC & FLOWS ====================

@router.callback_query(F.data == "cmd_mypacks_cb")
@router.message(Command("mypacks"))
async def cb_mypacks(event: Union[Message, CallbackQuery]):
    user_id = event.from_user.id
    packs = get_user_packs(user_id)

    if not packs:
        text = "📁 Sizda hali yaratilgan emoji to'plamlar yo'q. Ismingizni botga yozib yangi paket yarating!"
        if isinstance(event, CallbackQuery):
            await event.message.answer(text)
            await event.answer()
        else:
            await event.answer(text)
        return

    text = "📦 <b>Sizning emoji to'plamlaringiz:</b>\n\n"
    buttons = []
    for pname, ptitle, pdate in packs:
        link = f"https://t.me/addemoji/{pname}"
        text += f"• <a href=\"{link}\">{ptitle}</a>\n"
        buttons.append([InlineKeyboardButton(text=f"➕ {ptitle}", url=link)])

    buttons.append([InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="menu_main")])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    if isinstance(event, CallbackQuery):
        await event.message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        await event.answer()
    else:
        await event.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@router.callback_query(F.data == "cmd_help_cb")
@router.message(Command("help"))
async def cb_help(event: Union[Message, CallbackQuery]):
    price = get_emoji_price()
    ref_bonus = get_referral_bonus()
    help_text = (
        "ℹ️ <b>Yordam & Narxlar</b>\n\n"
        f"💎 <b>1 ta emoji narxi:</b> <b>{price} ⭐ Stars</b>\n"
        f"🎁 <b>Do'st taklif qilish bonusi:</b> <b>+{ref_bonus} ⭐ Stars</b> har bir do'st uchun!\n\n"
        "• <b>Mini App:</b> Yuqoridagi '🚀 Mini Appni Ochish' tugmasini bosing — unda barcha 117 ta shablon jonli ko'rinadi!\n"
        "• Botga istalgan so'z yoki ism yuborib ham yaratishingiz mumkin (1-16 ta belgi).\n"
        "• 3 xil zamonaviy shrift: <b>Stapel</b>, <b>Inter</b> va <b>Grobold</b>.\n"
        "• <b>To'lov usullari:</b> Hamyon balansi orqali yoki to'g'ridan-to'g'ri Telegram Stars orqali.\n"
        "• Mavjud to'plamingizga yangi stikerlarni ham qo'shishingiz mumkin!"
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="menu_main")]]
    )
    if isinstance(event, CallbackQuery):
        await event.message.answer(help_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        await event.answer()
    else:
        await event.answer(help_text, reply_markup=markup, parse_mode=ParseMode.HTML)


@router.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    """Processes any raw data sent from Mini App via Telegram.WebApp.sendData()"""
    try:
        raw_data = message.web_app_data.data
        data = json.loads(raw_data)
        action = data.get("action", "")

        if action == "pack_created":
            pack_name = data.get("pack_name", "")
            pack_link = f"https://t.me/addemoji/{pack_name}"
            markup = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="➕ Telegramga Qo'shish", url=pack_link)]]
            )
            await message.answer(
                f"🎉 <b>Mini App orqali emoji to'plamingiz tayyorlandi!</b>\n\n"
                f"📦 Havola: <a href=\"{pack_link}\">{pack_name}</a>",
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logger.error(f"Web app data parse error: {e}")


# ==================== SVG UPLOAD & TEXT INPUT & FONT SELECTION ====================

@router.message(F.document)
async def handle_document_input(message: Message, bot: Bot):
    doc = message.document
    if not doc:
        return

    file_name = doc.file_name or "vector.svg"
    if not file_name.lower().endswith(".svg"):
        await message.answer("⚠️ Iltimos, faqat <code>.svg</code> kengaytmali vektor fayl yuboring!", parse_mode=ParseMode.HTML)
        return

    user = message.from_user
    add_or_update_user(user_id=user.id, username=user.username, first_name=user.first_name)

    status_msg = await message.answer("⏳ <i>SVG vektor fayli tekshirilmoqda...</i>", parse_mode=ParseMode.HTML)

    try:
        file_info = await bot.get_file(doc.file_id)
        downloaded = await bot.download_file(file_info.file_path)
        raw_bytes = downloaded.read() if hasattr(downloaded, 'read') else downloaded

        clean_svg = validate_and_clean_svg(raw_bytes)
        title = file_name.rsplit(".", 1)[0]
        svg_id = cache_svg(clean_svg, title)

        p = Path(TEMPLATES_DIR)
        tgs_count = len(list(p.glob("*.tgs"))) if p.exists() else 117
        price = get_emoji_price()
        balance = get_user_balance(user.id)

        text = (
            f"🎨 <b>SVG Vektor qabul qilindi!</b>\n\n"
            f"📄 <b>Fayl:</b> <code>{file_name}</code>\n"
            f"💰 <b>1 ta emoji narxi:</b> <b>{price} ⭐ Stars</b> (Balansingiz: <b>{balance} ⭐</b>)\n\n"
            f"Qanday tarzda tayyorlashni xohlaysiz?"
        )

        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"🌟 Barcha {tgs_count} ta shablon (To'liq to'plam)",
                        callback_data=f"choose_dest:svg_all:svg:{svg_id}:all"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🎯 Bitta shablonni tanlash",
                        callback_data=f"svg_pick:{svg_id}:0"
                    )
                ],
                [
                    InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="menu_main")
                ]
            ]
        )

        try:
            await status_msg.delete()
        except:
            pass

        await message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"SVG document handling error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ SVG faylini o'qishda xatolik: {e}")


@router.message(F.text)
async def handle_name_input(message: Message):
    user = message.from_user
    add_or_update_user(user_id=user.id, username=user.username, first_name=user.first_name)

    raw_text = message.text.strip()
    if raw_text.startswith("/"):
        return

    # Check if raw_text is SVG XML code
    if "<svg" in raw_text.lower() and "</svg>" in raw_text.lower():
        try:
            clean_svg = validate_and_clean_svg(raw_text)
            svg_id = cache_svg(clean_svg, "SVG_Vector")
            p = Path(TEMPLATES_DIR)
            tgs_count = len(list(p.glob("*.tgs"))) if p.exists() else 117
            price = get_emoji_price()
            balance = get_user_balance(user.id)

            text = (
                f"🎨 <b>SVG Vektor kodi qabul qilindi!</b>\n\n"
                f"💰 <b>1 ta emoji narxi:</b> <b>{price} ⭐ Stars</b> (Balansingiz: <b>{balance} ⭐</b>)\n\n"
                f"Qanday tarzda tayyorlashni xohlaysiz?"
            )

            markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"🌟 Barcha {tgs_count} ta shablon (To'liq to'plam)",
                            callback_data=f"choose_dest:svg_all:svg:{svg_id}:all"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🎯 Bitta shablonni tanlash",
                            callback_data=f"svg_pick:{svg_id}:0"
                        )
                    ],
                    [
                        InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="menu_main")
                    ]
                ]
            )
            await message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)
            return
        except Exception as e:
            logger.warning(f"Failed to parse raw SVG text: {e}")

    clean_text = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ_ \-]', '', raw_text).strip().upper()
    if not clean_text:
        await message.answer("⚠️ Iltimos, faqat harf va raqamlardan iborat to'g'ri ism yoki so'z kiriting.")
        return

    if len(clean_text) > 16:
        await message.answer("⚠️ Iltimos, 16 ta belgidan oshmagan ism yoki so'z kiriting.")
        return

    price = get_emoji_price()
    balance = get_user_balance(user.id)

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1️⃣ Stapel (Qalin & Geometrik)", callback_data=f"font:stapel:{clean_text}"),
            ],
            [
                InlineKeyboardButton(text="2️⃣ Inter (Klassik & Toza)", callback_data=f"font:inter:{clean_text}")
            ],
            [
                InlineKeyboardButton(text="3️⃣ Grobold (Qalin & Zamonaviy)", callback_data=f"font:grobold:{clean_text}")
            ],
            [
                InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="menu_main")
            ]
        ]
    )

    text_msg = (
        f"✍️ <b>Ismingiz:</b> <code>{clean_text}</code>\n"
        f"💰 <b>Narxi:</b> <b>{price} ⭐ Stars</b> (Balansingiz: <b>{balance} ⭐</b>)\n\n"
        f"Qaysi shriftda emoji yaratmoqchisiz? Shriftni tanlang: 👇\n\n"
        f"<b>1. Stapel: <a href=\"https://t.me/addemoji/asilbek_1704_by_BepulEmojiBot\">Namunani Ko'rish</a></b>\n"
        f"<b>2. Inter: <a href=\"https://t.me/addemoji/asilbek_3103_by_BepulEmojiBot\">Namunani Ko'rish</a></b>\n"
        f"<b>3. Grobold: <a href=\"https://t.me/addemoji/asilbek_4966_by_BepulEmojiBot\">Namunani Ko'rish</a></b>"
    )

    await message.answer(text_msg, reply_markup=markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


# --- FONT TANLANGANDAN SO'NG REJIMNI TANLASH ---
@router.callback_query(F.data.startswith("font:"))
async def handle_font_selected(callback: CallbackQuery):
    _, font_key, clean_text = callback.data.split(":", 2)
    font_info = FONTS_MAP.get(font_key, FONTS_MAP["stapel"])

    p = Path(TEMPLATES_DIR)
    tgs_count = len(list(p.glob("*.tgs"))) if p.exists() else 0
    price = get_emoji_price()
    balance = get_user_balance(callback.from_user.id)

    text = (
        f"🎨 <b>Shrift:</b> {font_info['name']}\n"
        f"✍️ <b>Ism:</b> <code>{clean_text}</code>\n"
        f"💰 <b>Narxi:</b> <b>{price} ⭐ Stars</b> (Balansingiz: <b>{balance} ⭐</b>)\n\n"
        f"Qanday tarzda tayyorlashni xohlaysiz?"
    )

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"🌟 Barcha {tgs_count} ta shablon (To'liq to'plam)",
                    callback_data=f"choose_dest:gen_all:{font_key}:{clean_text}:all"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎯 Bitta shablonni tanlash",
                    callback_data=f"pick_single:{font_key}:{clean_text}"
                )
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu_main")
            ]
        ]
    )

    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()


# --- BITTA SHABLONNI TANLASH MENYUSI (MATN UCHUN) ---
@router.callback_query(F.data.startswith("pick_single:"))
async def handle_pick_single_menu(callback: CallbackQuery):
    parts = callback.data.split(":")
    font_key = parts[1]
    clean_text = parts[2]
    page = int(parts[3]) if len(parts) > 3 else 0

    p = Path(TEMPLATES_DIR)
    tgs_files = sorted(p.glob("*.tgs"), key=lambda f: (int(f.stem) if f.stem.isdigit() else 9999, f.name)) if p.exists() else []

    if not tgs_files:
        await callback.answer("❌ Shablonlar topilmadi.", show_alert=True)
        return

    PER_PAGE = 20
    total_pages = (len(tgs_files) + PER_PAGE - 1) // PER_PAGE
    page = max(0, min(page, total_pages - 1))

    start_idx = page * PER_PAGE
    end_idx = start_idx + PER_PAGE
    current_batch = tgs_files[start_idx:end_idx]

    text = (
        f"🎯 <b>Aynan qaysi shablonni tayyorlamoqchisiz?</b>\n"
        f"Jami: <b>{len(tgs_files)} ta</b> shablon (Sahifa: <b>{page + 1}/{total_pages}</b>)\n\n"
        "Kerakli shablon raqamini bosing: 👇"
    )

    buttons = []
    row = []
    for f in current_batch:
        btn_label = f.stem
        row.append(
            InlineKeyboardButton(
                text=f"#{btn_label}",
                callback_data=f"choose_dest:gen_one:{font_key}:{clean_text}:{f.name}"
            )
        )
        if len(row) == 4:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Oldingi", callback_data=f"pick_single:{font_key}:{clean_text}:{page - 1}"))
    nav_row.append(InlineKeyboardButton(text=f"📄 {page + 1}/{total_pages}", callback_data="ignore"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(text="Keyingi ▶️", callback_data=f"pick_single:{font_key}:{clean_text}:{page + 1}"))

    buttons.append(nav_row)
    buttons.append([
        InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"font:{font_key}:{clean_text}")
    ])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()


# --- BITTA SHABLONNI TANLASH MENYUSI (SVG UCHUN) ---
@router.callback_query(F.data.startswith("svg_pick:"))
async def handle_svg_pick_single_menu(callback: CallbackQuery):
    parts = callback.data.split(":")
    svg_id = parts[1]
    page = int(parts[2]) if len(parts) > 2 else 0

    p = Path(TEMPLATES_DIR)
    tgs_files = sorted(p.glob("*.tgs"), key=lambda f: (int(f.stem) if f.stem.isdigit() else 9999, f.name)) if p.exists() else []

    if not tgs_files:
        await callback.answer("❌ Shablonlar topilmadi.", show_alert=True)
        return

    PER_PAGE = 20
    total_pages = (len(tgs_files) + PER_PAGE - 1) // PER_PAGE
    page = max(0, min(page, total_pages - 1))

    start_idx = page * PER_PAGE
    end_idx = start_idx + PER_PAGE
    current_batch = tgs_files[start_idx:end_idx]

    cached = get_cached_svg(svg_id)
    svg_title = cached.get("title", "SVG") if cached else "SVG"

    text = (
        f"🎯 <b>Aynan qaysi shablonga SVG joylamoqchisiz?</b>\n"
        f"🎨 <b>SVG:</b> <code>{svg_title}</code>\n"
        f"Jami: <b>{len(tgs_files)} ta</b> shablon (Sahifa: <b>{page + 1}/{total_pages}</b>)\n\n"
        "Kerakli shablon raqamini bosing: 👇"
    )

    buttons = []
    row = []
    for f in current_batch:
        btn_label = f.stem
        row.append(
            InlineKeyboardButton(
                text=f"#{btn_label}",
                callback_data=f"choose_dest:svg_one:svg:{svg_id}:{f.name}"
            )
        )
        if len(row) == 4:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Oldingi", callback_data=f"svg_pick:{svg_id}:{page - 1}"))
    nav_row.append(InlineKeyboardButton(text=f"📄 {page + 1}/{total_pages}", callback_data="ignore"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(text="Keyingi ▶️", callback_data=f"svg_pick:{svg_id}:{page + 1}"))

    buttons.append(nav_row)
    buttons.append([
        InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="menu_main")
    ])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data == "ignore")
async def cb_ignore(callback: CallbackQuery):
    await callback.answer()


# ==================== STEP: PACK NI TANLANG (DESTINATION SELECTION) ====================
@router.callback_query(F.data.startswith("choose_dest:"))
async def handle_choose_destination(callback: CallbackQuery):
    # data: choose_dest:{action_type}:{font_key}:{clean_text}:{extra_param}
    parts = callback.data.split(":", 4)
    action_type = parts[1]
    font_key = parts[2]
    clean_text = parts[3]
    extra_param = parts[4]

    user_id = callback.from_user.id
    user_packs = get_user_packs(user_id)

    text = "<b>Pack ni tanlang:</b>"

    buttons = [
        [
            InlineKeyboardButton(
                text="➕ Yangi Emoji pack",
                callback_data=f"req_pay:{action_type}:{font_key}:{clean_text}:{extra_param}|new"
            )
        ]
    ]

    for pname, ptitle, _ in user_packs:
        buttons.append([
            InlineKeyboardButton(
                text=f"📁 {ptitle}",
                callback_data=f"req_pay:{action_type}:{font_key}:{clean_text}:{extra_param}|add_{pname}"
            )
        ])

    back_cb = f"svg_pick:{clean_text}:0" if (font_key == "svg" and action_type == "svg_one") else ("menu_main" if font_key == "svg" else f"font:{font_key}:{clean_text}")
    buttons.append([
        InlineKeyboardButton(
            text="◀️ Orqaga",
            callback_data=back_cb
        )
    ])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()


# ==================== STEP: TO'LOV USULINI TANLANG ====================
@router.callback_query(F.data.startswith("req_pay:"))
async def handle_payment_request(callback: CallbackQuery, bot: Bot):
    # data: req_pay:{action_type}:{font_key}:{clean_text}:{extra_param}
    parts = callback.data.split(":", 4)
    action_type = parts[1]
    font_key = parts[2]
    clean_text = parts[3]
    extra_param = parts[4]

    user_id = callback.from_user.id
    unit_price = get_emoji_price()
    balance = get_user_balance(user_id)

    p = Path(TEMPLATES_DIR)
    tgs_count = len(list(p.glob("*.tgs"))) if p.exists() else 117

    if action_type == "gen_all":
        stickers_count = tgs_count
    elif action_type == "gen_selected":
        raw_t = extra_param.split("|")[0]
        stickers_count = len(raw_t.split(",")) if "," in raw_t else 1
    else:
        stickers_count = 1

    total_cost = stickers_count * unit_price

    text = (
        "<b>To'lov usulini tanlang:</b>\n\n"
        f"📊 <b>Emojilar soni:</b> {stickers_count} ta.\n"
        f"💰 <b>Jami narx:</b> {total_cost} Stars (Balansingiz: {balance} ⭐)"
    )

    raw_base_extra = extra_param.split("|")[0]

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐️ Telegram Stars orqali to'lash",
                    callback_data=f"pay_stars_inv:{action_type}:{font_key}:{clean_text}:{extra_param}:{total_cost}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 Hamyondan to'lash",
                    callback_data=f"pay_wallet:{action_type}:{font_key}:{clean_text}:{extra_param}:{total_cost}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Orqaga",
                    callback_data=f"choose_dest:{action_type}:{font_key}:{clean_text}:{raw_base_extra}"
                )
            ]
        ]
    )

    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()


# --- TO'G'RIDAN-TO'G'RI STARS INVOICE YUBORISH ---
@router.callback_query(F.data.startswith("pay_stars_inv:"))
async def handle_send_direct_stars_invoice(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    parts = callback.data.split(":", 5)
    action_type = parts[1]
    font_key = parts[2]
    clean_text = parts[3]
    extra_param = parts[4]
    total_cost = int(parts[5]) if len(parts) > 5 else get_emoji_price()

    user_id = callback.from_user.id
    stickers_count = total_cost // max(1, get_emoji_price())
    payload = f"buy_pack:{user_id}:{font_key}:{clean_text}:{action_type}:{extra_param}:{total_cost}"

    try:
        await bot.send_invoice(
            chat_id=user_id,
            title="Emoji generatsiya",
            description=f"'{clean_text}' uchun {stickers_count} ta emoji to'lovi.",
            payload=payload,
            currency="XTR",
            prices=[LabeledPrice(label=f"Stars ({stickers_count} ta)", amount=total_cost)]
        )
    except Exception as e:
        logger.error(f"Direct invoice send error: {e}", exc_info=True)
        await callback.message.answer(f"❌ To'lov hisobini yuborishda xatolik: {e}")


# --- BALANSDAN TO'LASH ---
@router.callback_query(F.data.startswith("pay_wallet:"))
async def handle_pay_from_wallet(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split(":", 5)
    action_type = parts[1]
    font_key = parts[2]
    clean_text = parts[3]
    extra_param = parts[4]
    total_cost = int(parts[5]) if len(parts) > 5 else get_emoji_price()

    user_id = callback.from_user.id
    balance = get_user_balance(user_id)

    if balance < total_cost:
        await callback.answer(f"❌ Balansingiz yetarli emas! Sizda {balance} ⭐ bor, kerak: {total_cost} ⭐.", show_alert=True)
        stickers_count = total_cost // max(1, get_emoji_price())
        payload = f"buy_pack:{user_id}:{font_key}:{clean_text}:{action_type}:{extra_param}:{total_cost}"
        try:
            await bot.send_invoice(
                chat_id=user_id,
                title="Emoji generatsiya",
                description=f"'{clean_text}' uchun {stickers_count} ta emoji to'lovi.",
                payload=payload,
                currency="XTR",
                prices=[LabeledPrice(label=f"Stars ({stickers_count} ta)", amount=total_cost)]
            )
        except Exception as e:
            logger.error(f"Direct invoice send error: {e}", exc_info=True)
        return

    deducted = deduct_user_balance(
        user_id=user_id,
        amount=total_cost,
        tx_type="purchase_wallet",
        description=f"Hamyondan to'lov: {clean_text} ({action_type}, {total_cost} ⭐)"
    )

    await callback.answer(f"✅ {total_cost} Stars balansingizdan yechildi.", show_alert=False)
    await execute_generation_by_params(bot, user_id, clean_text, font_key, action_type, extra_param, callback.message.chat.id)


async def execute_generation_by_params(bot: Bot, user_id: int, clean_text: str, font_key: str, action_type: str, extra_param: str, chat_id: int):
    dest_mode = "new"
    pack_target = ""
    raw_target = extra_param

    if "|" in extra_param:
        raw_target, dest_info = extra_param.split("|", 1)
        if dest_info.startswith("add_"):
            dest_mode = "add"
            pack_target = dest_info.replace("add_", "")
        elif dest_info.startswith("add:"):
            dest_mode = "add"
            pack_target = dest_info.replace("add:", "")
        elif dest_info == "new":
            dest_mode = "new"

    is_svg = action_type.startswith("svg_") or font_key == "svg"
    svg_data = None
    badge_color = None
    badge_bg_color = None
    text_color = None
    if is_svg:
        cached = get_cached_svg(clean_text)
        if cached:
            svg_data = cached["svg"]
            badge_color = cached.get("badge_color")
            badge_bg_color = cached.get("badge_bg_color")
            text_color = cached.get("text_color")
            clean_text = cached.get("title", "SVG")
        else:
            svg_data = clean_text if "<svg" in clean_text.lower() else None
            clean_text = "SVG"

    if dest_mode == "add" and pack_target:
        await execute_add_to_pack_generation(bot, user_id, clean_text, font_key, pack_target, raw_target, chat_id, svg_data=svg_data, badge_color=badge_color, badge_bg_color=badge_bg_color, text_color=text_color)
    elif action_type in ("gen_all", "svg_all"):
        await execute_full_pack_generation(bot, user_id, clean_text, font_key, chat_id, svg_data=svg_data, badge_color=badge_color, badge_bg_color=badge_bg_color, text_color=text_color)
    elif action_type in ("gen_one", "svg_one"):
        await execute_single_sticker_generation(bot, user_id, clean_text, font_key, raw_target, chat_id, svg_data=svg_data, badge_color=badge_color, badge_bg_color=badge_bg_color, text_color=text_color)
    elif action_type in ("gen_selected", "svg_selected") or "," in raw_target:
        templates = [t.strip() for t in raw_target.split(",") if t.strip()]
        await execute_selected_templates_generation(bot, user_id, clean_text, font_key, templates, chat_id, svg_data=svg_data, badge_color=badge_color, badge_bg_color=badge_bg_color, text_color=text_color)
    else:
        await execute_full_pack_generation(bot, user_id, clean_text, font_key, chat_id, svg_data=svg_data, badge_color=badge_color, badge_bg_color=badge_bg_color, text_color=text_color)


async def execute_selected_templates_generation(bot: Bot, user_id: int, clean_text: str, font_key: str, template_filenames: List[str], chat_id: int, svg_data: Optional[str] = None, badge_color: Optional[str] = None, badge_bg_color: Optional[str] = None, text_color: Optional[str] = None):
    font_info = FONTS_MAP.get(font_key, FONTS_MAP["stapel"])
    font_file_path = Path(FONTS_DIR) / font_info["file"]
    
    p = Path(TEMPLATES_DIR)
    target_files = []
    for f in template_filenames:
        target = p / f if (p / f).exists() else (p / f"{f}.tgs")
        if target.exists():
            target_files.append(target)

    if not target_files:
        await bot.send_message(chat_id, "❌ Shablonlar topilmadi.")
        return

    item_label = f"🎨 <b>SVG: \"{clean_text}\"</b>" if svg_data else f"🎨 <b>\"{clean_text}\" ({font_info['name']})</b>"
    status_msg = await bot.send_message(
        chat_id,
        f"{item_label} uchun <b>{len(target_files)} ta</b> emoji tayyorlanmoqda...\n⏳ <i>Iltimos, biroz kuting...</i>",
        parse_mode=ParseMode.HTML
    )

    try:
        input_stickers = []
        for idx, tgs_file in enumerate(target_files):
            with open(tgs_file, "rb") as f:
                template_bytes = f.read()

            tpl_num = 0
            try:
                tpl_num = int(''.join(filter(str.isdigit, tgs_file.stem)))
            except Exception:
                pass
            is_logo = tpl_num >= 14 or bool(svg_data)

            processed_bytes = process_tgs_template(
                template_bytes=template_bytes,
                text=clean_text,
                font_path=str(font_file_path),
                svg_data=svg_data,
                input_type="svg" if svg_data else "text",
                badge_color=badge_color if is_logo else None,
                badge_bg_color=badge_bg_color if is_logo else None,
                text_color=text_color if is_logo else None
            )

            emoji_char = DEFAULT_EMOJIS[idx % len(DEFAULT_EMOJIS)]
            input_stickers.append(
                InputSticker(
                    sticker=BufferedInputFile(processed_bytes, filename=f"emoji_{idx+1}.tgs"),
                    emoji_list=[emoji_char],
                    format="animated"
                )
            )

        if svg_data:
            name_slug = to_svg_slug(clean_text)
            pack_title = f"{clean_text} Vector Emojis"
        else:
            name_slug = to_name_slug(clean_text)
            pack_title = f"{clean_text} Emojis"

        pack_name = await create_unique_custom_emoji_set(
            bot_instance=bot,
            user_id=user_id,
            base_slug=name_slug,
            pack_title=pack_title,
            stickers=[input_stickers[0]]
        )
        total_stickers = len(input_stickers)

        for idx in range(1, total_stickers):
            try:
                await bot.add_sticker_to_set(
                    user_id=user_id,
                    name=pack_name,
                    sticker=input_stickers[idx]
                )
            except TelegramRetryAfter as retry_err:
                await asyncio.sleep(retry_err.retry_after + 0.5)
                await bot.add_sticker_to_set(
                    user_id=user_id,
                    name=pack_name,
                    sticker=input_stickers[idx]
                )
            except Exception as e:
                logger.warning(f"Error adding sticker {idx}: {e}")

        save_user_pack(user_id=user_id, pack_name=pack_name, pack_title=pack_title)
        increment_user_packs(user_id)

        pack_link = f"https://t.me/addemoji/{pack_name}"
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="➕ Emoji Packni ochish", url=pack_link)],
                [InlineKeyboardButton(text="◀️ Asosiy menyu", callback_data="menu_main")]
            ]
        )

        type_text = f"🎨 <b>Turi:</b> SVG Vektor" if svg_data else f"✍️ <b>Matn:</b> {clean_text}\n🎨 <b>Shrift:</b> {font_info['name']}"
        await status_msg.edit_text(
            f"🎉 <b>Tabriklaymiz! Emoji to'plamingiz tayyor!</b>\n\n"
            f"{type_text}\n"
            f"📦 <b>To'plam:</b> <a href=\"{pack_link}\">{pack_name}</a>\n"
            f"⚡ <b>Jami emojilar:</b> {total_stickers} ta\n\n"
            f"<i>Pastdagi tugma orqali to'plamni Telegramga qo'shib olishingiz mumkin:</i>",
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        logger.error(f"Selected templates gen error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")


# ==================== GENERATION EXECUTION FUNCTIONS ====================

async def execute_single_sticker_generation(bot: Bot, user_id: int, clean_text: str, font_key: str, tgs_filename: str, chat_id: int, svg_data: Optional[str] = None, badge_color: Optional[str] = None, badge_bg_color: Optional[str] = None, text_color: Optional[str] = None):
    font_info = FONTS_MAP.get(font_key, FONTS_MAP["stapel"])
    font_file_path = Path(FONTS_DIR) / font_info["file"]
    target_tgs = Path(TEMPLATES_DIR) / tgs_filename
    if not target_tgs.exists():
        target_tgs = Path(TEMPLATES_DIR) / f"{tgs_filename}.tgs"
    if not target_tgs.exists():
        target_tgs = next(Path(TEMPLATES_DIR).glob("*.tgs"))

    status_msg = await bot.send_message(chat_id, "⏳ <i>Emoji tayyorlanmoqda...</i>", parse_mode=ParseMode.HTML)

    try:
        tpl_num = 0
        try:
            tpl_num = int(''.join(filter(str.isdigit, target_tgs.stem)))
        except Exception:
            pass
        is_logo = tpl_num >= 14 or bool(svg_data)

        with open(target_tgs, "rb") as f:
            proc_bytes = process_tgs_template(
                template_bytes=f.read(),
                text=clean_text,
                font_path=str(font_file_path),
                svg_data=svg_data,
                input_type="svg" if svg_data else "text",
                badge_color=badge_color if is_logo else None,
                badge_bg_color=badge_bg_color if is_logo else None,
                text_color=text_color if is_logo else None
            )

        rand_suffix = random.randint(1000, 99999)
        if svg_data:
            slug_text = to_svg_slug(clean_text)
            pack_title = f"{clean_text} Vector Emoji"
        else:
            slug_text = to_name_slug(clean_text)
            pack_title = f"{clean_text} ({font_info['name']})"

        sticker_item = InputSticker(
            sticker=BufferedInputFile(proc_bytes, filename="emoji_1.tgs"),
            emoji_list=["⭐"],
            format="animated"
        )

        pack_name = await create_unique_custom_emoji_set(
            bot_instance=bot,
            user_id=user_id,
            base_slug=slug_text,
            pack_title=pack_title,
            stickers=[sticker_item]
        )

        save_user_pack(user_id, pack_name, pack_title)
        pack_link = f"https://t.me/addemoji/{pack_name}"

        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="➕ Telegramga Qo'shish", url=pack_link)],
                [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="menu_main")]
            ]
        )

        type_text = f"🎨 <b>Turi:</b> SVG Vektor" if svg_data else f"✍️ <b>Matn:</b> {clean_text}\n🎨 <b>Shrift:</b> {font_info['name']}"
        await status_msg.edit_text(
            f"🎉 <b>Tabriklaymiz! Emoji yaratildi!</b>\n\n"
            f"{type_text}\n"
            f"📦 <b>To'plam nomi:</b> <a href=\"{pack_link}\">{pack_title}</a>\n"
            f"⚡ <b>Jami emojilar:</b> 1 ta\n\n"
            f"<i>Pastdagi tugma orqali to'plamni Telegramga qo'shib olishingiz mumkin:</i>",
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        logger.error(f"Single sticker gen error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")


async def execute_add_to_pack_generation(bot: Bot, user_id: int, clean_text: str, font_key: str, pack_name: str, tgs_mode: str, chat_id: int, svg_data: Optional[str] = None, badge_color: Optional[str] = None, badge_bg_color: Optional[str] = None, text_color: Optional[str] = None):
    font_info = FONTS_MAP.get(font_key, FONTS_MAP["stapel"])
    font_file_path = Path(FONTS_DIR) / font_info["file"]

    status_msg = await bot.send_message(chat_id, "⏳ <i>Emojilar paketga qo'shilmoqda...</i>", parse_mode=ParseMode.HTML)

    try:
        p = Path(TEMPLATES_DIR)
        if tgs_mode == 'all':
            tgs_files = sorted(p.glob("*.tgs"), key=lambda f: (int(f.stem) if f.stem.isdigit() else 9999, f.name))
        else:
            target = p / tgs_mode if (p / tgs_mode).exists() else (p / f"{tgs_mode}.tgs")
            tgs_files = [target] if target.exists() else [next(p.glob("*.tgs"))]

        added_count = 0
        for idx, tfile in enumerate(tgs_files):
            tpl_num = 0
            try:
                tpl_num = int(''.join(filter(str.isdigit, tfile.stem)))
            except Exception:
                pass
            is_logo = tpl_num >= 14 or bool(svg_data)

            with open(tfile, "rb") as f:
                proc_bytes = process_tgs_template(
                    template_bytes=f.read(),
                    text=clean_text,
                    font_path=str(font_file_path),
                    svg_data=svg_data,
                    input_type="svg" if svg_data else "text",
                    badge_color=badge_color if is_logo else None,
                    badge_bg_color=badge_bg_color if is_logo else None,
                    text_color=text_color if is_logo else None
                )

            emoji_char = DEFAULT_EMOJIS[idx % len(DEFAULT_EMOJIS)]
            sticker_item = InputSticker(
                sticker=BufferedInputFile(proc_bytes, filename=f"emoji_{idx+1}.tgs"),
                emoji_list=[emoji_char],
                format="animated"
            )

            await bot.add_sticker_to_set(
                user_id=user_id,
                name=pack_name,
                sticker=sticker_item
            )
            added_count += 1
            await asyncio.sleep(0.3)

        pack_link = f"https://t.me/addemoji/{pack_name}"
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="➕ Emoji Packni ochish", url=pack_link)],
                [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="menu_main")]
            ]
        )

        await status_msg.edit_text(
            f"✅ <b>Muvaffaqiyatli qo'shildi!</b>\n\n"
            f"📦 <b>To'plam:</b> <a href=\"{pack_link}\">{pack_name}</a>\n"
            f"➕ <b>Qo'shilgan emojilar soni:</b> {added_count} ta",
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        logger.error(f"Add to set error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Qo'shishda xatolik: {e}\n<i>Eslatma: Faqat o'zingiz yaratgan paketlarga stiker qo'sha olasiz.</i>", parse_mode=ParseMode.HTML)


async def execute_full_pack_generation(bot: Bot, user_id: int, clean_text: str, font_key: str, chat_id: int, svg_data: Optional[str] = None, badge_color: Optional[str] = None, badge_bg_color: Optional[str] = None, text_color: Optional[str] = None):
    if user_id in ACTIVE_USERS:
        await bot.send_message(chat_id, "⚠️ Sizda hozirda emoji paket tayyorlanmoqda. Iltimos, kuting!")
        return

    ACTIVE_USERS.add(user_id)
    font_info = FONTS_MAP.get(font_key, FONTS_MAP["stapel"])
    font_file_path = Path(FONTS_DIR) / font_info["file"]

    item_label = f"🎨 <b>SVG: \"{clean_text}\"</b>" if svg_data else f"🎨 <b>\"{clean_text}\" ({font_info['name']})</b>"
    status_msg = await bot.send_message(
        chat_id,
        f"{item_label} uchun barcha shablonlar tayyorlanmoqda...\n"
        f"⏳ <i>Iltimos, biroz kuting...</i>",
        parse_mode=ParseMode.HTML
    )

    try:
        p = Path(TEMPLATES_DIR)
        tgs_files = sorted(p.glob("*.tgs"), key=lambda f: (int(f.stem) if f.stem.isdigit() else 9999, f.name))

        if not tgs_files:
            await status_msg.edit_text("❌ <code>shablonlar</code> papkasida .tgs shablonlar topilmadi!", parse_mode=ParseMode.HTML)
            ACTIVE_USERS.discard(user_id)
            return

        input_stickers = []
        for idx, tgs_file in enumerate(tgs_files):
            tpl_num = 0
            try:
                tpl_num = int(''.join(filter(str.isdigit, tgs_file.stem)))
            except Exception:
                pass
            is_logo = tpl_num >= 14 or bool(svg_data)

            with open(tgs_file, "rb") as f:
                template_bytes = f.read()

            processed_bytes = process_tgs_template(
                template_bytes=template_bytes,
                text=clean_text,
                font_path=str(font_file_path),
                svg_data=svg_data,
                input_type="svg" if svg_data else "text",
                badge_color=badge_color if is_logo else None,
                badge_bg_color=badge_bg_color if is_logo else None,
                text_color=text_color if is_logo else None
            )

            emoji_char = DEFAULT_EMOJIS[idx % len(DEFAULT_EMOJIS)]
            input_stickers.append(
                InputSticker(
                    sticker=BufferedInputFile(processed_bytes, filename=f"emoji_{idx+1}.tgs"),
                    emoji_list=[emoji_char],
                    format="animated"
                )
            )

        if svg_data:
            name_slug = to_svg_slug(clean_text)
            pack_title = f"{clean_text} Vector Emojis"
        else:
            name_slug = to_name_slug(clean_text)
            pack_title = f"{clean_text} Emojis"

        try:
            pack_name = await create_unique_custom_emoji_set(
                bot_instance=bot,
                user_id=user_id,
                base_slug=name_slug,
                pack_title=pack_title,
                stickers=[input_stickers[0]]
            )
            emoji_pack_created = True

            if emoji_pack_created and total_stickers > 1:
                for idx in range(1, total_stickers):
                    try:
                        await bot.add_sticker_to_set(
                            user_id=user_id,
                            name=pack_name,
                            sticker=input_stickers[idx]
                        )
                    except TelegramRetryAfter as retry_err:
                        await asyncio.sleep(retry_err.retry_after + 0.5)
                        await bot.add_sticker_to_set(
                            user_id=user_id,
                            name=pack_name,
                            sticker=input_stickers[idx]
                        )
                    except Exception as add_err:
                        logger.warning(f"Sticker {idx+1} qo'shishda xatolik: {add_err}")

                    if idx % 15 == 0 or idx == total_stickers - 1:
                        percent = int(((idx + 1) / total_stickers) * 100)
                        try:
                            await status_msg.edit_text(
                                f"{item_label}\n\n"
                                f"⏳ Emoji to'plam yaratilmoqda: <b>{idx+1}/{total_stickers}</b> ({percent}%)\n"
                                f"<i>Iltimos, biroz kuting...</i>",
                                parse_mode=ParseMode.HTML
                            )
                        except:
                            pass
                    await asyncio.sleep(0.04)

        except TelegramRetryAfter as e:
            logger.warning(f"FloodWait cheklovi: {e.retry_after}s")
            mins = e.retry_after // 60
            secs = e.retry_after % 60
            time_str = f"{mins} daqiqa {secs} soniya" if mins > 0 else f"{secs} soniya"

            await status_msg.edit_text(
                f"⏳ <b>Telegram serveri yangi to'plam yaratishga vaqtinchalik limit qo'ydi (FloodWait: {time_str}).</b>\n\n"
                f"Iltimos, birozdan so'ng qayta urinib ko'ring yoki '🎯 Bitta shablonni tanlash' orqali alohida stikerni darhol tayyorlang.",
                parse_mode=ParseMode.HTML
            )
            ACTIVE_USERS.discard(user_id)
            return

        except Exception as e:
            logger.error(f"Paket yaratishda xato: {e}")
            await status_msg.edit_text(f"❌ Paketni yaratib bo'lmadi: {e}")
            ACTIVE_USERS.discard(user_id)
            return

        if emoji_pack_created:
            save_user_pack(user_id, pack_name, pack_title)
            increment_user_packs(user_id)

            pack_link = f"https://t.me/addemoji/{pack_name}"
            markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Emoji Packni qo'shish", url=pack_link)],
                    [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu_main")]
                ]
            )
            try:
                await status_msg.delete()
            except:
                pass

            type_text = f"🎨 <b>Turi:</b> SVG Vektor" if svg_data else f"🔤 <b>Matn:</b> <code>{clean_text}</code>\n🎨 <b>Shrift:</b> <b>{font_info['name']}</b>"
            await bot.send_message(
                chat_id=chat_id,
                text=(
                    f"✅ <b>Sizning shaxsiy emoji paketingiz tayyor bo'ldi!</b>\n\n"
                    f"{type_text}\n"
                    f"📦 <b>Animatsiyalar soni:</b> {len(input_stickers)} ta\n"
                    f"🔗 <b>Havola:</b> <a href=\"{pack_link}\">{pack_link}</a>\n\n"
                    f"👇 Quyidagi tugma orqali to'plamni Telegramingizga qo'shib oling:"
                ),
                reply_markup=markup,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False
            )
        else:
            await status_msg.edit_text("❌ Kechirasiz, emoji paketini yaratish jarayonida xatolik yuz berdi.")

    except Exception as e:
        logger.error(f"Global handler error: {e}", exc_info=True)
        await bot.send_message(chat_id, "❌ Kutilmagan texnik xatolik yuz berdi.")
    finally:
        ACTIVE_USERS.discard(user_id)
