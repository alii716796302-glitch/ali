import sqlite3
from datetime import datetime, timedelta
from config import DB_FILE

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        subscription_end TIMESTAMP,
        is_admin INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        is_restricted INTEGER DEFAULT 1,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS required_channels (id INTEGER PRIMARY KEY AUTOINCREMENT, channel_username TEXT UNIQUE)''')
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('free_trial_hours', '24')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('subscription_price_monthly', '10')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('subscription_price_yearly', '100')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('subscription_days', '30')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('warning_hours', '2')")
    conn.commit()
    conn.close()

def get_setting(key):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_setting(key, value):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE settings SET value=? WHERE key=?", (value, key))
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if c.fetchone() is None:
        c.execute("INSERT INTO users (user_id, username, first_name, is_restricted) VALUES (?, ?, ?, 1)", (user_id, username, first_name))
    else:
        c.execute("UPDATE users SET username=?, first_name=? WHERE user_id=?", (username, first_name, user_id))
    conn.commit()
    conn.close()

def is_user_banned(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT is_banned FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row and row[0] == 1

def is_user_admin(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT is_admin FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row and row[0] == 1

def get_all_admins():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE is_admin=1")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def add_admin(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET is_admin=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def remove_admin(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET is_admin=0 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def ban_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def get_subscription_end(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT subscription_end FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_subscription(user_id, days):
    end_date = datetime.now() + timedelta(days=days)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET subscription_end=?, is_restricted=0 WHERE user_id=?", (end_date.isoformat(), user_id))
    if c.rowcount == 0:
        c.execute("INSERT INTO users (user_id, subscription_end, is_restricted) VALUES (?, ?, 0)", (user_id, end_date.isoformat()))
    conn.commit()
    conn.close()
    return end_date

def get_required_channels():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT channel_username FROM required_channels")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def add_required_channel(channel):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO required_channels (channel_username) VALUES (?)", (channel.strip().lstrip('@'),))
    conn.commit()
    conn.close()

def remove_required_channel(channel):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM required_channels WHERE channel_username=?", (channel.strip().lstrip('@'),))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id, username, first_name, subscription_end, is_admin, is_banned, is_restricted FROM users ORDER BY registered_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_stats():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    total = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    active = c.execute("SELECT COUNT(*) FROM users WHERE subscription_end IS NOT NULL AND subscription_end > datetime('now') AND is_restricted=0").fetchone()[0]
    admins = c.execute("SELECT COUNT(*) FROM users WHERE is_admin=1").fetchone()[0]
    banned = c.execute("SELECT COUNT(*) FROM users WHERE is_banned=1").fetchone()[0]
    restricted = c.execute("SELECT COUNT(*) FROM users WHERE is_restricted=1").fetchone()[0]
    conn.close()
    return {"total": total, "active": active, "admins": admins, "banned": banned, "restricted": restricted}

def get_remaining_time(user_id):
    end_date = get_subscription_end(user_id)
    if not end_date:
        return None
    try:
        end = datetime.fromisoformat(end_date)
        if end > datetime.now():
            return (end - datetime.now()).total_seconds() / 3600
        return 0
    except:
        return None

def is_user_restricted(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT is_restricted FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row is None:
        return True
    return row[0] == 1
