import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple, Any, Union

DB_PATH = Path(__file__).resolve().parent / "bot_database.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            balance INTEGER DEFAULT 0,
            referred_by INTEGER DEFAULT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            packs_created INTEGER DEFAULT 0
        )
    """)

    # Check & migrate users table columns if missing
    cursor.execute("PRAGMA table_info(users)")
    columns = [row["name"] for row in cursor.fetchall()]
    if "balance" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN balance INTEGER DEFAULT 0")
    if "referred_by" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN referred_by INTEGER DEFAULT NULL")
    if "language_code" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN language_code TEXT DEFAULT 'uz'")
    if "last_daily_bonus" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN last_daily_bonus TIMESTAMP DEFAULT NULL")

    # 2. User packs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_packs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            pack_name TEXT UNIQUE,
            pack_title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Bot Settings table (for emoji price, referral bonus, etc.)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Set default settings if not exist
    cursor.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('emoji_price', '5')")
    cursor.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('referral_bonus', '10')")

    # 4. Promocodes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS promocodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            reward_amount INTEGER NOT NULL,
            max_uses INTEGER DEFAULT 100,
            used_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 5. Promocode Usages table (One use per user)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS promocode_usages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            promo_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(promo_id, user_id),
            FOREIGN KEY (promo_id) REFERENCES promocodes (id) ON DELETE CASCADE
        )
    """)

    # 6. Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 7. Pending orders table (stores full customization parameters for Stars purchases)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_orders (
            order_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            order_data TEXT NOT NULL,
            total_cost INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 8. Cheks table (Channel stars vouchers)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cheks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            amount INTEGER NOT NULL,
            total_count INTEGER NOT NULL,
            remaining_count INTEGER NOT NULL,
            channel_id INTEGER,
            channel_username TEXT,
            message_id INTEGER,
            created_by INTEGER NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 9. Chek Usages table (One use per user per chek)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chek_usages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chek_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(chek_id, user_id),
            FOREIGN KEY (chek_id) REFERENCES cheks (id) ON DELETE CASCADE
        )
    """)

    # 10. Broadcast Exclusions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS broadcast_exclusions (
            user_id INTEGER PRIMARY KEY,
            reason TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_pending_order(order_id: str, user_id: int, order_data: dict, total_cost: int):
    """Saves pending order with all customization parameters (text_color, svg_data, templates, etc.)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO pending_orders (order_id, user_id, order_data, total_cost)
        VALUES (?, ?, ?, ?)
    """, (order_id, user_id, json.dumps(order_data), total_cost))
    conn.commit()
    conn.close()


def get_pending_order(order_id: str) -> Optional[dict]:
    """Retrieves full order parameters by order_id"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT order_id, user_id, order_data, total_cost, created_at
        FROM pending_orders WHERE order_id = ?
    """, (order_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    try:
        data = json.loads(row["order_data"])
    except Exception:
        data = {}
    return {
        "order_id": row["order_id"],
        "user_id": row["user_id"],
        "order_data": data,
        "total_cost": row["total_cost"],
        "created_at": row["created_at"]
    }


def delete_pending_order(order_id: str):
    """Deletes a completed or cancelled pending order"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pending_orders WHERE order_id = ?", (order_id,))
    conn.commit()
    conn.close()


# ==================== USER MANAGEMENT ====================

