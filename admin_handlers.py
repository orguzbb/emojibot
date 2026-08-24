import os
import gzip
import json
import logging
import asyncio
import re
from pathlib import Path

from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    BufferedInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

from config import ADMIN_IDS, TEMPLATES_DIR, FONTS_DIR
from lottie_processor import process_tgs_template, process_all_templates
from database import get_users_count, get_all_user_ids

logger = logging.getLogger(__name__)
admin_router = Router()


class AdminStates(StatesGroup):
    waiting_for_tgs_file = State()
    waiting_for_pack_link = State()
    confirm_pack_import = State()
    waiting_for_broadcast_msg = State()
    confirm_broadcast = State()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📁 Shablonlar ro'yxati", callback_data="admin:list"),
                InlineKeyboardButton(text="➕ Shablon qo'shish (.tgs)", callback_data="admin:add")
            ],
            [
                InlineKeyboardButton(text="📥 Packdan import qilish (100+)", callback_data="admin:import_pack"),
                InlineKeyboardButton(text="🗑 Shablon o'chirish", callback_data="admin:delete_menu")
            ],
            [
                InlineKeyboardButton(text="🧪 Barchasini test qilish", callback_data="admin:test"),
                InlineKeyboardButton(text="📊 Bot statistikasi", callback_data="admin:stats")
            ],
            [
                InlineKeyboardButton(text="📢 Xabar yuborish (/broadcast)", callback_data="admin:broadcast_start")
            ]
        ]
    )


@admin_router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.clear()
    p = Path(TEMPLATES_DIR)
    tgs_count = len(list(p.glob("*.tgs"))) if p.exists() else 0
    users_count = get_users_count()

    text = (
        "👑 <b>Admin Boshqaruv Paneli</b>\n\n"
        f"👥 <b>Foydalanuvchilar soni:</b> {users_count} ta\n"
        f"📂 <b>Faol shablonlar soni:</b> {tgs_count} ta\n"
        f"🤖 <b>Bot holati:</b> Ishchi (Online)\n\n"
        "<i>Quyidagi bo'limlardan birini tanlang:</i>"
    )
    await message.answer(text, reply_markup=get_admin_menu_keyboard(), parse_mode=ParseMode.HTML)


