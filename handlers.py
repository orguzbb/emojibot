import time
import re
import json
import random
import logging
import asyncio
import urllib.parse
from pathlib import Path
from typing import Optional

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
from lottie_processor import process_tgs_template, process_all_templates
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
        if ref_arg.startswith("ref_") or ref_arg.startswith("ref"):
            try:
                clean_ref = ref_arg.replace("ref_", "").replace("ref", "")
                ref_id = int(clean_ref)
            except ValueError:
                ref_id = None

    is_new, awarded_ref = add_or_update_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        referred_by=ref_id
    )

    if is_new and awarded_ref:
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
async def handle_wallet_menu(event: Message | CallbackQuery, state: FSMContext):
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
async def handle_promo_menu(event: Message | CallbackQuery, state: FSMContext):
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
async def handle_referral_menu(event: Message | CallbackQuery):
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
    if payload.startswith("topup:"):
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
async def cb_mypacks(event: Message | CallbackQuery):
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
async def cb_help(event: Message | CallbackQuery):
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


# ==================== TEXT INPUT & FONT SELECTION ====================

@router.message(F.text)
async def handle_name_input(message: Message):
    user = message.from_user
    add_or_update_user(user_id=user.id, username=user.username, first_name=user.first_name)

    raw_text = message.text.strip()
    if raw_text.startswith("/"):
        return

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