def add_or_update_user(
    user_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    referred_by: Optional[int] = None
) -> Tuple[bool, Optional[int]]:
    """
    Adds a new user or updates an existing user.
    Returns (is_new_user, valid_referred_by_id_if_awarded)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, referred_by, packs_created FROM users WHERE user_id = ?", (user_id,))
    existing = cursor.fetchone()

    is_new = False
    awarded_referrer = None

    valid_ref = None
    if referred_by is not None:
        try:
            r_int = int(referred_by)
            if r_int != int(user_id):
                valid_ref = r_int
        except (ValueError, TypeError):
            valid_ref = None

    if existing is None:
        is_new = True
        if valid_ref:
            awarded_referrer = valid_ref

        cursor.execute("""
            INSERT INTO users (user_id, username, first_name, balance, referred_by)
            VALUES (?, ?, ?, 0, ?)
        """, (user_id, username, first_name, valid_ref))
    else:
        # If user exists but was never referred by anyone and hasn't created packs
        if (existing["referred_by"] is None or existing["referred_by"] == 0) and valid_ref and (existing["packs_created"] or 0) == 0:
            awarded_referrer = valid_ref
            cursor.execute("""
                UPDATE users SET
                    username = COALESCE(?, username),
                    first_name = COALESCE(?, first_name),
                    referred_by = ?
                WHERE user_id = ?
            """, (username, first_name, valid_ref, user_id))
        else:
            cursor.execute("""
                UPDATE users SET
                    username = COALESCE(?, username),
                    first_name = COALESCE(?, first_name)
                WHERE user_id = ?
            """, (username, first_name, user_id))

    conn.commit()
    conn.close()
    return (is_new, awarded_referrer)


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users_list(limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """Returns paginated list of users for admin panel"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, username, first_name, balance, packs_created, joined_at
        FROM users
        ORDER BY joined_at DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_balance(user_id: int) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row["balance"] is not None:
        return row["balance"]
    return 0


def add_user_balance(user_id: int, amount: int, tx_type: str = "deposit", description: str = "") -> int:
    """Adds stars to user balance and records transaction. Returns new balance."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ensure user exists
    cursor.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)", (user_id,))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    
    # Record transaction
    cursor.execute("""
        INSERT INTO transactions (user_id, amount, type, description)
        VALUES (?, ?, ?, ?)
    """, (user_id, amount, tx_type, description))

    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    new_balance = cursor.fetchone()["balance"]

    conn.commit()
    conn.close()
    return new_balance


def deduct_user_balance(user_id: int, amount: int, tx_type: str = "purchase", description: str = "") -> bool:
    """
    Deducts stars from user balance if sufficient.
    Returns True on success, False if balance is insufficient.
    """
    if amount <= 0:
        return True

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row or row["balance"] < amount:
        conn.close()
        return False

    cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
    cursor.execute("""
        INSERT INTO transactions (user_id, amount, type, description)
        VALUES (?, ?, ?, ?)
    """, (user_id, -amount, tx_type, description))

    conn.commit()
    conn.close()
    return True


def admin_set_user_balance(user_id: int, new_balance: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)", (user_id,))
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    cursor.execute("""
        INSERT INTO transactions (user_id, amount, type, description)
        VALUES (?, ?, 'admin_set', 'Admin tomonidan balans o`zgartirildi')
    """, (user_id, new_balance))
    conn.commit()
    conn.close()
    return True


# ==================== SETTINGS (PRICING & REFERRALS) ====================

def get_setting(key: str, default: str = "") -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM bot_settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["value"]
    return default


def set_setting(key: str, value: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bot_settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, str(value)))
    conn.commit()
    conn.close()


def get_emoji_price() -> int:
    try:
        val = get_setting("emoji_price", "5")
        return max(0, int(val))
    except (ValueError, TypeError):
        return 5


def set_emoji_price(price: int):
    set_setting("emoji_price", str(max(0, price)))


def get_referral_bonus() -> int:
    try:
        val = get_setting("referral_bonus", "10")
        return max(0, int(val))
    except (ValueError, TypeError):
        return 10


def set_referral_bonus(bonus: int):
    set_setting("referral_bonus", str(max(0, bonus)))


def get_referral_stats(user_id: int) -> Dict[str, int]:
    """Returns count of invited users and total bonus earned from referrals."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) AS ref_count FROM users WHERE referred_by = ?", (user_id,))
    ref_count = cursor.fetchone()["ref_count"]

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total_earned
        FROM transactions
        WHERE user_id = ? AND type = 'referral_bonus'
    """, (user_id,))
    total_earned = cursor.fetchone()["total_earned"]

    conn.close()
    return {
        "count": ref_count,
        "total_earned": total_earned
    }


# ==================== PROMOCODES ====================

def create_promocode(code: str, reward_amount: int, max_uses: int = 100) -> Tuple[bool, str]:
    code = code.strip().upper()
    if not code:
        return False, "Promokod bo'sh bo'lishi mumkin emas."
    if reward_amount <= 0:
        return False, "Mukofot miqdori 0 dan katta bo'lishi kerak."

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO promocodes (code, reward_amount, max_uses, used_count)
            VALUES (?, ?, ?, 0)
        """, (code, reward_amount, max_uses))
        conn.commit()
        conn.close()
        return True, "Promokod muvaffaqiyatli yaratildi!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Bu nomdagi promokod allaqachon mavjud."
    except Exception as e:
        conn.close()
        return False, f"Xatolik: {e}"


