import os
import gzip
import json
import random
import logging
import asyncio
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InputSticker, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from aiogram.exceptions import TelegramRetryAfter, TelegramAPIError

from config import (
    BOT_TOKEN,
    BOT_USERNAME,
    ADMIN_IDS,
    TEMPLATES_DIR,
    FONTS_DIR,
    DEFAULT_FONT_PATH,
    WEBAPP_URL,
    SERVER_HOST,
    SERVER_PORT
)
from lottie_processor import process_tgs_template
from database import (
    add_or_update_user,
    increment_user_packs,
    save_user_pack,
    get_user_packs,
    get_user_balance,
    deduct_user_balance,
    get_emoji_price
)
from handlers import FONTS_MAP, DEFAULT_EMOJIS, to_name_slug

logger = logging.getLogger("server")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="GnEmoji Mini App Server", version="1.0.0")

# Enable CORS for Telegram WebApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files directory
WEBAPP_DIR = Path(__file__).resolve().parent / "webapp"
app.mount("/static", StaticFiles(directory=str(WEBAPP_DIR)), name="static")

# Shared Bot instance for Telegram API interactions
bot_instance: Optional[Bot] = None


def set_bot(bot: Bot):
    global bot_instance
    bot_instance = bot


def get_bot() -> Bot:
    global bot_instance
    if bot_instance is None:
        bot_instance = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    return bot_instance


# ==================== PYDANTIC MODELS ====================

# In-memory cache for raw template bytes to make preview generation ultra fast
_TEMPLATE_BYTES_CACHE = {}

def get_template_bytes(template_name: str) -> Optional[bytes]:
    if not template_name.endswith(".tgs"):
        template_name = f"{template_name}.tgs"
    if template_name in _TEMPLATE_BYTES_CACHE:
        return _TEMPLATE_BYTES_CACHE[template_name]
    
    tgs_path = Path(TEMPLATES_DIR) / template_name
    if not tgs_path.exists():
        return None
    with open(tgs_path, "rb") as f:
        data = f.read()
    _TEMPLATE_BYTES_CACHE[template_name] = data
    return data


class PreviewRequest(BaseModel):
    template_id: str
    text: str
    font: str = "stapel"
    scale: Optional[float] = 1.0


class BatchPreviewRequest(BaseModel):
    template_ids: List[str]
    text: str
    font: str = "stapel"
    scale: Optional[float] = 1.0


class GenerateRequest(BaseModel):
    user_id: int
    text: str
    font: str = "stapel"
    mode: str = "single"  # "single", "selected", "all", "add_to_pack"
    pack_name: Optional[str] = None
    template_id: Optional[str] = "1.tgs"
    selected_templates: Optional[List[str]] = None
    scale: Optional[float] = 1.0
    init_data: Optional[str] = None


class AddToPackRequest(BaseModel):
    user_id: int
    pack_name: str
    text: str
    font: str = "stapel"
    template_id: str = "1.tgs"
    scale: Optional[float] = 1.0


class CreateInvoiceRequest(BaseModel):
    user_id: int
    count: int = 1
    text: Optional[str] = ""


# ==================== WEB APP FRONTEND ROUTE ====================

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = WEBAPP_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Web app frontend topilmadi")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/style.css")
async def serve_css():
    return FileResponse(WEBAPP_DIR / "style.css", media_type="text/css")


@app.get("/app.js")
async def serve_js():
    return FileResponse(WEBAPP_DIR / "app.js", media_type="application/javascript")


@app.get("/ticket_templates.js")
async def serve_ticket_templates():
    return FileResponse(WEBAPP_DIR / "ticket_templates.js", media_type="application/javascript")


# ==================== REST API ENDPOINTS ====================

