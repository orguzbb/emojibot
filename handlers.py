import time
import re
import json
import random
import logging
import asyncio
from pathlib import Path
from aiogram import Bot, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
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
    get_user_packs
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
    waiting_for_pack_name = State()


def to_name_slug(text: str) -> str:
    res = []
    for ch in text.upper():
        res.append(CYRILLIC_TO_LATIN.get(ch, ch))
    slug = "".join(res)
    slug = re.sub(r'[^a-zA-Z0-9]', '', slug).lower()
    if not slug or not slug[0].isalpha():
        slug = f"e{slug}"
    return slug[:18]


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    add_or_update_user(user_id=user.id, username=user.username, first_name=user.first_name)

    welcome_text = (
        "👋 <b>Assalomu alaykum!</b>\n\n"
        "✨ Ushbu bot orqali siz o'zingizning ismingiz bilan "
        "<b>Telegram Premium Animatsiyali Emoji Pack</b> yaratishingiz mumkin!\n\n"
        "🚀 <b>Mini App orqali foydalanish:</b>\n"
        "Pastdagi <b>📱 Mini App</b> tugmasini bosing va jonli prevyuni ko'rgan holda "
        "100x100 ticket emojilar yoki to'liq to'plamni 1 bosishda yarating!\n\n"
        "🔤 <b>Bot orqali oddiy usul:</b>\n"
        "1. Ismingizni botga yozing (masalan: <code>ASILBEK</code>).\n"
        "2. Shriftni tanlang (Stapel, Inter yoki Grobold).\n"
        "3. Shablonni tanlab yarating!"
    )

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Mini Appni Ochish (Jonli Prevyu)",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                InlineKeyboardButton(
                    text="📦 Mening To'plamlarim",
                    callback_data="cmd_mypacks_cb"
                ),
                InlineKeyboardButton(
                    text="ℹ️ Yordam",
                    callback_data="cmd_help_cb"
                )
            ]
        ]
    )
    await message.answer(welcome_text, reply_markup=markup, parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "cmd_mypacks_cb")
async def cb_mypacks(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    packs = get_user_packs(user_id)
    if not packs:
        await callback.message.answer("📁 Sizda hali yaratilgan emoji to'plamlar yo'q. Mini App yoki bot orqali yangi paket yarating!")
        return

    text = "📦 <b>Sizning emoji to'plamlaringiz:</b>\n\n"
    buttons = []
    for pname, ptitle, pdate in packs:
        link = f"https://t.me/addemoji/{pname}"
        text += f"• <a href=\"{link}\">{ptitle}</a>\n"
        buttons.append([InlineKeyboardButton(text=f"➕ {ptitle}", url=link)])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@router.callback_query(F.data == "cmd_help_cb")
async def cb_help(callback: CallbackQuery):
    await callback.answer()
    help_text = (
        "ℹ️ <b>Yordam bo'limi</b>\n\n"
        "• <b>Mini App:</b> Yuqoridagi '🚀 Mini Appni Ochish' tugmasini bosing — unda barcha 117 ta shablon jonli ko'rinadi!\n"
        "• Botga istalgan so'z yoki ism yuborib ham yaratishingiz mumkin (1-16 ta belgi).\n"
        "• 3 xil zamonaviy shrift: Stapel, Inter va Grobold.\n"
        "• Yangi stikerni o'zingizning mavjud to'plamingizga ham qo'sha olasiz!"
    )
    await callback.message.answer(help_text, parse_mode=ParseMode.HTML)


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


@router.message(Command("help"))
async def cmd_help(message: Message):
    user = message.from_user
    add_or_update_user(user_id=user.id, username=user.username, first_name=user.first_name)

    help_text = (
        "ℹ️ <b>Yordam bo'limi</b>\n\n"
        "• Botga istalgan so'z yoki ism yuboring (1-16 ta belgi).\n"
        "• 3 xil zamonaviy shrift (Stapel, Inter va Grobold) dan birini tanlang.\n"
        "• <b>To'liq to'plam</b> yaratishingiz yoki <b>Bitta shablonni (masalan 14)</b> tanlashingiz mumkin.\n"
        "• Shuningdek, yangi stikerni o'zingizning <b>mavjud to'plamingizga</b> ham qo'sha olasiz!\n\n"
        "<i>Ismingizni yuborib ko'ring!</i>"
    )
    await message.answer(help_text, parse_mode=ParseMode.HTML)


@router.message(Command("mypacks"))
async def cmd_mypacks(message: Message):
    user_id = message.from_user.id
    packs = get_user_packs(user_id)
    if not packs:
        await message.answer("📁 Sizda hali yaratilgan emoji to'plamlar yo'q. Ismingizni yozib yangi paket yarating!")
        return

    text = "📦 <b>Sizning emoji to'plamlaringiz:</b>\n\n"
    buttons = []
    for pname, ptitle, pdate in packs:
        link = f"https://t.me/addemoji/{pname}"
        text += f"• <a href=\"{link}\">{ptitle}</a>\n"
        buttons.append([InlineKeyboardButton(text=f"➕ {ptitle}", url=link)])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


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
            ]
        ]
    )

    text_msg = (
        f"✍️ <b>Ismingiz:</b> <code>{clean_text}</code>\n\n"
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

    text = (
        f"🎨 <b>Shrift:</b> {font_info['name']}\n"
        f"✍️ <b>Ism:</b> <code>{clean_text}</code>\n\n"
        f"Qanday tarzda tayyorlashni xohlaysiz?"
    )

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"🌟 Barcha {tgs_count} ta shablon (To'liq to'plam)",
                    callback_data=f"gen_all:{font_key}:{clean_text}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎯 Bitta shablonni tanlash",
                    callback_data=f"pick_single:{font_key}:{clean_text}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Mavjud to'plamga qo'shish",
                    callback_data=f"add_pack_menu:{font_key}:{clean_text}"
                )
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
                callback_data=f"gen_one:{font_key}:{clean_text}:{f.name}"
            )
        )
        if len(row) == 4:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # Navigatsiya tugmalari
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


