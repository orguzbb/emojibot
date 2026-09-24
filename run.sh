#!/bin/bash

echo "=== GnEmoji Bot Yangilanmoqda ==="
cd "$(dirname "$0")"

# 1. Python muhitini aniqlash (venv yoki tizim)
PYTHON_CMD="python3"
if [ -d "venv" ] && [ -f "venv/bin/python3" ]; then
    PYTHON_CMD="venv/bin/python3"
    echo "Using venv Python: $PYTHON_CMD"
elif [ -d ".venv" ] && [ -f ".venv/bin/python3" ]; then
    PYTHON_CMD=".venv/bin/python3"
    echo "Using .venv Python: $PYTHON_CMD"
fi

# 2. Eski jarayonlarni to'xtatish va port 8000 ni tozalash
echo "🛑 Eski jarayonlar to'xtatilmoqda..."
pkill -9 -f "main.py" 2>/dev/null || true
fuser -k 8000/tcp 2>/dev/null || true
sleep 1

# 3. Gitdan oxirgi kodni olish (aniq sinxronizatsiya)
echo "📥 Gitdan yangilanishlar olinmoqda..."
git fetch origin main || true
git reset --hard origin/main || true

# 4. WebApp fayllarini nusxalash
if [ -d "$HOME/www/xs134.xuss.us" ]; then
    cp -a webapp/. "$HOME/www/xs134.xuss.us/"
    echo "✅ WebApp fayllari nusxalandi ($HOME/www/xs134.xuss.us)."
fi

# 5. Bog'liqliklarni tekshirish va o'rnatish
echo "📦 Kutubxonalar o'rnatilmoqda..."
if [ -f "venv/bin/pip" ]; then
    venv/bin/pip install -r requirements.txt
elif [ -f ".venv/bin/pip" ]; then
    .venv/bin/pip install -r requirements.txt
else
    $PYTHON_CMD -m pip install -r requirements.txt || pip3 install -r requirements.txt || true
fi

# 6. Botni ishga tushirish
echo "🚀 Bot va Server ishga tushirilmoqda..."
nohup $PYTHON_CMD main.py > bot.log 2>&1 &
sleep 3

# 7. Holatni tekshirish
echo "=== Bot Holati va Loglar ==="
if ps aux | grep -v grep | grep -q "main.py"; then
    echo "✅ Bot jarayoni muvaffaqiyatli ishga tushdi va ishlamoqda!"
else
    echo "⚠️ DIQQAT: Bot jarayoni to'xtab qoldi! Oxirgi loglar:"
fi
tail -n 25 bot.log

echo ""
echo "=== Tugadi ==="