def get_all_promocodes() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM promocodes ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_promocode(code: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM promocodes WHERE code = ?", (code.strip().upper(),))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def use_promocode(user_id: int, raw_code: str) -> Tuple[bool, int, str]:
    """
    Validates and activates a promocode for a user.
    Returns (success, reward_amount, message).
    """
    code = raw_code.strip().upper()
    if not code:
        return False, 0, "Iltimos, promokodni kiriting."

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM promocodes WHERE code = ?", (code,))
    promo = cursor.fetchone()

    if not promo:
        conn.close()
        return False, 0, "Bunday promokod mavjud emas yoki muddati tugagan."

    promo_id = promo["id"]
    reward = promo["reward_amount"]
    max_uses = promo["max_uses"]
    used_count = promo["used_count"]

    if used_count >= max_uses:
        conn.close()
        return False, 0, "Ushbu promokoddan foydalanish limiti tugagan."

    # Check if user already used this promo
    cursor.execute("SELECT id FROM promocode_usages WHERE promo_id = ? AND user_id = ?", (promo_id, user_id))
    if cursor.fetchone():
        conn.close()
        return False, 0, "Siz ushbu promokoddan allaqachon foydalangansiz."

    try:
        # Record usage
        cursor.execute("INSERT INTO promocode_usages (promo_id, user_id) VALUES (?, ?)", (promo_id, user_id))
        cursor.execute("UPDATE promocodes SET used_count = used_count + 1 WHERE id = ?", (promo_id,))
        
        # Add balance to user
        cursor.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)", (user_id,))
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (reward, user_id))
        
        # Record transaction
        cursor.execute("""
            INSERT INTO transactions (user_id, amount, type, description)
            VALUES (?, ?, 'promocode', ?)
        """, (user_id, reward, f"Promokod faollashtirildi: {code}"))

        conn.commit()
        conn.close()
        return True, reward, f"Promokod faollashtirildi! Balansingizga +{reward} ⭐ Stars qo'shildi."
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, 0, f"Xatolik yuz berdi: {e}"


# ==================== STATS & MISC ====================

def increment_user_packs(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET packs_created = packs_created + 1 WHERE user_id = ?
    """, (user_id,))
    conn.commit()
    conn.close()


def save_user_pack(user_id: int, pack_name: str, pack_title: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO user_packs (user_id, pack_name, pack_title)
        VALUES (?, ?, ?)
    """, (user_id, pack_name, pack_title))
    conn.commit()
    conn.close()


def get_user_packs(user_id: int) -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pack_name, pack_title, created_at FROM user_packs
        WHERE user_id = ? ORDER BY id DESC LIMIT 15
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [tuple(r) for r in rows]


def get_all_user_ids() -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [r["user_id"] for r in rows]


def get_users_count() -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM users")
    count = cursor.fetchone()["total"]
    conn.close()
    return count


