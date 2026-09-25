#!/bin/bash

echo "=== GnEmoji Bot Yangilanmoqda ==="
cd "$(dirname "$0")"

# 1. Eski jarayonlarni to'xtatish va port 8085 ni tozalash
echo "🛑 Eski barcha python jarayonlari to'xtatilmoqda..."
for pid in $(ps -u $USER -o pid,args | grep -E "python.*main.py|python3" | grep -v grep | awk '{print $1}'); do
    kill -9 $pid 2>/dev/null || true
done
killall -9 python3 2>/dev/null || true
pkill -9 -f "main.py" 2>/dev/null || true
fuser -k 8085/tcp 2>/dev/null || true
sleep 2

# 2. Gitdan oxirgi kodni olish (aniq sinxronizatsiya)
echo "📥 Gitdan yangilanishlar olinmoqda..."
git fetch origin main || true
git reset --hard origin/main || true

# 3. WebApp fayllarini nusxalash
if [ -d "$HOME/www/xs134.xuss.us" ]; then
    cp -a webapp/. "$HOME/www/xs134.xuss.us/"
    echo "✅ WebApp fayllari nusxalandi ($HOME/www/xs134.xuss.us)."
fi

# 4. Bog'liqliklarni o'rnatish
echo "📦 Kutubxonalar o'rnatilmoqda..."
pip3 install -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt --break-system-packages 2>/dev/null || true

# 5. Botni ishga tushirish
echo "🚀 Bot va Server ishga tushirilmoqda..."
nohup python3 main.py > bot.log 2>&1 &
sleep 3

# 6. Holatni tekshirish
echo "=== Bot Holati va Loglar ==="
if ps aux | grep -v grep | grep -q "main.py"; then
    echo "✅ Bot jarayoni muvaffaqiyatli ishga tushdi va ishlamoqda!"
else
    echo "⚠️ DIQQAT: Bot jarayoni to'xtab qoldi! Oxirgi loglar:"
fi
tail -n 25 bot.log

echo ""
echo "=== Tugadi ==="