@admin_router.callback_query(F.data == "admin:main")
async def cb_admin_main(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Ruxsat berilmagan.", show_alert=True)
        return

    await state.clear()
    p = Path(TEMPLATES_DIR)
    tgs_count = len(list(p.glob("*.tgs"))) if p.exists() else 0
    users_count = get_users_count()

    text = (
        "👑 <b>Admin Boshqaruv Paneli</b>\n\n"
        f"👥 <b>Foydalanuvchilar soni:</b> {users_count} ta\n"
        f"📂 <b>Faol shablonlar soni:</b> {tgs_count} ta\n"
        f"🤖 <b>Bot holati:</b> Ishchi (Online)\n\n"
        "<i>Quyidagi bo'limlardan birini tanlang:</i>"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_menu_keyboard(), parse_mode=ParseMode.HTML)
    await callback.answer()


@admin_router.callback_query(F.data == "admin:list")
async def cb_admin_list(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    p = Path(TEMPLATES_DIR)
    tgs_files = sorted(p.glob("*.tgs"), key=lambda f: (int(f.stem) if f.stem.isdigit() else 9999, f.name)) if p.exists() else []

    if not tgs_files:
        text = "📁 <b>Hozircha hech qanday shablon mavjud emas.</b>"
    else:
        text = f"📁 <b>Barcha shablonlar ro'yxati ({len(tgs_files)} ta):</b>\n\n"
        total_size = 0
        # Ko'p shablon bo'lsa qisqartirib ko'rsatish
        display_files = tgs_files[:25]
        for idx, f in enumerate(display_files, start=1):
            size_kb = f.stat().st_size / 1024
            total_size += size_kb
            text += f"<b>{f.stem}.</b> <code>{f.name}</code> ({size_kb:.1f} KB)\n"
        
        if len(tgs_files) > 25:
            remaining_size = sum(f.stat().st_size for f in tgs_files[25:]) / 1024
            total_size += remaining_size
            text += f"\n<i>... va yana {len(tgs_files) - 25} ta boshqa shablonlar.</i>\n"
        
        text += f"\n📦 <b>Jami umumiy hajm:</b> {total_size / 1024:.2f} MB"

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Yangi qo'shish", callback_data="admin:add"),
                InlineKeyboardButton(text="📥 Packdan import", callback_data="admin:import_pack")
            ],
            [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="admin:main")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()


@admin_router.callback_query(F.data == "admin:add")
async def cb_admin_add(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    await state.set_state(AdminStates.waiting_for_tgs_file)
    text = (
        "➕ <b>Yangi shablon qo'shish</b>\n\n"
        "Menga yangi <b>.tgs</b> faylini yuboring (fayl / document ko'rinishida).\n\n"
        "💡 <i>Talablar:</i>\n"
        "• Telegram Lottie animatsiyasi (.tgs formati)\n"
        "• Standart 512x512 o'lcham\n"
        "• Maksimal davomiyligi 3 soniya (60 FPS)\n\n"
        "<i>Bekor qilish uchun /cancel yoki quyidagi tugmani bosing:</i>"
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin:main")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()


@admin_router.message(AdminStates.waiting_for_tgs_file, F.document)
async def handle_uploaded_tgs(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    doc = message.document
    if not doc.file_name or not doc.file_name.lower().endswith(".tgs"):
        await message.answer("⚠️ Iltimos, faqat <b>.tgs</b> formatidagi fayl yuboring!", parse_mode=ParseMode.HTML)
        return

    status_msg = await message.answer("⏳ <i>Fayl yuklab olinmoqda va tekshirilmoqda...</i>", parse_mode=ParseMode.HTML)

    try:
        file = await bot.get_file(doc.file_id)
        file_bytes_io = await bot.download_file(file.file_path)
        file_bytes = file_bytes_io.read()

        try:
            decompressed = gzip.decompress(file_bytes)
            data = json.loads(decompressed)
        except Exception as e:
            await status_msg.edit_text(f"❌ <b>Xatolik:</b> Ushbu fayl to'g'ri .tgs (gzipped Lottie JSON) formati emas!\n<code>{e}</code>", parse_mode=ParseMode.HTML)
            return

        w = data.get("w", 512)
        h = data.get("h", 512)
        fr = data.get("fr", 60)

        p = Path(TEMPLATES_DIR)
        p.mkdir(parents=True, exist_ok=True)

        existing_numbers = []
        for f in p.glob("*.tgs"):
            stem = f.stem
            if stem.isdigit():
                existing_numbers.append(int(stem))

        next_num = max(existing_numbers, default=0) + 1
        target_filename = f"{next_num}.tgs"
        target_path = p / target_filename

        font_sample = Path(FONTS_DIR) / "stapel.ttf"
        test_proc = process_tgs_template(file_bytes, "ASILBEK", str(font_sample))

        with open(target_path, "wb") as f:
            f.write(file_bytes)

        await state.clear()

        success_text = (
            f"✅ <b>Yangi shablon muvaffaqiyatli saqlandi!</b>\n\n"
            f"🏷 <b>Fayl nomi:</b> <code>{target_filename}</code>\n"
            f"📐 <b>O'lchami:</b> {w}x{h} px\n"
            f"🎞 <b>FPS:</b> {fr} fps\n"
            f"📦 <b>Hajmi:</b> {len(file_bytes)/1024:.1f} KB\n\n"
            f"🎉 Endi ushbu shablon barcha foydalanuvchilarning yangi emoji to'plamlariga avtomatik qo'shiladi!"
        )

        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📁 Shablonlar ro'yxati", callback_data="admin:list")],
                [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="admin:main")]
            ]
        )
        await status_msg.edit_text(success_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Shablon yuklashda xatolik: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ <b>Kutilmagan xatolik yuz berdi:</b> {e}", parse_mode=ParseMode.HTML)


# --- PACKDAN IMPORT QILISH (IMPORT STICKER/EMOJI SET) ---
@admin_router.callback_query(F.data == "admin:import_pack")
async def cb_admin_import_pack(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    await state.set_state(AdminStates.waiting_for_pack_link)
    text = (
        "📥 <b>Sticker / Emoji Packdan shablonlarni import qilish</b>\n\n"
        "Menga Telegram emoji yoki stiker to'plamining <b>havolasini</b> (yoki nomini) yuboring.\n\n"
        "<i>Misol uchun:</i>\n"
        "• <code>https://t.me/addemoji/e7692310743_919735_by_Skwjjeejjej_bot</code>\n"
        "• <code>https://t.me/addstickers/...</code>\n"
        "• yoki paket nomini: <code>e7692310743_919735_by_Skwjjeejjej_bot</code>\n\n"
        "<i>Bekor qilish uchun /cancel yoki quyidagi tugmani bosing:</i>"
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin:main")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()


@admin_router.message(AdminStates.waiting_for_pack_link, F.text)
async def handle_pack_link_input(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    raw_text = message.text.strip()
    if raw_text.lower() in ("/cancel", "cancel", "bekor"):
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=get_admin_menu_keyboard())
        return

    # Paket nomini ajratib olish
    pack_name = raw_text
    if "t.me/addemoji/" in pack_name:
        pack_name = pack_name.split("t.me/addemoji/")[1].split("?")[0].strip()
    elif "t.me/addstickers/" in pack_name:
        pack_name = pack_name.split("t.me/addstickers/")[1].split("?")[0].strip()

    status_msg = await message.answer(f"🔍 <b>To'plam ma'lumotlari qidirilmoqda:</b> <code>{pack_name}</code>...", parse_mode=ParseMode.HTML)

    try:
        sticker_set = await bot.get_sticker_set(name=pack_name)
        stickers_count = len(sticker_set.stickers)

        if stickers_count == 0:
            await status_msg.edit_text("❌ Ushbu to'plamda hech qanday stiker topilmadi.", reply_markup=get_admin_menu_keyboard())
            return

        await state.update_data(import_pack_name=pack_name, stickers_count=stickers_count)
        await state.set_state(AdminStates.confirm_pack_import)

        confirm_text = (
            f"📦 <b>To'plam topildi!</b>\n\n"
            f"🏷 <b>Nomi:</b> {sticker_set.title}\n"
            f"🔗 <b>Paket nomi:</b> <code>{pack_name}</code>\n"
            f"🎞 <b>Stikerlar soni:</b> {stickers_count} ta\n"
            f"🌟 <b>Turi:</b> {sticker_set.sticker_type}\n\n"
            f"Barcha <b>{stickers_count} ta</b> animatsiyalarni yuklab olib, bot shablonlariga qo'shamizmi?"
        )

        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=f"🚀 Ha, import qilish ({stickers_count} ta)", callback_data="admin:do_import_pack"),
                    InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin:main")
                ]
            ]
        )
        await status_msg.edit_text(confirm_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Get sticker set error: {e}")
        await status_msg.edit_text(
            f"❌ <b>To'plamni yuklab bo'lmadi:</b>\n<code>{e}</code>\n\n"
            "Iltimos, havola to'g'riligini tekshiring va qaytadan yuboring.",
            parse_mode=ParseMode.HTML
        )


@admin_router.callback_query(AdminStates.confirm_pack_import, F.data == "admin:do_import_pack")
async def execute_pack_import(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not is_admin(callback.from_user.id):
        return

    data = await state.get_data()
    pack_name = data.get("import_pack_name")
    await state.clear()

    status_msg = await callback.message.edit_text(
        f"⏳ <b>To'plam yuklab olinmoqda...</b> (0%)",
        parse_mode=ParseMode.HTML
    )

    try:
        sticker_set = await bot.get_sticker_set(name=pack_name)
        total_stickers = len(sticker_set.stickers)

        p = Path(TEMPLATES_DIR)
        p.mkdir(parents=True, exist_ok=True)

        existing_numbers = []
        for f in p.glob("*.tgs"):
            stem = f.stem
            if stem.isdigit():
                existing_numbers.append(int(stem))

        current_next_num = max(existing_numbers, default=0) + 1

        imported_count = 0
        skipped_count = 0

        for idx, st in enumerate(sticker_set.stickers, start=1):
            try:
                file = await bot.get_file(st.file_id)
                file_io = await bot.download_file(file.file_path)
                file_bytes = file_io.read()

                # Gzip va Lottie formatini tekshiramiz
                try:
                    decompressed = gzip.decompress(file_bytes)
                    js_data = json.loads(decompressed)
                except:
                    skipped_count += 1
                    continue

                # Yangi shablon sifatida saqlaymiz
                target_path = p / f"{current_next_num}.tgs"
                with open(target_path, "wb") as f:
                    f.write(file_bytes)

                current_next_num += 1
                imported_count += 1

                # Progressni har 10 ta stikerda yangilaymiz
                if idx % 10 == 0 or idx == total_stickers:
                    percent = int((idx / total_stickers) * 100)
                    try:
                        await status_msg.edit_text(
                            f"📥 <b>Shablonlar import qilinmoqda:</b>\n\n"
                            f"⏳ Jarayon: <b>{idx}/{total_stickers}</b> ({percent}%)\n"
                            f"✅ Muvaffaqiyatli saqlandi: {imported_count} ta",
                            parse_mode=ParseMode.HTML
                        )
                    except:
                        pass

                await asyncio.sleep(0.05)

            except Exception as item_err:
                logger.warning(f"Sticker import error: {item_err}")
                skipped_count += 1

        total_now = len(list(p.glob("*.tgs")))
        result_text = (
            f"🎉 <b>Import muvaffaqiyatli yakunlandi!</b>\n\n"
            f"📥 <b>To'plam:</b> {sticker_set.title}\n"
            f"✅ <b>Qo'shilgan yangi shablonlar:</b> {imported_count} ta\n"
            f"⚠️ <b>O'tkazib yuborilgan:</b> {skipped_count} ta\n\n"
            f"📂 <b>Botdagi jami faol shablonlar soni:</b> {total_now} ta!\n\n"
            f"<i>Endi foydalanuvchilar ism kiritganda barcha {total_now} ta shablon avtomatik ishlaydi.</i>"
        )

        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📁 Shablonlar ro'yxati", callback_data="admin:list")],
                [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="admin:main")]
            ]
        )
        await status_msg.edit_text(result_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Pack import fatal error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ <b>Import jarayonida xatolik yuz berdi:</b>\n<code>{e}</code>", parse_mode=ParseMode.HTML)


@admin_router.callback_query(F.data == "admin:delete_menu")
async def cb_admin_delete_menu(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    p = Path(TEMPLATES_DIR)
    tgs_files = sorted(p.glob("*.tgs"), key=lambda f: (int(f.stem) if f.stem.isdigit() else 9999, f.name)) if p.exists() else []

    if not tgs_files:
        text = "📁 O'chirish uchun shablonlar mavjud emas."
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="admin:main")]
            ]
        )
        await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
        return

    text = f"🗑 <b>O'chirmoqchi bo'lgan shabloningizni tanlang (Jami {len(tgs_files)} ta):</b>"
    buttons = []
    row = []
    for f in tgs_files[:30]: # Dastlabki 30 tasini ko'rsatish
        row.append(InlineKeyboardButton(text=f"❌ {f.stem}", callback_data=f"admin:confirm_del:{f.name}"))
        if len(row) == 5:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="admin:main")])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin:confirm_del:"))