# --- BITTA SHABLONNI TANLASH MENYUSI (PAGINATSIYA BILAN) ---
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

    buttons.append([
        InlineKeyboardButton(
            text="◀️ Orqaga",
            callback_data=f"font:{font_key}:{clean_text}"
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
        f"📊 <b>Stikerlar soni:</b> {stickers_count} ta.\n"
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
            title="Stiker generatsiya",
            description=f"'{clean_text}' uchun {stickers_count} ta stiker to'lovi.",
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
                title="Stiker generatsiya",
                description=f"'{clean_text}' uchun {stickers_count} ta stiker to'lovi.",
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

    if dest_mode == "add" and pack_target:
        await execute_add_to_pack_generation(bot, user_id, clean_text, font_key, pack_target, raw_target, chat_id)
    elif action_type == "gen_all":
        await execute_full_pack_generation(bot, user_id, clean_text, font_key, chat_id)
    elif action_type == "gen_one":
        await execute_single_sticker_generation(bot, user_id, clean_text, font_key, raw_target, chat_id)
    elif action_type == "gen_selected" or "," in raw_target:
        templates = [t.strip() for t in raw_target.split(",") if t.strip()]
        await execute_selected_templates_generation(bot, user_id, clean_text, font_key, templates, chat_id)
    else:
        await execute_full_pack_generation(bot, user_id, clean_text, font_key, chat_id)


async def execute_selected_templates_generation(bot: Bot, user_id: int, clean_text: str, font_key: str, template_filenames: List[str], chat_id: int):
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

    status_msg = await bot.send_message(
        chat_id,
        f"🎨 <b>\"{clean_text}\"</b> uchun <b>{len(target_files)} ta</b> emoji tayyorlanmoqda...\n⏳ <i>Iltimos, biroz kuting...</i>",
        parse_mode=ParseMode.HTML
    )

    try:
        input_stickers = []
        for idx, tgs_file in enumerate(target_files):
            with open(tgs_file, "rb") as f:
                template_bytes = f.read()

            processed_bytes = process_tgs_template(
                template_bytes=template_bytes,
                text=clean_text,
                font_path=str(font_file_path)
            )

            emoji_char = DEFAULT_EMOJIS[idx % len(DEFAULT_EMOJIS)]
            input_stickers.append(
                InputSticker(
                    sticker=BufferedInputFile(processed_bytes, filename=f"emoji_{idx+1}.tgs"),
                    emoji_list=[emoji_char],
                    format="animated"
                )
            )

        name_slug = to_name_slug(clean_text)
        short_code = random.randint(100, 9999)
        pack_name = f"{name_slug}_{short_code}_by_{BOT_USERNAME}"
        pack_title = f"{clean_text} Emojis"
        total_stickers = len(input_stickers)

        await bot.create_new_sticker_set(
            user_id=user_id,
            name=pack_name,
            title=pack_title,
            stickers=[input_stickers[0]],
            sticker_type="custom_emoji"
        )

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

        await status_msg.edit_text(
            f"🎉 <b>Tabriklaymiz! Emoji to'plamingiz tayyor!</b>\n\n"
            f"✍️ <b>Matn:</b> {clean_text}\n"
            f"🎨 <b>Shrift:</b> {font_info['name']}\n"
            f"📦 <b>To'plam:</b> <a href=\"{pack_link}\">{pack_name}</a>\n"
            f"⚡ <b>Jami stikerlar:</b> {total_stickers} ta\n\n"
            f"<i>Pastdagi tugma orqali to'plamni Telegramga qo'shib olishingiz mumkin:</i>",
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        logger.error(f"Selected templates gen error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")


# ==================== GENERATION EXECUTION FUNCTIONS ====================

async def execute_single_sticker_generation(bot: Bot, user_id: int, clean_text: str, font_key: str, tgs_filename: str, chat_id: int):
    font_info = FONTS_MAP.get(font_key, FONTS_MAP["stapel"])
    font_file_path = Path(FONTS_DIR) / font_info["file"]
    target_tgs = Path(TEMPLATES_DIR) / tgs_filename

    if not target_tgs.exists():
        await bot.send_message(chat_id, f"❌ Shablon {tgs_filename} topilmadi.")
        return

    status_msg = await bot.send_message(
        chat_id,
        f"🎨 <b>\"{clean_text}\"</b> uchun <b>{tgs_filename}</b> shabloni tayyorlanmoqda...\n⏳ <i>Iltimos, biroz kuting...</i>",
        parse_mode=ParseMode.HTML
    )

    try:
        with open(target_tgs, "rb") as f:
            raw_bytes = f.read()

        proc_bytes = process_tgs_template(raw_bytes, clean_text, str(font_file_path))
        input_file = BufferedInputFile(proc_bytes, filename=f"{clean_text}_{tgs_filename}")

        await bot.send_document(
            chat_id=chat_id,
            document=input_file,
            caption=f"✨ <b>{clean_text}</b> — Shablon <code>{tgs_filename}</code> ({font_info['name']})",
            parse_mode=ParseMode.HTML
        )

        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="➕ Mavjud paketga qo'shish",
                        callback_data=f"add_single_pack:{font_key}:{clean_text}:{tgs_filename}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🎯 Boshqa shablon tanlash",
                        callback_data=f"pick_single:{font_key}:{clean_text}"
                    )
                ],
                [
                    InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="menu_main")
                ]
            ]
        )
        await status_msg.edit_text("✅ <b>Tayyor!</b> Animatsiya yuqorida yuborildi.", reply_markup=markup, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Single sticker gen error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")


async def execute_add_to_pack_generation(bot: Bot, user_id: int, clean_text: str, font_key: str, pack_name: str, tgs_mode: str, chat_id: int):
    font_info = FONTS_MAP.get(font_key, FONTS_MAP["stapel"])
    font_file_path = Path(FONTS_DIR) / font_info["file"]

    status_msg = await bot.send_message(chat_id, "⏳ <i>Stikerlar paketga qo'shilmoqda...</i>", parse_mode=ParseMode.HTML)

    try:
        p = Path(TEMPLATES_DIR)
        if tgs_mode == 'all':
            tgs_files = sorted(p.glob("*.tgs"), key=lambda f: (len(f.name), f.name))
        else:
            tgs_files = [p / tgs_mode]

        added_count = 0
        for idx, tfile in enumerate(tgs_files):
            with open(tfile, "rb") as f:
                proc_bytes = process_tgs_template(f.read(), clean_text, str(font_file_path))

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
            f"➕ <b>Qo'shilgan stikerlar soni:</b> {added_count} ta",
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        logger.error(f"Add to set error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Qo'shishda xatolik: {e}\n<i>Eslatma: Faqat o'zingiz yaratgan paketlarga stiker qo'sha olasiz.</i>", parse_mode=ParseMode.HTML)


async def execute_full_pack_generation(bot: Bot, user_id: int, clean_text: str, font_key: str, chat_id: int):
    if user_id in ACTIVE_USERS:
        await bot.send_message(chat_id, "⚠️ Sizda hozirda emoji paket tayyorlanmoqda. Iltimos, kuting!")
        return

    ACTIVE_USERS.add(user_id)
    font_info = FONTS_MAP.get(font_key, FONTS_MAP["stapel"])
    font_file_path = Path(FONTS_DIR) / font_info["file"]

    status_msg = await bot.send_message(
        chat_id,
        f"🎨 <b>\"{clean_text}\"</b> uchun <b>{font_info['name']}</b> shriftida barcha shablonlar tayyorlanmoqda...\n"
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
            with open(tgs_file, "rb") as f:
                template_bytes = f.read()

            processed_bytes = process_tgs_template(
                template_bytes=template_bytes,
                text=clean_text,
                font_path=str(font_file_path)
            )

            emoji_char = DEFAULT_EMOJIS[idx % len(DEFAULT_EMOJIS)]
            input_stickers.append(
                InputSticker(
                    sticker=BufferedInputFile(processed_bytes, filename=f"emoji_{idx+1}.tgs"),
                    emoji_list=[emoji_char],
                    format="animated"
                )
            )

        name_slug = to_name_slug(clean_text)
        short_code = random.randint(100, 9999)
        pack_name = f"{name_slug}_{short_code}_by_{BOT_USERNAME}"
        pack_title = f"{clean_text} Emojis"
        total_stickers = len(input_stickers)
        emoji_pack_created = False

        try:
            logger.info(f"Paket yaratilmoqda (Dastlabki stiker bilan): {pack_name}")
            created = await bot.create_new_sticker_set(
                user_id=user_id,
                name=pack_name,
                title=pack_title,
                stickers=[input_stickers[0]],
                sticker_type="custom_emoji"
            )
            emoji_pack_created = created

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
                                f"🎨 <b>\"{clean_text}\" ({font_info['name']})</b>\n\n"
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

            await bot.send_message(
                chat_id=chat_id,
                text=(
                    f"✅ <b>Sizning shaxsiy emoji paketingiz tayyor bo'ldi!</b>\n\n"
                    f"🔤 <b>Matn:</b> <code>{clean_text}</code>\n"
                    f"🎨 <b>Shrift:</b> <b>{font_info['name']}</b>\n"
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