@app.get("/api/info")
async def get_info():
    """Returns bot meta information, emoji prices and font lists"""
    p = Path(TEMPLATES_DIR)
    total_templates = len(list(p.glob("*.tgs"))) if p.exists() else 0
    emoji_price = get_emoji_price()

    return {
        "bot_username": BOT_USERNAME,
        "total_templates": total_templates,
        "ticket_templates_count": 13,
        "logo_templates_count": max(0, total_templates - 13),
        "emoji_price": emoji_price,
        "fonts": [
            {"id": "stapel", "name": "Stapel", "description": "Qalin va Geometrik"},
            {"id": "inter", "name": "Inter", "description": "Klassik va Toza"},
            {"id": "grobold", "name": "Grobold", "description": "Zamonaviy Display"}
        ]
    }


@app.get("/api/user_info")
async def get_user_info_endpoint(user_id: int = Query(...)):
    """Returns user balance, price per emoji, user created packs and admin flag"""
    balance = get_user_balance(user_id)
    price = get_emoji_price()
    packs = get_user_packs(user_id)
    is_admin = user_id in ADMIN_IDS

    return {
        "user_id": user_id,
        "balance": balance,
        "emoji_price": price,
        "packs": packs,
        "is_admin": is_admin
    }


class SendInvoiceRequest(BaseModel):
    user_id: int
    count: int = 1
    text: str
    font: str = "stapel"
    mode: str = "single"
    pack_name: Optional[str] = None
    template_id: Optional[str] = "1.tgs"
    selected_templates: Optional[List[str]] = None


@app.post("/api/send_invoice_to_chat")
async def send_invoice_to_chat_endpoint(req: SendInvoiceRequest):
    """Sends a Telegram Stars (XTR) invoice directly to user's Telegram chat"""
    unit_price = get_emoji_price()
    total_cost = max(1, req.count * unit_price)

    clean_text = req.text.strip().upper()[:16]
    if not clean_text:
        clean_text = "EMOJI"

    bot = get_bot()

    action_type = "gen_all" if req.mode == "all" else ("gen_one" if req.mode == "single" else "gen_selected")

    if req.selected_templates and len(req.selected_templates) > 0:
        raw_files = ",".join(req.selected_templates)
    elif req.mode == "single":
        raw_files = req.template_id or "1.tgs"
    else:
        raw_files = "all"

    dest_flag = f"add_{req.pack_name}" if (req.mode == "add_to_pack" and req.pack_name) else "new"
    extra_param = f"{raw_files}|{dest_flag}"

    payload = f"buy_pack:{req.user_id}:{req.font}:{clean_text}:{action_type}:{extra_param}:{total_cost}"

    try:
        await bot.send_invoice(
            chat_id=req.user_id,
            title="Stiker generatsiya",
            description=f"'{clean_text}' uchun {req.count} ta stiker to'lovi.",
            payload=payload,
            currency="XTR",
            prices=[LabeledPrice(label=f"Stars ({req.count} ta)", amount=total_cost)]
        )
        return {"ok": True, "total_cost": total_cost, "user_id": req.user_id}
    except Exception as e:
        logger.error(f"Send invoice to chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Botga hisob-faktura yuborishda xatolik: {e}")


@app.get("/api/templates")
async def get_templates_list():
    """Returns full list of available 117 animated emoji templates"""
    p = Path(TEMPLATES_DIR)
    if not p.exists():
        return {"templates": []}

    files = sorted(p.glob("*.tgs"), key=lambda f: (int(f.stem) if f.stem.isdigit() else 9999, f.name))
    items = []
    for f in files:
        num = int(f.stem) if f.stem.isdigit() else 999
        items.append({
            "id": f.stem,
            "filename": f.name,
            "category": "ticket" if num <= 13 else "logo",
            "name": f"Ticket #{num}" if num <= 13 else f"Logo #{num - 13}"
        })
    return {"templates": items}


