from __future__ import annotations
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