async def cb_admin_confirm_del(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    fname = callback.data.split(":", 2)[2]
    text = (
        f"⚠️ <b>Haqiqatan ham <code>{fname}</code> shablonini o'chirmoqchimisiz?</b>\n\n"
        "<i>Ushbu amalni ortga qaytarib bo'lmaydi!</i>"
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🗑 Ha, o'chirish", callback_data=f"admin:do_del:{fname}"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin:delete_menu")
            ]
        ]
    )
    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin:do_del:"))
async def cb_admin_do_del(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    fname = callback.data.split(":", 2)[2]
    target_path = Path(TEMPLATES_DIR) / fname

    if target_path.exists():
        try:
            target_path.unlink()
            text = f"✅ <b><code>{fname}</code> shabloni muvaffaqiyatli o'chirildi!</b>"
        except Exception as e:
            text = f"❌ O'chirishda xatolik: {e}"
    else:
        text = f"⚠️ <code>{fname}</code> topilmadi."

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Boshqa shablon o'chirish", callback_data="admin:delete_menu")],
            [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="admin:main")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()


@admin_router.callback_query(F.data == "admin:test")
async def cb_admin_test(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    await callback.message.edit_text("⏳ <i>Shablonlar testdan o'tkazilmoqda...</i>", parse_mode=ParseMode.HTML)
    
    font_path = str(Path(FONTS_DIR) / "stapel.ttf")
    results = process_all_templates(str(TEMPLATES_DIR), "ASILBEK", font_path)

    text = f"🧪 <b>Shablonlar test natijasi ({len(results)} ta):</b>\n\n"
    for name, proc_bytes in results[:20]:
        size_kb = len(proc_bytes) / 1024
        text += f"• <code>{name}</code> — ✅ Ishlaydi ({size_kb:.1f} KB)\n"
    
    if len(results) > 20:
        text += f"\n<i>... va qolgan barcha {len(results) - 20} ta shablonlar ham to'liq ishchi holatda!</i>"

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="admin:main")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()


@admin_router.callback_query(F.data == "admin:stats")
async def cb_admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    p = Path(TEMPLATES_DIR)
    tgs_files = list(p.glob("*.tgs")) if p.exists() else []
    total_size_mb = sum(f.stat().st_size for f in tgs_files) / (1024 * 1024) if tgs_files else 0

    fonts_p = Path(FONTS_DIR)
    fonts_count = len(list(fonts_p.glob("*.ttf"))) if fonts_p.exists() else 0
    users_count = get_users_count()

    text = (
        "📊 <b>Bot Statistikasi va Ma'lumotlar</b>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {users_count} ta\n"
        f"📁 <b>Jami faol shablonlar:</b> {len(tgs_files)} ta\n"
        f"💾 <b>Shablonlar umumiy hajmi:</b> {total_size_mb:.2f} MB\n"
        f"🔤 <b>O'rnatilgan shriftlar:</b> {fonts_count} ta (Stapel, Inter, Grobold)\n"
        f"👑 <b>Bosh administrator ID:</b> <code>1323217434</code>\n"
        "⚡ <b>Holat:</b> Barcha servislar faol va tayyor."
    )

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="admin:main")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()