@app.post("/api/preview")
async def generate_preview(req: PreviewRequest):
    """Renders a single template with text/font/scale and returns Lottie JSON"""
    clean_text = req.text.strip().upper()[:16]
    if not clean_text:
        clean_text = "ISMINGIZ"

    font_info = FONTS_MAP.get(req.font, FONTS_MAP["stapel"])
    font_file_path = Path(FONTS_DIR) / font_info["file"]
    if not font_file_path.exists():
        font_file_path = Path(DEFAULT_FONT_PATH)

    raw_bytes = get_template_bytes(req.template_id)
    if not raw_bytes:
        raise HTTPException(status_code=404, detail="Shablon fayli topilmadi")

    try:
        proc_bytes = process_tgs_template(
            template_bytes=raw_bytes,
            text=clean_text,
            font_path=str(font_file_path),
            text_scale=req.scale or 1.0
        )
        lottie_json = json.loads(gzip.decompress(proc_bytes).decode("utf-8"))
        return JSONResponse(content=lottie_json)
    except Exception as e:
        logger.error(f"Preview generation error for {req.template_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Prevyu yaratishda xatolik yuz berdi")


@app.post("/api/batch_preview")
async def generate_batch_preview(req: BatchPreviewRequest):
    """Renders multiple templates in a single batch request for speed"""
    clean_text = req.text.strip().upper()[:16]
    if not clean_text:
        clean_text = "ISMINGIZ"

    font_info = FONTS_MAP.get(req.font, FONTS_MAP["stapel"])
    font_file_path = Path(FONTS_DIR) / font_info["file"]
    if not font_file_path.exists():
        font_file_path = Path(DEFAULT_FONT_PATH)

    results = {}
    for tpl_id in req.template_ids:
        raw_bytes = get_template_bytes(tpl_id)
        if not raw_bytes:
            continue
        try:
            proc_bytes = process_tgs_template(
                template_bytes=raw_bytes,
                text=clean_text,
                font_path=str(font_file_path),
                text_scale=req.scale or 1.0
            )
            lottie_json = json.loads(gzip.decompress(proc_bytes).decode("utf-8"))
            filename = tpl_id if tpl_id.endswith(".tgs") else f"{tpl_id}.tgs"
            results[filename] = lottie_json
        except Exception as e:
            logger.warning(f"Batch preview error for {tpl_id}: {e}")

    return JSONResponse(content={"previews": results})


_background_tasks = set()


async def background_add_stickers(
    bot_instance: Bot,
    user_id: int,
    pack_name: str,
    pack_title: str,
    pack_link: str,
    stickers_to_add: List[InputSticker],
    total_count: int,
    clean_text: str
):
    """Safely adds stickers in background to prevent HTTP timeouts and handle Telegram flood limits"""
    logger.info(f"Background worker started: adding {len(stickers_to_add)} stickers to {pack_name}")
    for idx, st in enumerate(stickers_to_add):
        for attempt in range(8):
            try:
                await bot_instance.add_sticker_to_set(
                    user_id=user_id,
                    name=pack_name,
                    sticker=st
                )
                break
            except TelegramRetryAfter as retry_err:
                wait_sec = retry_err.retry_after + 1.5
                logger.warning(f"Background FloodWait on sticker {idx+1}: waiting {wait_sec}s")
                await asyncio.sleep(wait_sec)
            except Exception as e:
                logger.warning(f"Background add sticker {idx+1} error (attempt {attempt+1}): {e}")
                await asyncio.sleep(1.0)
        # Polite spacing to avoid fast rate limits
        await asyncio.sleep(0.4)

    logger.info(f"Background worker completed for {pack_name} (Total: {total_count})")
    try:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="➕ To'plamni Telegramda Ochish", url=pack_link)]
            ]
        )
        await bot_instance.send_message(
            chat_id=user_id,
            text=(
                f"🎉 <b>Barcha stikerlar muvaffaqiyatli yuklandi!</b>\n\n"
                f"✍️ <b>Matn:</b> <code>{clean_text}</code>\n"
                f"📦 <b>To'plam:</b> <a href=\"{pack_link}\">{pack_title}</a>\n"
                f"⚡ <b>Jami stikerlar:</b> {total_count} ta to'liq tayyor!\n\n"
                f"<i>Foydalanish uchun to'plamni oching:</i>"
            ),
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )
    except Exception as notify_err:
        logger.info(f"Background completion notification warning: {notify_err}")


