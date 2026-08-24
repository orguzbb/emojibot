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
from aiogram.types import InputSticker, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramRetryAfter, TelegramAPIError

from config import (
    BOT_TOKEN,
    BOT_USERNAME,
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
    get_user_packs
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
    mode: str = "single"  # "single", "selected", or "all"
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
async def serve_ticket_templates_js():
    return FileResponse(WEBAPP_DIR / "ticket_templates.js", media_type="application/javascript")


# ==================== API ENDPOINTS ====================

@app.get("/api/info")
async def get_app_info():
    """Bot and server metadata"""
    p = Path(TEMPLATES_DIR)
    tgs_count = len(list(p.glob("*.tgs"))) if p.exists() else 0
    return {
        "bot_username": BOT_USERNAME,
        "webapp_url": WEBAPP_URL,
        "templates_count": tgs_count,
        "fonts": FONTS_MAP
    }


@app.get("/api/templates")
async def list_templates():
    """Returns list of all available templates (1..117)"""
    p = Path(TEMPLATES_DIR)
    if not p.exists():
        return {"templates": []}

    tgs_files = sorted(
        p.glob("*.tgs"),
        key=lambda f: (int(f.stem) if f.stem.isdigit() else 9999, f.name)
    )

    templates = []
    for f in tgs_files:
        templates.append({
            "id": f.stem,
            "file": f.name,
            "name": f"Emoji #{f.stem}"
        })

    return {"templates": templates, "total": len(templates)}


@app.post("/api/preview")
async def generate_live_preview(req: PreviewRequest):
    """Processes template with text, font & scale and returns decompressed Lottie JSON for 60fps browser playback"""
    clean_text = req.text.strip().upper()[:16]
    if not clean_text:
        clean_text = "EMOJI"

    raw_bytes = get_template_bytes(req.template_id)
    if not raw_bytes:
        raw_bytes = get_template_bytes("1.tgs") or get_template_bytes("14.tgs")
    if not raw_bytes:
        raise HTTPException(status_code=404, detail="Shablon topilmadi")

    font_info = FONTS_MAP.get(req.font, FONTS_MAP["stapel"])
    font_file_path = Path(FONTS_DIR) / font_info["file"]
    if not font_file_path.exists():
        font_file_path = Path(DEFAULT_FONT_PATH)

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
        logger.error(f"Preview error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prevyu yaratishda xatolik: {str(e)}")


@app.post("/api/batch_preview")
async def generate_batch_previews(req: BatchPreviewRequest):
    """Generates Lottie JSON for multiple templates in one fast request"""
    clean_text = req.text.strip().upper()[:16]
    if not clean_text:
        clean_text = "EMOJI"

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


@app.post("/api/generate")
async def generate_emoji_pack(req: GenerateRequest):
    """Creates a single custom emoji, a selected set of emojis, or a full 117-pack in Telegram"""
    clean_text = req.text.strip().upper()[:16]
    if not clean_text:
        raise HTTPException(status_code=400, detail="Iltimos, matn kiriting")

    bot = get_bot()
    font_info = FONTS_MAP.get(req.font, FONTS_MAP["stapel"])
    font_file_path = Path(FONTS_DIR) / font_info["file"]
    if not font_file_path.exists():
        font_file_path = Path(DEFAULT_FONT_PATH)

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

    name_slug = to_name_slug(clean_text)
    short_code = random.randint(100, 9999)
    pack_name = f"{name_slug}_{short_code}_by_{BOT_USERNAME}"
    pack_title = f"{clean_text} ({font_info['name']})" if req.mode == "single" else f"{clean_text} Emojis"

    try:
        # Step 1: Create new custom emoji sticker set with initial sticker
        await bot.create_new_sticker_set(
            user_id=req.user_id,
            name=pack_name,
            title=pack_title,
            stickers=[input_stickers[0]],
            sticker_type="custom_emoji"
        )

        # Step 2: Add remaining stickers if full pack or multiple
        if len(input_stickers) > 1:
            for idx in range(1, len(input_stickers)):
                try:
                    await bot.add_sticker_to_set(
                        user_id=req.user_id,
                        name=pack_name,
                        sticker=input_stickers[idx]
                    )
                except TelegramRetryAfter as retry_err:
                    await asyncio.sleep(retry_err.retry_after + 0.5)
                    await bot.add_sticker_to_set(
                        user_id=req.user_id,
                        name=pack_name,
                        sticker=input_stickers[idx]
                    )
                except Exception as add_err:
                    logger.warning(f"Add sticker {idx+1} warning: {add_err}")
                await asyncio.sleep(0.04)

        # Save to database
        save_user_pack(req.user_id, pack_name, pack_title)
        increment_user_packs(req.user_id)

        pack_link = f"https://t.me/addemoji/{pack_name}"

        # Send notification message into Telegram chat
        try:
            markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Telegramga Qo'shish", url=pack_link)]
                ]
            )
            await bot.send_message(
                chat_id=req.user_id,
                text=(
                    f"🎉 <b>Tabriklaymiz! Yangi emoji to'plamingiz tayyor!</b>\n\n"
                    f"✍️ <b>Matn:</b> <code>{clean_text}</code>\n"
                    f"🎨 <b>Shrift:</b> {font_info['name']}\n"
                    f"📦 <b>To'plam nomi:</b> <a href=\"{pack_link}\">{pack_title}</a>\n"
                    f"⚡ <b>Jami stikerlar:</b> {len(input_stickers)} ta\n\n"
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
            "stickers_count": len(input_stickers)
        }

    except TelegramRetryAfter as e:
        logger.warning(f"Telegram FloodWait: {e.retry_after}s")
        raise HTTPException(
            status_code=429,
            detail=f"Telegram serveri floodwait qo'ydi ({e.retry_after} soniya). Iltimos, birozdan so'ng urinib ko'ring."
        )
    except TelegramAPIError as api_err:
        logger.error(f"Telegram API Error: {api_err}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Telegram API xatoligi: {str(api_err)}")
    except Exception as e:
        logger.error(f"Generate error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Xatolik: {str(e)}")


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
