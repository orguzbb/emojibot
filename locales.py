# ==============================================================================
# COPYRIGHT NOTICE & LICENSE AGREEMENT (C) 2026 GN STUDIO
# Project: GnEmoji Studio — Telegram Bot Localization (UZ, RU, EN)
# All Rights Reserved.
# ==============================================================================

from typing import Dict, Any

LANGUAGES = {
    "uz": "🇺🇿 O'zbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English"
}

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # --- GREETINGS & START ---
    "start_greeting": {
        "uz": (
            "👋 <b>Assalomu alaykum, {name}!</b>\n\n"
            "🔥 <b>GnEmoji Studio</b> ga xush kelibsiz!\n"
            "Bu bot orqali siz o'z ismingiz, so'z yoki logotipingizdan iborat "
            "<b>eksklyuziv animatsiyali Telegram emoji to'plamlarini</b> yaratishingiz mumkin! 🚀\n\n"
            "👇 <i>Quyidagi menyudan kerakli bo'limni tanlang:</i>"
        ),
        "ru": (
            "👋 <b>Здравствуйте, {name}!</b>\n\n"
            "🔥 Добро пожаловать в <b>GnEmoji Studio</b>!\n"
            "С помощью этого бота вы можете создавать <b>эксклюзивные анимированные Telegram эмодзи</b> "
            "со своим именем, словом или логотипом! 🚀\n\n"
            "👇 <i>Выберите нужный раздел из меню ниже:</i>"
        ),
        "en": (
            "👋 <b>Hello, {name}!</b>\n\n"
            "🔥 Welcome to <b>GnEmoji Studio</b>!\n"
            "Create <b>exclusive animated Telegram custom emoji sets</b> with your name, "
            "text, or vector logo in seconds! 🚀\n\n"
            "👇 <i>Choose an option from the menu below:</i>"
        )
    },

    # --- MAIN MENU BUTTONS ---
    "btn_create_emoji": {
        "uz": "✨ Yangi Emoji yaratish",
        "ru": "✨ Создать эмодзи",
        "en": "✨ Create Emoji"
    },
    "btn_wallet": {
        "uz": "💳 Hamyon & Balans",
        "ru": "💳 Кошелек и Баланс",
        "en": "💳 Wallet & Balance"
    },
    "btn_my_packs": {
        "uz": "📦 Mening Paketlarim",
        "ru": "📦 Мои Пакеты",
        "en": "📦 My Packs"
    },
    "btn_referral": {
        "uz": "👥 Do'stlarni taklif qilish",
        "ru": "👥 Пригласить друзей",
        "en": "👥 Invite Friends"
    },
    "btn_daily_bonus": {
        "uz": "🎁 Kunlik Bonus (3 ⭐)",
        "ru": "🎁 Ежедневный бонус (3 ⭐)",
        "en": "🎁 Daily Bonus (3 ⭐)"
    },
    "btn_language": {
        "uz": "🌐 Til / Язык / Lang",
        "ru": "🌐 Язык / Til / Lang",
        "en": "🌐 Language / Til / Язык"
    },
    "btn_open_miniapp": {
        "uz": "📱 Mini Appni ochish",
        "ru": "📱 Открыть Mini App",
        "en": "📱 Open Mini App"
    },
    "btn_support": {
        "uz": "🆘 Qo'llab-quvvatlash",
        "ru": "🆘 Поддержка",
        "en": "🆘 Support"
    },
    "btn_main_menu": {
        "uz": "🏠 Asosiy menyu",
        "ru": "🏠 Главное меню",
        "en": "🏠 Main Menu"
    },
    "btn_back": {
        "uz": "◀️ Orqaga",
        "ru": "◀️ Назад",
        "en": "◀️ Back"
    },

    # --- LANGUAGE SELECTOR ---
    "lang_prompt": {
        "uz": "🌐 <b>Muloqot tilini tanlang:</b>\n<i>Iltimos, o'zingizga qulay tilni tanlang:</i>",
        "ru": "🌐 <b>Выберите язык интерфейса:</b>\n<i>Пожалуйста, выберите удобный для вас язык:</i>",
        "en": "🌐 <b>Select your interface language:</b>\n<i>Please choose your preferred language:</i>"
    },
    "lang_changed": {
        "uz": "✅ <b>Til muvaffaqiyatli O'zbekchaga o'zgartirildi!</b> 🇺🇿",
        "ru": "✅ <b>Язык успешно изменен на Русский!</b> 🇷🇺",
        "en": "✅ <b>Language successfully changed to English!</b> 🇬🇧"
    },

    # --- DAILY BONUS ---
    "daily_bonus_success": {
        "uz": (
            "🎉 <b>TABRIKLAYMIZ! KUNLIK BONUS QABUL QILINDI!</b> 🎁\n\n"
            "⭐️ <b>Berilgan Stars:</b> <b>+{stars} ⭐</b>\n"
            "💰 <b>Joriy balansingiz:</b> <b>{balance} ⭐️ Stars</b>\n\n"
            "<i>Har 24 soatda botga kiring va bepul Stars bonusini oling!</i>"
        ),
        "ru": (
            "🎉 <b>ПОЗДРАВЛЯЕМ! ЕЖЕДНЕВНЫЙ БОНУС ПОЛУЧЕН!</b> 🎁\n\n"
            "⭐️ <b>Начислено:</b> <b>+{stars} ⭐ Stars</b>\n"
            "💰 <b>Ваш баланс:</b> <b>{balance} ⭐️ Stars</b>\n\n"
            "<i>Заходите каждый день и получайте бесплатные Stars!</i>"
        ),
        "en": (
            "🎉 <b>CONGRATULATIONS! DAILY BONUS CLAIMED!</b> 🎁\n\n"
            "⭐️ <b>Rewarded:</b> <b>+{stars} ⭐ Stars</b>\n"
            "💰 <b>Your balance:</b> <b>{balance} ⭐️ Stars</b>\n\n"
            "<i>Come back every 24 hours to claim your free Stars!</i>"
        )
    },
    "daily_bonus_cooldown": {
        "uz": (
            "⏳ <b>Siz bugungi bonusni allaqachon olgansiz!</b>\n\n"
            "Keyingi bonus <b>{hours} soat {minutes} daqiqa</b>dan so'ng mavjud bo'ladi.\n"
            "💰 Hozirgi balansingiz: <b>{balance} ⭐ Stars</b>"
        ),
        "ru": (
            "⏳ <b>Вы уже получили бонус за сегодня!</b>\n\n"
            "Следующий бонус будет доступен через <b>{hours} ч. {minutes} мин.</b>\n"
            "💰 Текущий баланс: <b>{balance} ⭐ Stars</b>"
        ),
        "en": (
            "⏳ <b>You have already claimed today's bonus!</b>\n\n"
            "Next bonus available in <b>{hours}h {minutes}m</b>.\n"
            "💰 Current balance: <b>{balance} ⭐ Stars</b>"
        )
    },

    # --- WALLET & BALANCE ---
    "wallet_info": {
        "uz": (
            "💳 <b>Sizning Hamyoningiz</b>\n\n"
            "🆔 Foydalanuvchi ID: <code>{user_id}</code>\n"
            "💰 Balansingiz: <b>{balance} ⭐️ Stars</b>\n"
            "📦 Yaratilgan paketlar: <b>{packs_count} ta</b>\n"
            "👥 Taklif qilgan do'stlaringiz: <b>{ref_count} ta</b>\n\n"
            "<i>Stars orqali istalgan shaxsiy emoji to'plamini yaratishingiz mumkin!</i>"
        ),
        "ru": (
            "💳 <b>Ваш Кошелек</b>\n\n"
            "🆔 ID пользователя: <code>{user_id}</code>\n"
            "💰 Баланс: <b>{balance} ⭐️ Stars</b>\n"
            "📦 Создано пакетов: <b>{packs_count}</b>\n"
            "👥 Приглашено друзей: <b>{ref_count}</b>\n\n"
            "<i>Используйте Stars для создания любых анимированных эмодзи!</i>"
        ),
        "en": (
            "💳 <b>Your Wallet</b>\n\n"
            "🆔 User ID: <code>{user_id}</code>\n"
            "💰 Balance: <b>{balance} ⭐️ Stars</b>\n"
            "📦 Packs Created: <b>{packs_count}</b>\n"
            "👥 Friends Invited: <b>{ref_count}</b>\n\n"
            "<i>Use Stars to craft any custom animated emoji set!</i>"
        )
    },

    # --- REFERRAL SYSTEM ---
    "referral_info": {
        "uz": (
            "👥 <b>Do'stlarni Taklif Qilish (Referral Dasturi)</b>\n\n"
            "Do'stlaringizni botga taklif qiling va har bir yangi do'stingiz uchun "
            "<b>+{bonus} ⭐️ Stars</b> oling!\n\n"
            "🔗 <b>Sizning taklif havolangiz:</b>\n"
            "<code>https://t.me/{bot_username}?start={user_id}</code>\n\n"
            "📊 <b>Statistikangiz:</b>\n"
            "• Taklif qilingan do'stlar: <b>{total_refs} ta</b>\n"
            "• Ishlab olingan Stars: <b>{earned} ⭐️</b>"
        ),
        "ru": (
            "👥 <b>Реферальная Программа (Пригласи друзей)</b>\n\n"
            "Приглашайте друзей в бота и получайте <b>+{bonus} ⭐️ Stars</b> "
            "за каждого приглашенного пользователя!\n\n"
            "🔗 <b>Ваша реферальная ссылка:</b>\n"
            "<code>https://t.me/{bot_username}?start={user_id}</code>\n\n"
            "📊 <b>Ваша статистика:</b>\n"
            "• Приглашено друзей: <b>{total_refs}</b>\n"
            "• Заработано Stars: <b>{earned} ⭐️</b>"
        ),
        "en": (
            "👥 <b>Referral Program (Invite Friends)</b>\n\n"
            "Invite friends to the bot and receive <b>+{bonus} ⭐️ Stars</b> "
            "for each invited user!\n\n"
            "🔗 <b>Your invite link:</b>\n"
            "<code>https://t.me/{bot_username}?start={user_id}</code>\n\n"
            "📊 <b>Your stats:</b>\n"
            "• Invited users: <b>{total_refs}</b>\n"
            "• Total earned: <b>{earned} ⭐️ Stars</b>"
        )
    },

    # --- CHEKS (PROMO STARS) ---
    "chek_not_found": {
        "uz": "❌ <b>Bunday chek topilmadi yoki u o'chirilgan.</b>",
        "ru": "❌ <b>Чек не найден или был удален.</b>",
        "en": "❌ <b>Chek not found or has been deleted.</b>"
    },
    "chek_already_claimed": {
        "uz": (
            "⚠️ <b>Siz ushbu chekni allaqachon faollashtirgansiz!</b>\n\n"
            "ℹ️ <i>Har bir foydalanuvchi ushbu chekdan faqat 1 marta foydalana oladi.</i>"
        ),
        "ru": (
            "⚠️ <b>Вы уже активировали этот чек ранее!</b>\n\n"
            "ℹ️ <i>Каждый пользователь может использовать чек только 1 раз.</i>"
        ),
        "en": (
            "⚠️ <b>You have already claimed this voucher!</b>\n\n"
            "ℹ️ <i>Each user can claim each voucher only once.</i>"
        )
    },
    "chek_exhausted": {
        "uz": (
            "❌ <b>Kechirasiz, ushbu chekning barcha nusxalari tugagan!</b>\n\n"
            "Keyingi sovg'a va cheklarni o'tkazib yubormaslik uchun kanalimizni kuzatib boring!"
        ),
        "ru": (
            "❌ <b>К сожалению, лимит активаций этого чека исчерпан!</b>\n\n"
            "Следите за нашим каналом, чтобы не пропустить следующие акции!"
        ),
        "en": (
            "❌ <b>Sorry, all activations for this voucher have been claimed!</b>\n\n"
            "Follow our channel to catch upcoming giveaways and vouchers!"
        )
    },
    "chek_sub_required": {
        "uz": (
            "🎁 <b>{amount} Stars uchun chek topildi! ⭐️</b>\n\n"
            "⚠️ Chekni faollashtirish va balansingizga <b>+{amount} ⭐</b> olish uchun avval homiy kanalimizga a'zo bo'lishingiz lozim.\n\n"
            "Kanalga a'zo bo'lgach, pastdagi <b>«✅ A'zo bo'ldim (Tekshirish)»</b> tugmasini bosing:"
        ),
        "ru": (
            "🎁 <b>Найден чек на {amount} Stars! ⭐️</b>\n\n"
            "⚠️ Чтобы активировать чек и получить <b>+{amount} ⭐</b>, сначала подпишитесь на наш канал.\n\n"
            "После подписки нажмите кнопку <b>«✅ Я подписался (Проверить)»</b>:"
        ),
        "en": (
            "🎁 <b>Voucher found for {amount} Stars! ⭐️</b>\n\n"
            "⚠️ To claim this voucher and receive <b>+{amount} ⭐</b>, please subscribe to our channel first.\n\n"
            "Once subscribed, click <b>«✅ Joined (Verify)»</b> below:"
        )
    },
    "chek_success": {
        "uz": (
            "🎉 <b>TABRIKLAYMIZ! CHEK FAOLLASHTIRILDI!</b> 🎁\n\n"
            "⭐️ <b>Qo'shilgan Stars:</b> <b>+{amount} ⭐</b>\n"
            "💰 <b>Joriy balansingiz:</b> <b>{balance} ⭐️ Stars</b>\n\n"
            "<i>Siz ushbu Stars'lardan botdagi har qanday shaxsiy emoji to'plamlarini yaratishda foydalanishingiz mumkin!</i>"
        ),
        "ru": (
            "🎉 <b>ПОЗДРАВЛЯЕМ! ЧЕК УСПЕШНО АКТИВИРОВАН!</b> 🎁\n\n"
            "⭐️ <b>Начислено:</b> <b>+{amount} ⭐ Stars</b>\n"
            "💰 <b>Ваш баланс:</b> <b>{balance} ⭐️ Stars</b>\n\n"
            "<i>Вы можете использовать эти Stars для создания персональных наборов эмодзи!</i>"
        ),
        "en": (
            "🎉 <b>CONGRATULATIONS! VOUCHER ACTIVATED!</b> 🎁\n\n"
            "⭐️ <b>Added Stars:</b> <b>+{amount} ⭐ Stars</b>\n"
            "💰 <b>Your balance:</b> <b>{balance} ⭐️ Stars</b>\n\n"
            "<i>You can use these Stars to craft custom emoji packs right away!</i>"
        )
    },
    "btn_sub_channel": {
        "uz": "📢 Kanalga a'zo bo'lish",
        "ru": "📢 Подписаться на канал",
        "en": "📢 Subscribe to Channel"
    },
    "btn_sub_verify": {
        "uz": "✅ A'zo bo'ldim (Tekshirish)",
        "ru": "✅ Я подписался (Проверить)",
        "en": "✅ Joined (Verify)"
    }
}


def t(key: str, lang: str = "uz", **kwargs) -> str:
    """
    Translates a key into the specified language ('uz', 'ru', 'en').
    Defaults to 'uz' if key or language is not found.
    Interpolates kwargs into template string.
    """
    if lang not in ("uz", "ru", "en"):
        lang = "uz"

    entry = TRANSLATIONS.get(key)
    if not entry:
        return key

    text = entry.get(lang) or entry.get("uz") or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