@app.post("/api/generate")
async def generate_emoji_pack(req: GenerateRequest):
    """
    Bulletproof Generation Endpoint:
    - Verifies user balance (deducts once)
    - Creates sticker set immediately
    - Adds initial batch synchronously and runs remaining batch in background
    - Returns instant success response to Mini App
    """
    clean_text = req.text.strip().upper()[:16]
    if not clean_text:
        raise HTTPException(status_code=400, detail="Matn kiritilmagan")

    bot = get_bot()

    # Font lookup
    font_key = req.font.lower() if req.font else "stapel"
    font_info = FONTS_MAP.get(font_key, FONTS_MAP["stapel"])
    font_file_path = Path(FONTS_DIR) / font_info["file"]
    if not font_file_path.exists():
        font_file_path = Path(FONTS_DIR) / "stapel.ttf"

    # Template filtering
    p = Path(TEMPLATES_DIR)
    if req.selected_templates and len(req.selected_templates) > 0:
        target_files = [p / f for f in req.selected_templates if (p / f).exists()]
    elif req.mode == "single":
        tgs_name = req.template_id if req.template_id and req.template_id.endswith(".tgs") else f"{req.template_id or '1'}.tgs"
        target_files = [p / tgs_name] if (p / tgs_name).exists() else [next(p.glob('*.tgs'))]
    else:
        # Full Mega Pack (all templates)
        target_files = sorted(p.glob("*.tgs"), key=lambda f: (int(f.stem) if f.stem.isdigit() else 9999, f.name))

    if not target_files:
        raise HTTPException(status_code=404, detail="Shablonlar topilmadi")

    # Pricing & Balance Check
    total_stickers_count = len(target_files)
    emoji_price = get_emoji_price()
    total_cost = total_stickers_count * emoji_price
    
    if total_cost > 0:
        balance = get_user_balance(req.user_id)
        if balance < total_cost:
            raise HTTPException(
                status_code=402,
                detail=f"Balansingiz yetarli emas! Sizda {balance} ⭐ Stars bor, kerak: {total_cost} ⭐ Stars ({total_stickers_count} ta emoji x {emoji_price} ⭐). Iltimos, hisobingizni to'ldiring."
            )
        
        # Balansdan yechish (Faqat bir marta)
        deducted = deduct_user_balance(
            user_id=req.user_id,
            amount=total_cost,
            tx_type="purchase_webapp",
            description=f"Mini App: {clean_text} ({total_stickers_count} ta emoji, {total_cost} ⭐)"
        )
        if not deducted:
            raise HTTPException(status_code=402, detail="Balansdan Stars yechishda xatolik yuz berdi.")

    # Generate processed animated stickers
    input_stickers: List[InputSticker] = []
    for idx, tgs_file in enumerate(target_files):
        with open(tgs_file, "rb") as f:
            raw_bytes = f.read()

        proc_bytes = process_tgs_template(
            template_bytes=raw_bytes,
            text=clean_text,
            font_path=str(font_file_path),
            text_scale=req.scale or 1.0
        )

        emoji_char = DEFAULT_EMOJIS[idx % len(DEFAULT_EMOJIS)]
        input_stickers.append(
            InputSticker(
                sticker=BufferedInputFile(proc_bytes, filename=f"emoji_{idx+1}.tgs"),
                emoji_list=[emoji_char],
                format="animated"
            )
        )

    # Branch A: Add to existing user pack
    if (req.mode == "add_to_pack" or req.pack_name) and req.pack_name:
        pack_name = req.pack_name
        pack_title = req.pack_name
        try:
            sync_limit = min(5, len(input_stickers))
            for idx in range(sync_limit):
                for attempt in range(4):
                    try:
                        await bot.add_sticker_to_set(
                            user_id=req.user_id,
                            name=pack_name,
                            sticker=input_stickers[idx]
                        )
                        break
                    except TelegramRetryAfter as retry_err:
                        await asyncio.sleep(retry_err.retry_after + 1.0)
                    except Exception as add_err:
                        logger.warning(f"Add sticker {idx+1} warning (attempt {attempt+1}): {add_err}")
                        await asyncio.sleep(0.2)
                await asyncio.sleep(0.04)

            pack_link = f"https://t.me/addemoji/{pack_name}"
            
            if len(input_stickers) > 5:
                bg_task = asyncio.create_task(
                    background_add_stickers(
                        bot_instance=bot,
                        user_id=req.user_id,
                        pack_name=pack_name,
                        pack_title=pack_title,
                        pack_link=pack_link,
                        stickers_to_add=input_stickers[5:],
                        total_count=len(input_stickers),
                        clean_text=clean_text
                    )
                )
                _background_tasks.add(bg_task)
                bg_task.add_done_callback(_background_tasks.discard)

            new_bal = get_user_balance(req.user_id)
            return {
                "ok": True,
                "pack_name": pack_name,
                "pack_title": pack_title,
                "pack_link": pack_link,
                "stickers_count": len(input_stickers),
                "remaining_balance": new_bal,
                "mode": "add_to_pack"
            }
        except Exception as e:
            if total_cost > 0:
                add_user_balance(req.user_id, total_cost, tx_type="refund", description="Muvaffaqiyatsiz to'plam uchun qaytarildi")
            logger.error(f"Add to pack error: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Mavjud to'plamga qo'shishda xatolik: {str(e)}")

    # Branch B: Create a brand new sticker set
    raw_slug = to_name_slug(clean_text)
    if not raw_slug or not raw_slug[0].isalpha():
        raw_slug = f"e{raw_slug}"
    short_code = random.randint(100, 99999)
    pack_name = f"{raw_slug}_{short_code}_by_{BOT_USERNAME}"
    pack_title = f"{clean_text} ({font_info['name']})" if req.mode == "single" else f"{clean_text} Emojis"
    pack_link = f"https://t.me/addemoji/{pack_name}"

    try:
        # Step 1: Create new custom emoji sticker set with initial 10 stickers in ONE call
        initial_count = min(10, len(input_stickers))
        await bot.create_new_sticker_set(
            user_id=req.user_id,
            name=pack_name,
            title=pack_title,
            stickers=input_stickers[:initial_count],
            sticker_type="custom_emoji"
        )

        # Save to database immediately so it shows up everywhere
        save_user_pack(req.user_id, pack_name, pack_title)
        increment_user_packs(req.user_id)

        # Step 2: If more than 10 stickers, spawn background worker for the rest
        if len(input_stickers) > 10:
            bg_task = asyncio.create_task(
                background_add_stickers(
                    bot_instance=bot,
                    user_id=req.user_id,
                    pack_name=pack_name,
                    pack_title=pack_title,
                    pack_link=pack_link,
                    stickers_to_add=input_stickers[10:],
                    total_count=len(input_stickers),
                    clean_text=clean_text
                )
            )
            _background_tasks.add(bg_task)
            bg_task.add_done_callback(_background_tasks.discard)

        new_bal = get_user_balance(req.user_id)

        # Send notification message into Telegram chat
        try:
            markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Telegramga Qo'shish", url=pack_link)]
                ]
            )
            extra_txt = f"\n⏳ <i>Qolgan stikerlar orqa fonda to'liq yuklanmoqda...</i>" if len(input_stickers) > 5 else ""
            await bot.send_message(
                chat_id=req.user_id,
                text=(
                    f"🎉 <b>Tabriklaymiz! Yangi emoji to'plamingiz yaratildi!</b>\n\n"
                    f"✍️ <b>Matn:</b> <code>{clean_text}</code>\n"
                    f"🎨 <b>Shrift:</b> {font_info['name']}\n"
                    f"📦 <b>To'plam nomi:</b> <a href=\"{pack_link}\">{pack_title}</a>\n"
                    f"⚡ <b>Jami stikerlar:</b> {len(input_stickers)} ta\n"
                    f"💰 <b>Qolgan balansingiz:</b> {new_bal} ⭐ Stars\n\n"
                    f"<i>Pastdagi tugma orqali to'plamni Telegramga qo'shib olishingiz mumkin:</i>"
                ),
                reply_markup=markup,
                disable_web_page_preview=False
            )
        except Exception as msg_err:
            logger.info(f"Could not send telegram chat notification: {msg_err}")

        return {
            "ok": True,
            "pack_name": pack_name,
            "pack_title": pack_title,
            "pack_link": pack_link,
            "stickers_count": len(input_stickers),
            "remaining_balance": new_bal
        }

    except TelegramRetryAfter as e:
        if total_cost > 0:
            add_user_balance(req.user_id, total_cost, tx_type="refund", description="Telegram floodwait sababli qaytarildi")
        logger.warning(f"Telegram FloodWait: {e.retry_after}s")
        raise HTTPException(
            status_code=429,
            detail=f"Telegram serveri vaqtinchalik cheklov qo'ydi ({e.retry_after} soniya). Stars qaytarildi. Iltimos, birozdan so'ng urinib ko'ring."
        )
    except TelegramAPIError as api_err:
        if total_cost > 0:
            add_user_balance(req.user_id, total_cost, tx_type="refund", description="Telegram xatosi sababli qaytarildi")
        logger.error(f"Telegram API Error: {api_err}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Telegram API xatoligi: {getattr(api_err, 'message', str(api_err))}"
        )
    except Exception as e:
        if total_cost > 0:
            add_user_balance(req.user_id, total_cost, tx_type="refund", description="Xatolik sababli qaytarildi")
        logger.error(f"Generation unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Generatsiyada xatolik yuz berdi. Stars qaytarildi.")