# --- BROADCAST SYSTEM (/broadcast) ---
@admin_router.message(Command("broadcast"))
@admin_router.callback_query(F.data == "admin:broadcast_start")
async def cmd_broadcast_start(event: Message | CallbackQuery, state: FSMContext):
    user_id = event.from_user.id
    if not is_admin(user_id):
        return

    await state.set_state(AdminStates.waiting_for_broadcast_msg)
    users_count = get_users_count()

    text = (
        "📢 <b>Barcha foydalanuvchilarga xabar yuborish (/broadcast)</b>\n\n"
        f"Hozirda botda <b>{users_count}</b> ta foydalanuvchi mavjud.\n\n"
        "Yubormoqchi bo'lgan xabaringizni yozing (matn, rasm, video, formatlangan xabar bo'lishi mumkin):\n\n"
        "<i>Bekor qilish uchun /cancel deb yozing.</i>"
    )

    if isinstance(event, CallbackQuery):
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin:main")]
            ]
        )
        await event.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
        await event.answer()
    else:
        await event.answer(text, parse_mode=ParseMode.HTML)


@admin_router.message(AdminStates.waiting_for_broadcast_msg)
async def handle_broadcast_message_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    if message.text and message.text.strip().lower() in ("/cancel", "cancel", "bekor"):
        await state.clear()
        await message.answer("❌ Xabar yuborish bekor qilindi.", reply_markup=get_admin_menu_keyboard())
        return

    users_count = get_users_count()
    await state.update_data(broadcast_msg_id=message.message_id, from_chat_id=message.chat.id)
    await state.set_state(AdminStates.confirm_broadcast)

    confirm_text = (
        f"⚠️ <b>Xabarni tasdiqlash:</b>\n\n"
        f"Ushbu xabar <b>{users_count} ta</b> foydalanuvchiga yuboriladi.\n"
        f"Yuborishni boshlaymizmi?"
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚀 Ha, yuborilsin", callback_data="admin:do_broadcast"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin:main")
            ]
        ]
    )
    await message.reply(confirm_text, reply_markup=markup, parse_mode=ParseMode.HTML)


