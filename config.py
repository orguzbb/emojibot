import os
from pathlib import Path

BOT_TOKEN = "8957385356:AAHGgiKASWPZ67TnTl658yTlDZ9YxB9f408"
BOT_USERNAME = "GnEmojiBot"

ADMIN_IDS = [1323217434]

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "shablonlar"
FONTS_DIR = BASE_DIR / "fonts"
DEFAULT_FONT_PATH = FONTS_DIR / "stapel.ttf"

WEBAPP_URL = "https://xs134.xuss.us/?v=7.4.0"
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

CHANNEL_ID = -1003900982155
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/gnemoji")
CHANNEL_USERNAME = "gnemoji"

