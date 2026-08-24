# 🚀 Serverda (xs134.xuss.us) Bot va Mini Appni Ishga Tushirish Bo'yicha To'liq Qo'llanma

Ushbu qo'llanma orqali siz **GnEmoji Telegram Bot** va **Telegram Mini App**-ni o'zingizning Linux VPS (Ubuntu/Debian) serveringizda `https://xs134.xuss.us` domeni ostida 24/7 uzluksiz ishlaydigan qilib sozlashingiz mumkin.

---

## 📋 1-Qadam: Serverga Bog'lanish va Tizimni Yangilash

Terminal (SSH) orqali serveringizga kiring:

```bash
ssh root@xs134.xuss.us
# yoki
ssh root@SERVER_IP_MANZILINGIZ
```

Kerakli paketlarni o'rnating:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl
```

---

## 📁 2-Qadam: Loyiha Fayllarini Serverga Joylashtirish

Loyihani serverdagi `/var/www/gn_emoji` papkasiga joylashtiramiz:

```bash
sudo mkdir -p /var/www/gn_emoji
sudo chown -R $USER:$USER /var/www/gn_emoji
cd /var/www/gn_emoji
```

> **Eslatma:** Kompyuteringizdagi barcha loyiha fayllarini (shu jumladan `shablonlar/`, `fonts/`, `webapp/`, `bot.py`, `server.py`, `main.py`, `requirements.txt` va boshqalarni) SFTP, FileZilla yoki Git orqali `/var/www/gn_emoji` papkasiga yuklang.

---

## 🐍 3-Qadam: Python Virtual Muhitini Sozlash va Kutubxonalarni O'rnatish

Loyiha papkasida:

```bash
cd /var/www/gn_emoji

# Virtual muhit yaratish
python3 -m venv venv

# Virtual muhitni faollashtirish
source venv/bin/activate

# Kutubxonalarni o'rnatish
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🌐 4-Qadam: Nginx Web Serverni Sozlash (xs134.xuss.us)

FastAPI web serverimiz server ichida `127.0.0.1:8080` portida ishlaydi. Nginx esa `xs134.xuss.us` dan kelgan so'rovlarni unga yo'naltiradi (Reverse Proxy).

Yangi Nginx konfiguratsiya faylini ochamiz:

```bash
sudo nano /etc/nginx/sites-available/xs134.xuss.us
```

Ichiga quyidagi konfiguratsiyani nusxalab qo'ying:

```nginx
server {
    server_name xs134.xuss.us;

    # Katta hajmdagi stikerlar va animatsiyalar uchun
    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout sozlamalari
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

Faylni saqlang (`Ctrl + O`, `Enter`, `Ctrl + X`).

Konfiguratsiyani faollashtiring va Nginx-ni tekshiring:

```bash
sudo ln -s /etc/nginx/sites-available/xs134.xuss.us /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 5-Qadam: Bepul SSL (HTTPS) Sertifikat Olish

> **MUHIM:** Telegram Mini App faqat **HTTPS** (xavfsiz protokol) orqali ishlaydi.

`Certbot` orqali bepul Let's Encrypt SSL sertifikatini o'rnating:

```bash
sudo certbot --nginx -d xs134.xuss.us
```

Sizdan email so'raydi, email kiritib `Y` ni bosing. Certbot avtomatik ravishda SSL sertifikatni o'rnatib Nginx-ni sozlaydi.

---

## ⚙️ 6-Qadam: Systemd Service Yaratish (24/7 Uzluksiz Ishlash)

Server qayta yoqilganda yoki xatolik yuz berganda dastur avtomatik o'zi qayta yonishi uchun `systemd` xizmati yaratamiz:

```bash
sudo nano /etc/systemd/system/gn_emoji.service
```

Quyidagi matnni qo'ying:

```ini
[Unit]
Description=GnEmoji Bot & Mini App Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/gn_emoji
ExecStart=/var/www/gn_emoji/venv/bin/python3 /var/www/gn_emoji/main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Saqlang (`Ctrl + O`, `Enter`, `Ctrl + X`).

Xizmatni yoqing va ishga tushiring:

```bash
# Systemd ni yangilash
sudo systemctl daemon-reload

# Avtomatik yonishga qo'shish
sudo systemctl enable gn_emoji

# Xizmatni ishga tushirish
sudo systemctl start gn_emoji

# Statusini tekshirish
sudo systemctl status gn_emoji
```

Agar yashil rangda `Active: active (running)` ko'rinsa — dastur muvaffaqiyatli ishga tushdi!

---

## 🤖 7-Qadam: BotFather da Mini App Tugmasini Sozlash

1. Telegramda [@BotFather](https://t.me/BotFather) botiga kiring.
2. `/mybots` buyrug'ini yuboring va o'zingizning botingizni tanlang (`@GnEmojiBot`).
3. **Bot Settings** bo'limiga kiring.
4. **Menu Button** -> **Configure menu button** tugmasini bosing.
5. URL manzilini yuboring:
   ```text
   https://xs134.xuss.us
   ```
6. Tugma nomini yuboring:
   ```text
   📱 Mini App
   ```

*(Ixtiyoriy: To'g'ridan-to'g'ri Mini App yaratish uchun BotFather da `/newapp` buyrug'ini berib, o'z botingizni tanlab, nom va rasmlar yuklab `https://t.me/GnEmojiBot/app` formatidagi qisqa havolaga ham ega bo'lishingiz mumkin).*

---

## 📊 8-Qadam: Foydali Buyruqlar (Xizmatni Boshqarish)

- **Loglarni jonli ko'rish:**
  ```bash
  journalctl -u gn_emoji -f
  ```
- **Xizmatni qayta ishga tushirish (restart):**
  ```bash
  sudo systemctl restart gn_emoji
  ```
- **Xizmatni to'xtatish:**
  ```bash
  sudo systemctl stop gn_emoji
  ```
- **Xizmatni yoqish:**
  ```bash
  sudo systemctl start gn_emoji
  ```

---

## ✅ Hammasi Tayyor!
Endi har qanday foydalanuvchi botingizga kirganda yoki `https://xs134.xuss.us` manzilini ochganda, zamonaviy **GnEmoji Studio Mini App** orqali ism yozib, **100x100 Ticket** yoki **Logo Mega Pack** animatsiyali emojilarini bemalol yarata oladi! 🎉