def get_stats_summary() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total_users FROM users")
    total_users = cursor.fetchone()["total_users"]

    cursor.execute("SELECT COALESCE(SUM(balance), 0) AS total_user_balance FROM users")
    total_user_balance = cursor.fetchone()["total_user_balance"]

    cursor.execute("SELECT COUNT(*) AS total_packs FROM user_packs")
    total_packs = cursor.fetchone()["total_packs"]

    cursor.execute("SELECT COUNT(*) AS total_promos, COALESCE(SUM(used_count), 0) AS total_promo_uses FROM promocodes")
    promo_data = cursor.fetchone()
    total_promos = promo_data["total_promos"]
    total_promo_uses = promo_data["total_promo_uses"]

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total_stars_deposited
        FROM transactions
        WHERE type = 'deposit_stars'
    """)
    total_stars_deposited = cursor.fetchone()["total_stars_deposited"]

    cursor.execute("""
        SELECT COUNT(*) AS ref_joined
        FROM users
        WHERE referred_by IS NOT NULL
    """)
    ref_joined = cursor.fetchone()["ref_joined"]

    conn.close()
    return {
        "total_users": total_users,
        "total_user_balance": total_user_balance,
        "total_packs": total_packs,
        "total_promos": total_promos,
        "total_promo_uses": total_promo_uses,
        "total_stars_deposited": total_stars_deposited,
        "ref_joined": ref_joined
    }


# ==================== CHEK (GIFT VOUCHER) SYSTEM ====================

def create_chek(
    code: str,
    amount: int,
    total_count: int,
    channel_id: Optional[int] = None,
    channel_username: Optional[str] = None,
    message_id: Optional[int] = None,
    created_by: int = 0
) -> int:
    """Creates a new chek and returns its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cheks (code, amount, total_count, remaining_count, channel_id, channel_username, message_id, created_by, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (code, amount, total_count, total_count, channel_id, channel_username, message_id, created_by))
    chek_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return chek_id


def update_chek_message_id(chek_id: int, message_id: int):
    """Updates the published telegram message_id of the chek."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE cheks SET message_id = ? WHERE id = ?", (message_id, chek_id))
    conn.commit()
    conn.close()


def get_chek(code: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cheks WHERE code = ?", (code,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_chek_by_id(chek_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cheks WHERE id = ?", (chek_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_cheks(limit: int = 25) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM cheks
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_chek(chek_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cheks WHERE id = ?", (chek_id,))
    cursor.execute("DELETE FROM chek_usages WHERE chek_id = ?", (chek_id,))
    conn.commit()
    conn.close()
    return True


def has_user_claimed_chek(chek_id: int, user_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM chek_usages WHERE chek_id = ? AND user_id = ?", (chek_id, user_id))
    row = cursor.fetchone()
    conn.close()
    return bool(row)


def claim_chek(code: str, user_id: int) -> Tuple[bool, int, str, Optional[Dict[str, Any]]]:
    """
    Atomically claims a chek for a user.
    Returns (success, amount, message, chek_data)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cheks WHERE code = ?", (code,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return False, 0, "Bunday chek topilmadi yoki o'chirilgan.", None

    chek = dict(row)
    chek_id = chek["id"]
    amount = chek["amount"]
    remaining = chek["remaining_count"]
    is_active = chek["is_active"]

    if not is_active or remaining <= 0:
        conn.close()
        return False, 0, "Kechirasiz, ushbu chekning barcha nusxalari tugagan!", chek

    # Check if user already claimed
    cursor.execute("SELECT id FROM chek_usages WHERE chek_id = ? AND user_id = ?", (chek_id, user_id))
    if cursor.fetchone():
        conn.close()
        return False, 0, "Siz ushbu chekni allaqachon faollashtirgansiz! (Chek faqat 1 marta ishlatiladi)", chek

    try:
        # Record usage
        cursor.execute("INSERT INTO chek_usages (chek_id, user_id) VALUES (?, ?)", (chek_id, user_id))

        # Decrement remaining
        new_remaining = remaining - 1
        new_active = 1 if new_remaining > 0 else 0
        cursor.execute("UPDATE cheks SET remaining_count = ?, is_active = ? WHERE id = ?", (new_remaining, new_active, chek_id))

        # Add balance to user
        cursor.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)", (user_id,))
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))

        # Record transaction
        cursor.execute("""
            INSERT INTO transactions (user_id, amount, type, description)
            VALUES (?, ?, 'chek', ?)
        """, (user_id, amount, f"Kanal cheki faollashtirildi: {code} (+{amount} Stars)"))

        cursor.execute("SELECT * FROM cheks WHERE id = ?", (chek_id,))
        updated_chek = dict(cursor.fetchone())

        conn.commit()
        conn.close()
        return True, amount, f"Chek muvaffaqiyatli faollashtirildi! Balansingizga +{amount} ⭐ Stars qo'shildi.", updated_chek
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, 0, f"Xatolik yuz berdi: {e}", None