@admin_router.callback_query(AdminStates.confirm_broadcast, F.data == "admin:do_broadcast")
async def execute_broadcast(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not is_admin(callback.from_user.id):
        return

    data = await state.get_data()
    msg_id = data.get("broadcast_msg_id")
    chat_id = data.get("from_chat_id")
    await state.clear()

    user_ids = get_all_user_ids()
    total = len(user_ids)

    if total == 0:
        await callback.message.edit_text("❌ Foydalanuvchilar topilmadi.", reply_markup=get_admin_menu_keyboard())
        return

    status_msg = await callback.message.edit_text(
        f"🚀 <b>Xabar yuborilmoqda...</b> (0/{total})",
        parse_mode=ParseMode.HTML
    )

    sent = 0
    blocked = 0
    failed = 0

    for idx, uid in enumerate(user_ids, start=1):
        try:
            await bot.copy_message(chat_id=uid, from_chat_id=chat_id, message_id=msg_id)
            sent += 1
        except TelegramForbiddenError:
            blocked += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            try:
                await bot.copy_message(chat_id=uid, from_chat_id=chat_id, message_id=msg_id)
                sent += 1
            except:
                failed += 1
        except Exception as e:
            failed += 1

        if idx % 25 == 0 or idx == total:
            try:
                await status_msg.edit_text(
                    f"🚀 <b>Xabar yuborilmoqda...</b> ({idx}/{total})\n"
                    f"✅ Yetkazildi: {sent}\n"
                    f"🚫 Bloklagan: {blocked}",
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
        await asyncio.sleep(0.04)

    report_text = (
        f"📢 <b>Xabar yuborish yakunlandi!</b>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {total}\n"
        f"✅ <b>Yetkazildi:</b> {sent} ta\n"
        f"🚫 <b>Botni bloklagan:</b> {blocked} ta\n"
        f"⚠️ <b>Yetkazilmadi:</b> {failed} ta"
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="admin:main")]
        ]
    )
    await status_msg.edit_text(report_text, reply_markup=markup, parse_mode=ParseMode.HTML)