@app.get("/api/user_packs")
async def get_user_packs_endpoint(user_id: int = Query(...)):
    """Retrieves user's created packs"""
    packs = get_user_packs(user_id)
    return {"packs": packs}


@app.post("/api/add_to_pack")
async def add_to_existing_pack_endpoint(req: AddToPackRequest):
    """Adds a single sticker to an existing user's custom emoji set"""
    bot = get_bot()
    font_info = FONTS_MAP.get(req.font, FONTS_MAP["stapel"])
    font_file_path = Path(FONTS_DIR) / font_info["file"]
    if not font_file_path.exists():
        font_file_path = Path(DEFAULT_FONT_PATH)

    tgs_name = req.template_id if req.template_id.endswith(".tgs") else f"{req.template_id}.tgs"
    tgs_path = Path(TEMPLATES_DIR) / tgs_name
    if not tgs_path.exists():
        tgs_path = next(Path(TEMPLATES_DIR).glob("*.tgs"))

    try:
        with open(tgs_path, "rb") as f:
            raw_bytes = f.read()

        proc_bytes = process_tgs_template(
            template_bytes=raw_bytes,
            text=req.text.strip().upper()[:16],
            font_path=str(font_file_path)
        )

        sticker_item = InputSticker(
            sticker=BufferedInputFile(proc_bytes, filename=f"emoji_add.tgs"),
            emoji_list=["⭐"],
            format="animated"
        )

        await bot.add_sticker_to_set(
            user_id=req.user_id,
            name=req.pack_name,
            sticker=sticker_item
        )

        pack_link = f"https://t.me/addemoji/{req.pack_name}"
        return {
            "ok": True,
            "pack_name": req.pack_name,
            "pack_link": pack_link
        }
    except Exception as e:
        logger.error(f"Add to pack error: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Paketga qo'shishda xatolik: {str(e)}")