# ==================== USER LANGUAGE (I18N) ====================

def get_user_language(user_id: int) -> str:
    """Returns the user's preferred language ('uz', 'ru', 'en'). Defaults to 'uz'."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT language_code FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row["language_code"]:
        lang = str(row["language_code"]).strip().lower()
        if lang in ("uz", "ru", "en"):
            return lang
    return "uz"


def set_user_language(user_id: int, lang: str) -> bool:
    """Updates the user's language preference."""
    if lang not in ("uz", "ru", "en"):
        lang = "uz"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, language_code) VALUES (?, ?)", (user_id, lang))
    cursor.execute("UPDATE users SET language_code = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()
    conn.close()
    return True


# ==================== KUNLIK BONUS (DAILY 3 STARS) ====================

def claim_daily_bonus(user_id: int) -> Tuple[bool, str, int, Optional[int]]:
    """
    Claims 3 Stars daily bonus for user.
    Cooldown: 24 hours (86400 seconds).
    Returns (success, message, new_balance, remaining_seconds_if_fail)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance, last_daily_bonus FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)", (user_id,))
        balance = 0
        last_bonus = None
    else:
        balance = row["balance"] or 0
        last_bonus = row["last_daily_bonus"]

    now = datetime.utcnow()
    COOLDOWN = 86400  # 24 hours

    if last_bonus:
        try:
            clean_ts = str(last_bonus).replace("T", " ").split(".")[0]
            last_dt = datetime.strptime(clean_ts, "%Y-%m-%d %H:%M:%S")
            elapsed = (now - last_dt).total_seconds()
            if elapsed < COOLDOWN:
                remaining = int(COOLDOWN - elapsed)
                conn.close()
                return False, "Bugungi bonus allaqachon olingan!", balance, remaining
        except Exception:
            pass

    bonus_amount = 3
    new_balance = balance + bonus_amount
    cursor.execute("""
        UPDATE users 
        SET balance = balance + ?, last_daily_bonus = CURRENT_TIMESTAMP 
        WHERE user_id = ?
    """, (bonus_amount, user_id))

    cursor.execute("""
        INSERT INTO transactions (user_id, amount, type, description)
        VALUES (?, ?, 'daily_bonus', 'Kunlik bonus (+3 ⭐)')
    """, (user_id, bonus_amount))

    conn.commit()
    conn.close()
    return True, "Tabriklaymiz! +3 ⭐ Stars balansingizga muvaffaqiyatli qo'shildi!", new_balance, None


def get_daily_bonus_status(user_id: int) -> Dict[str, Any]:
    """Returns whether user can claim daily bonus and remaining seconds."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT last_daily_bonus, balance FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row or not row["last_daily_bonus"]:
        return {"can_claim": True, "remaining_seconds": 0, "bonus_amount": 3}

    now = datetime.utcnow()
    last_bonus = row["last_daily_bonus"]
    try:
        clean_ts = str(last_bonus).replace("T", " ").split(".")[0]
        last_dt = datetime.strptime(clean_ts, "%Y-%m-%d %H:%M:%S")
        elapsed = (now - last_dt).total_seconds()
        if elapsed < 86400:
            return {"can_claim": False, "remaining_seconds": int(86400 - elapsed), "bonus_amount": 3}
    except Exception:
        pass
    return {"can_claim": True, "remaining_seconds": 0, "bonus_amount": 3}


# ==================== LEADERBOARD (REYTING) ====================

def get_leaderboard_referrals(limit: int = 20) -> List[Dict[str, Any]]:
    """Returns top users who invited the most referrals."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.user_id, u.username, u.first_name, COUNT(r.user_id) as score
        FROM users u
        JOIN users r ON r.referred_by = u.user_id
        GROUP BY u.user_id
        HAVING score > 0
        ORDER BY score DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_leaderboard_creators(limit: int = 20) -> List[Dict[str, Any]]:
    """Returns top users who created the most emoji packs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, username, first_name, packs_created as score
        FROM users
        WHERE packs_created > 0
        ORDER BY packs_created DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_leaderboard_rank(user_id: int) -> Dict[str, Any]:
    """Returns a specific user's leaderboard standings and rank."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, username, first_name, balance, packs_created FROM users WHERE user_id = ?", (user_id,))
    u_row = cursor.fetchone()
    if not u_row:
        conn.close()
        return {"user_id": user_id, "ref_count": 0, "ref_rank": 0, "packs_created": 0, "creator_rank": 0}

    # Count user referrals
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE referred_by = ?", (user_id,))
    ref_count = cursor.fetchone()["count"]

    # Rank in referrals
    ref_rank = 0
    if ref_count > 0:
        cursor.execute("""
            SELECT COUNT(*) + 1 as rank FROM (
                SELECT COUNT(r.user_id) as cnt
                FROM users u
                JOIN users r ON r.referred_by = u.user_id
                GROUP BY u.user_id
                HAVING cnt > ?
            )
        """, (ref_count,))
        rr = cursor.fetchone()
        ref_rank = rr["rank"] if rr else 0

    # Rank in creators
    packs_created = u_row["packs_created"] or 0
    creator_rank = 0
    if packs_created > 0:
        cursor.execute("SELECT COUNT(*) + 1 as rank FROM users WHERE packs_created > ?", (packs_created,))
        cr = cursor.fetchone()
        creator_rank = cr["rank"] if cr else 0

    conn.close()
    return {
        "user_id": user_id,
        "first_name": u_row["first_name"] or "",
        "username": u_row["username"] or "",
        "ref_count": ref_count,
        "ref_rank": ref_rank,
        "packs_created": packs_created,
        "creator_rank": creator_rank
    }


# ==================== BROADCAST EXCLUSIONS (ISTISNOLAR) ====================

def add_broadcast_exclusion(user_id: int, reason: Optional[str] = None) -> bool:
    """Adds a user to the permanent broadcast exclusion list."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO broadcast_exclusions (user_id, reason, added_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (user_id, reason))
    conn.commit()
    conn.close()
    return True


def remove_broadcast_exclusion(user_id: int) -> bool:
    """Removes a user from the broadcast exclusion list."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM broadcast_exclusions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True


def get_broadcast_exclusions() -> List[Dict[str, Any]]:
    """Returns all users in the broadcast exclusion list."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.user_id, e.reason, e.added_at, u.username, u.first_name
        FROM broadcast_exclusions e
        LEFT JOIN users u ON u.user_id = e.user_id
        ORDER BY e.added_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def is_user_excluded(user_id: int) -> bool:
    """Checks if a user is excluded from broadcast."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM broadcast_exclusions WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return bool(row)


def get_broadcast_user_ids() -> List[int]:
    """Returns all user IDs for broadcast, strictly excluding any in broadcast_exclusions."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id FROM users
        WHERE user_id NOT IN (SELECT user_id FROM broadcast_exclusions)
    """)
    rows = cursor.fetchall()
    conn.close()
    return [row["user_id"] for row in rows]


# ==================== ADMIN: USER PACKS MANAGEMENT ====================

def get_all_user_packs_admin(user_id: Optional[int] = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """Returns user packs joined with user info for admin inspection."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("""
            SELECT p.id, p.user_id, p.pack_name, p.pack_title, p.created_at,
                   u.username, u.first_name
            FROM user_packs p
            LEFT JOIN users u ON u.user_id = p.user_id
            WHERE p.user_id = ?
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset))
    else:
        cursor.execute("""
            SELECT p.id, p.user_id, p.pack_name, p.pack_title, p.created_at,
                   u.username, u.first_name
            FROM user_packs p
            LEFT JOIN users u ON u.user_id = p.user_id
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_packs_count_admin(user_id: Optional[int] = None) -> int:
    """Returns total count of packs created (optionally filtered by user_id)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT COUNT(*) as cnt FROM user_packs WHERE user_id = ?", (user_id,))
    else:
        cursor.execute("SELECT COUNT(*) as cnt FROM user_packs")
    row = cursor.fetchone()
    conn.close()
    return row["cnt"] if row else 0