# --- BITTA SHABLONNI GENERATSIYA QILISH ---
@router.callback_query(F.data.startswith("gen_one:"))
async def handle_generate_single_sticker(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split(":", 3)
    font_key = parts[1]
    clean_text = parts[2]
    tgs_filename = parts[3]

    font_info = FONTS_MAP.get(font_key, FONTS_MAP["stapel"])
    font_file_path = Path(FONTS_DIR) / font_info["file"]
    target_tgs = Path(TEMPLATES_DIR) / tgs_filename

    if not target_tgs.exists():
        await callback.answer(f"❌ Shablon {tgs_filename} topilmadi.", show_alert=True)
        return

    await callback.answer()
    status_msg = await callback.message.answer(
        f"🎨 <b>\"{clean_text}\"</b> uchun <b>{tgs_filename}</b> shabloni tayyorlanmoqda...\n"
        f"⏳ <i>Iltimos, biroz kuting...</i>",
        parse_mode=ParseMode.HTML
    )

    try:
        with open(target_tgs, "rb") as f:
            raw_bytes = f.read()

        proc_bytes = process_tgs_template(raw_bytes, clean_text, str(font_file_path))

        # 1. Foydalanuvchiga to'g'ridan-to'g'ri animatsiyani yuboramiz
        input_file = BufferedInputFile(proc_bytes, filename=f"{clean_text}_{tgs_filename}")
        try:
            await callback.message.answer_document(
                input_file,
                caption=f"✨ <b>{clean_text}</b> — Shablon <code>{tgs_filename}</code> ({font_info['name']})",
                parse_mode=ParseMode.HTML
            )
        except TelegramRetryAfter as e:
            logger.warning(f"SendDocument FloodWait: {e.retry_after}s")
            await status_msg.edit_text(
                f"⏳ <b>Telegram serveri fayl yuborishga vaqtinchalik tanaffus qo'ydi ({e.retry_after} soniya).</b>\n\n"
                f"Iltimos, {e.retry_after} soniyadan so'ng qayta bosing.",
                parse_mode=ParseMode.HTML
            )
            return

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
                ]
            ]
        )

        await status_msg.edit_text("✅ <b>Tayyor!</b> Animatsiya yuqorida yuborildi.", reply_markup=markup, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Single sticker gen error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")


# --- MAVJUD TO'PLAMGA QO'SHISH MENYUSI ---
@router.callback_query(F.data.startswith("add_pack_menu:"))
@router.callback_query(F.data.startswith("add_single_pack:"))
async def handle_add_pack_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    
    if callback.data.startswith("add_single_pack:"):
        # add_single_pack:{font_key}:{clean_text}:{tgs_filename}
        font_key = parts[1]
        clean_text = parts[2]
        single_tgs = parts[3]
    else:
        # add_pack_menu:{font_key}:{clean_text}
        font_key = parts[1]
        clean_text = parts[2]
        single_tgs = "all"

    user_packs = get_user_packs(user_id)

    text = (
        f"➕ <b>Qaysi to'plamingizga qo'shmoqchisiz?</b>\n\n"
        "O'zingiz yaratgan mavjud paketlardan birini tanlang:"
    )

    buttons = []
    for pname, ptitle, _ in user_packs:
        buttons.append([
            InlineKeyboardButton(
                text=f"📦 {ptitle}",
                callback_data=f"do_add:{pname}:{font_key}:{clean_text}:{single_tgs}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data=f"font:{font_key}:{clean_text}"
        )
    ])

    if not user_packs:
        text = (
            "📁 <b>Sizda hali yaratilgan paketlar yo'q.</b>\n\n"
            "Avval yangi to'plam yaratishingiz kerak. Orqaga qaytib 'Barcha shablonlar' tugmasini bosing."
        )

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()


# --- MAVJUD TO'PLAMGA QO'SHISH AMALGA OSHIRISH ---
@router.callback_query(F.data.startswith("do_add:"))
async def handle_execute_add_to_pack(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    # do_add:{pname}:{font_key}:{clean_text}:{tgs_mode}
    _, pack_name, font_key, clean_text, tgs_mode = callback.data.split(":", 4)

    font_info = FONTS_MAP.get(font_key, FONTS_MAP["stapel"])
    font_file_path = Path(FONTS_DIR) / font_info["file"]

    await callback.answer()
    status_msg = await callback.message.answer("⏳ <i>Stikerlar paketga qo'shilmoqda...</i>", parse_mode=ParseMode.HTML)

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
            inline_keyboard=[[InlineKeyboardButton(text="➕ Emoji Packni ochish", url=pack_link)]]
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


# --- BARCHA SHABLONLARDAN YANGI PAKET YARATISH ---
@router.callback_query(F.data.startswith("gen_all:"))
async def handle_generate_all_emojis(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id

    if user_id in ACTIVE_USERS:
        await callback.answer("⚠️ Sizda hozirda emoji paket tayyorlanmoqda. Iltimos, kuting!", show_alert=True)
        return

    ACTIVE_USERS.add(user_id)
    await callback.answer()

    try:
        _, font_key, clean_text = callback.data.split(":", 2)
        font_info = FONTS_MAP.get(font_key, FONTS_MAP["stapel"])
        font_file_path = Path(FONTS_DIR) / font_info["file"]
    except Exception as e:
        logger.error(f"Callback data parse error: {e}")
        ACTIVE_USERS.discard(user_id)
        return

    status_msg = await callback.message.answer(
        f"🎨 <b>\"{clean_text}\"</b> uchun <b>{font_info['name']}</b> shriftida barcha shablonlar tayyorlanmoqda...\n"
        f"⏳ <i>Iltimos, biroz kuting...</i>",
        parse_mode=ParseMode.HTML
    )

    try:
        p = Path(TEMPLATES_DIR)
        tgs_files = sorted(p.glob("*.tgs"), key=lambda f: (len(f.name), f.name))

        if not tgs_files:
            await status_msg.edit_text("❌ <code>shablonlar</code> papkasida .tgs shablonlar topilmadi!", parse_mode=ParseMode.HTML)
            ACTIVE_USERS.discard(user_id)
            return

        input_stickers = []
        generated_raw_files = []
        for idx, tgs_file in enumerate(tgs_files):
            with open(tgs_file, "rb") as f:
                template_bytes = f.read()

            processed_bytes = process_tgs_template(
                template_bytes=template_bytes,
                text=clean_text,
                font_path=str(font_file_path)
            )

            generated_raw_files.append((tgs_file.name, processed_bytes))
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
            # 1. Dastlabki 1 ta stiker bilan to'plamni yaratamiz (Request Entity Too Large muammosini oldini oladi)
            created = await bot.create_new_sticker_set(
                user_id=user_id,
                name=pack_name,
                title=pack_title,
                stickers=[input_stickers[0]],
                sticker_type="custom_emoji"
            )
            emoji_pack_created = created

            # 2. Qolgan barcha stikerlarni xavfsiz ketma-ket qo'shib chiqamiz
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

                    # Har 15 ta stikerda progressni yangilash
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
                    [InlineKeyboardButton(text="➕ Emoji Packni qo'shish", url=pack_link)]
                ]
            )
            await status_msg.delete()
            await callback.message.answer(
                f"✅ <b>Sizning shaxsiy emoji paketingiz tayyor bo'ldi!</b>\n\n"
                f"🔤 <b>Matn:</b> <code>{clean_text}</code>\n"
                f"🎨 <b>Shrift:</b> <b>{font_info['name']}</b>\n"
                f"📦 <b>Animatsiyalar soni:</b> {len(input_stickers)} ta\n"
                f"🔗 <b>Havola:</b> <a href=\"{pack_link}\">{pack_link}</a>\n\n"
                f"👇 Quyidagi tugma orqali to'plamni Telegramingizga qo'shib oling:",
                reply_markup=markup,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False
            )
        else:
            await status_msg.edit_text("❌ Kechirasiz, emoji paketini yaratish jarayonida xatolik yuz berdi.")

    except Exception as e:
        logger.error(f"Global handler error: {e}", exc_info=True)
        await callback.message.answer("❌ Kutilmagan texnik xatolik yuz berdi.")
    finally:
        ACTIVE_USERS.discard(user_id)
