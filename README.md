# Telegram Premium Animated Emoji Pack Bot (@BepulEmojiBot)

Ushbu bot foydalanuvchi yuborgan ism yoki matn asosida `shablonlar/` papkasidagi barcha `.tgs` (Lottie) animatsiyalarni tahrirlab, Telegram Premium uchun maxsus animatsiyali emoji pack yaratib beradi.

## Xususiyatlari:
1. **Lottie / TGS Vektor Tahrirlash**:
   - `fonts/stapel.ttf` shrifti orqali harflarni to'g'ridan-to'g'ri Lottie vektor egri chiziqlariga (Bézier paths) o'giradi.
   - Har bir harf alohida guruh va shakl sifatida joylanadi.
   - Harf o'lchamlari va oraliqlari avtomatik hisoblanib, markazlashtiriladi.
2. **Rang va 3D Soya Saqlanishi**:
   - Shablonning old qatlam rangi (Fill) va orqa soya qatlam rangi (Shadow Fill) avtomatik olinadi va yangi harflarga qo'llanadi.
3. **Avtomatik Telegram Premium Emoji Pack**:
   - Telegram Bot API orqali `custom_emoji` to'plami yaratiladi.
   - Foydalanuvchiga `https://t.me/addemoji/<pack_name>` havolasi taqdim etiladi.
4. **Moslashuvchanlik**:
   - `shablonlar/` papkasiga istalgancha yangi `.tgs` shablonlar qo'shish mumkin.

## O'rnatish va Ishga Tushirish:

```bash
# 1. Kutubxonalarni o'rnatish
pip install -r requirements.txt

# 2. Botni ishga tushirish
python bot.py
```
