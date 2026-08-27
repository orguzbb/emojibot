#!/bin/bash
set -e

echo "=== GnEmoji Bot Yangilanmoqda ==="
cd "$(dirname "$0")"

# 1. Eski jarayonlarni to'xtatish
killall -9 python3 2>/dev/null || kill -9 $(ps -u $USER -o pid,comm | grep python | awk '{print $1}') 2>/dev/null || true

# 2. Gitdan oxirgi kodni olish
git pull origin main

# 3. WebApp fayllarini nusxalash
if [ -d "$HOME/www/xs134.xuss.us" ]; then
    cp -a webapp/. "$HOME/www/xs134.xuss.us/"
    echo "✅ WebApp fayllari yangilandi."
fi

# 4. Bog'liqliklarni tekshirish
pip3 install -r requirements.txt --quiet 2>/dev/null || true

# 5. Botni ishga tushirish
echo "🚀 Bot va Server ishga tushirilmoqda..."
nohup python3 main.py > bot.log 2>&1 &
sleep 3

# 6. Loglarni tekshirish
echo "=== Bot Loglari ==="
cat bot.log

echo ""
echo "✅ Tayyor! Bot hozir ishlamoqda."
