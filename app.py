from flask import Flask, request, jsonify, render_template_string
import requests
import os
import random
import hmac
import hashlib
import json
from urllib.parse import parse_qsl
import psycopg
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__, static_folder='static')

# ===== Environment Variables =====
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@MarshalomTech")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "marshalom_bot")
AI_CHANNEL_ID = os.environ.get("AI_CHANNEL_ID", "@MarshalomAI")
PRICE_CHANNEL_ID = os.environ.get("PRICE_CHANNEL_ID", "@Pricefrombot")
HR_CHANNEL_ID = os.environ.get("HR_CHANNEL_ID", "@Marshalomet")
DATABASE_URL = os.environ.get("DATABASE_URL")
BASE_URL = os.environ.get("BASE_URL", "https://marshalom700.onrender.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_PASSWORD_2 = os.environ.get("ADMIN_PASSWORD_2")
TECHNICAL_PASSWORD = os.environ.get("TECHNICAL_PASSWORD")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
ETHIOPIA_TZ = pytz.timezone("Africa/Addis_Ababa")

# ===== Database =====
def get_db_connection():
    return psycopg.connect(DATABASE_URL, sslmode='require')

def init_db():
    if not DATABASE_URL:
        print("⚠️ DATABASE_URL not set - storage disabled")
        return
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS promos (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                text_am TEXT,
                text_en TEXT,
                text_ti TEXT,
                text_or TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("ALTER TABLE promos ADD COLUMN IF NOT EXISTS text_am TEXT")
        cur.execute("ALTER TABLE promos ADD COLUMN IF NOT EXISTS text_en TEXT")
        cur.execute("ALTER TABLE promos ADD COLUMN IF NOT EXISTS text_ti TEXT")
        cur.execute("ALTER TABLE promos ADD COLUMN IF NOT EXISTS text_or TEXT")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                photo_url TEXT,
                photos TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS photos TEXT")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                user_id BIGINT PRIMARY KEY,
                name TEXT,
                username TEXT,
                message_count INTEGER DEFAULT 1,
                first_seen TIMESTAMP DEFAULT NOW(),
                last_seen TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS price_inquiries (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                name TEXT,
                username TEXT,
                product_name TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("ALTER TABLE price_inquiries ADD COLUMN IF NOT EXISTS product_name TEXT")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                location TEXT,
                pdf_url TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS pdf_url TEXT")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS job_applications (
                id SERIAL PRIMARY KEY,
                job_id INTEGER,
                job_title TEXT,
                user_id BIGINT,
                name TEXT,
                username TEXT,
                phone TEXT,
                email TEXT,
                id_number TEXT,
                selfie_photo TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS email TEXT")
        cur.execute("ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS id_number TEXT")
        cur.execute("ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS selfie_photo TEXT")
        cur.execute("ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending'")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS site_config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS internal_messages (
                id SERIAL PRIMARY KEY,
                sender_name TEXT,
                sender_username TEXT,
                sender_user_id BIGINT,
                recipient_type TEXT,
                recipient_username TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS testimonials (
                id SERIAL PRIMARY KEY,
                name TEXT,
                username TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                position TEXT,
                salary TEXT,
                bonus TEXT DEFAULT '',
                warnings TEXT DEFAULT '',
                tasks TEXT DEFAULT '',
                role TEXT DEFAULT 'employee',
                must_change_password BOOLEAN DEFAULT TRUE,
                telegram_chat_id BIGINT,
                internal_email TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("ALTER TABLE employees ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'employee'")
        cur.execute("ALTER TABLE employees ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN DEFAULT TRUE")
        cur.execute("ALTER TABLE employees ADD COLUMN IF NOT EXISTS telegram_chat_id BIGINT")
        cur.execute("ALTER TABLE employees ADD COLUMN IF NOT EXISTS internal_email TEXT")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                name TEXT,
                username TEXT,
                text TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                chat_id BIGINT PRIMARY KEY,
                role TEXT NOT NULL,
                employee_id INTEGER,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                photo_url TEXT,
                file_url TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS custom_pages (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                icon TEXT DEFAULT '📄',
                content TEXT,
                page_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database ready.")
    except Exception as e:
        print(f"DB init error: {e}")

init_db()

# ===== Helper Functions =====
def send_with_webapp_button(chat_id, text, button_text, webapp_path):
    webapp_url = f"{BASE_URL.rstrip('/')}{webapp_path}"
    result = requests.post(f"{TELEGRAM_URL}/sendMessage", json={
        'chat_id': chat_id,
        'text': text,
        'reply_markup': {'inline_keyboard': [[{'text': button_text, 'web_app': {'url': webapp_url}}]]}
    })
    resp_json = result.json() if result.ok or result.content else {}
    if not resp_json.get('ok'):
        print(f"⚠️ web_app button send failed: {resp_json.get('description')}")
        requests.post(f"{TELEGRAM_URL}/sendMessage", json={
            'chat_id': chat_id,
            'text': text,
            'reply_markup': {'inline_keyboard': [[{'text': button_text, 'url': webapp_url}]]}
        })
    return resp_json

def load_promos():
    if not DATABASE_URL: return []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(text_am, text) FROM promos ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r[0] for r in rows]

def add_promo(raw_text):
    if not DATABASE_URL: return 0
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        translations = {"am": raw_text, "en": raw_text, "ti": raw_text, "or": raw_text}
        cur.execute(
            "INSERT INTO promos (text, text_am, text_en, text_ti, text_or) VALUES (%s,%s,%s,%s,%s)",
            (raw_text, translations["am"], translations["en"], translations["ti"], translations["or"])
        )
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM promos")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count
    except Exception as e:
        print(f"DB add error: {e}")
        return 0

def get_promos_multilang():
    if not DATABASE_URL: return []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, COALESCE(text_am,text), COALESCE(text_en,text), COALESCE(text_ti,text), COALESCE(text_or,text) FROM promos ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "am": r[1], "en": r[2], "ti": r[3], "or": r[4]} for r in rows]

def get_products(category=None):
    if not DATABASE_URL: return []
    conn = get_db_connection()
    cur = conn.cursor()
    if category:
        cur.execute("SELECT id, name, category, description, photo_url, photos FROM products WHERE category=%s ORDER BY id DESC", (category,))
    else:
        cur.execute("SELECT id, name, category, description, photo_url, photos FROM products ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    result = []
    for r in rows:
        try:
            photos = json.loads(r[5]) if r[5] else ([r[4]] if r[4] else [])
        except:
            photos = [r[4]] if r[4] else []
        result.append({"id": r[0], "name": r[1], "category": r[2], "description": r[3], "photo_url": r[4], "photos": photos})
    return result

def add_product(name, category, description, photos):
    if isinstance(photos, str):
        photos = [photos] if photos else []
    photo_url = photos[0] if photos else None
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, category, description, photo_url, photos) VALUES (%s,%s,%s,%s,%s) RETURNING id",
        (name, category, description, photo_url, json.dumps(photos, ensure_ascii=False))
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return new_id

def delete_product(product_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
    conn.commit()
    cur.close()
    conn.close()

def upsert_customer(user_id, name, username):
    if not DATABASE_URL or not user_id: return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO customers (user_id, name, username, message_count, last_seen)
        VALUES (%s, %s, %s, 1, NOW())
        ON CONFLICT (user_id) DO UPDATE SET
            name = EXCLUDED.name,
            username = EXCLUDED.username,
            message_count = customers.message_count + 1,
            last_seen = NOW()
    """, (user_id, name, username))
    conn.commit()
    cur.close()
    conn.close()

def log_price_inquiry(user_id, name, username, product_name=None):
    if not DATABASE_URL: return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO price_inquiries (user_id, name, username, product_name) VALUES (%s,%s,%s,%s)",
        (user_id, name, username, product_name)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_jobs():
    if not DATABASE_URL: return []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, location, pdf_url FROM jobs WHERE active=TRUE ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "title": r[1], "description": r[2], "location": r[3], "pdf_url": r[4]} for r in rows]

def add_job(title, description, location, pdf_url=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO jobs (title, description, location, pdf_url) VALUES (%s,%s,%s,%s) RETURNING id", (title, description, location, pdf_url))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return new_id

def delete_job(job_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE jobs SET active=FALSE WHERE id=%s", (job_id,))
    conn.commit()
    cur.close()
    conn.close()

def add_job_application(job_id, job_title, user_id, name, username, phone, email='', id_number='', selfie_photo=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO job_applications
           (job_id, job_title, user_id, name, username, phone, email, id_number, selfie_photo, status)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'pending') RETURNING id""",
        (job_id, job_title, user_id, name, username, phone, email, id_number, selfie_photo)
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return new_id

def get_pending_applications():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, job_title, name, username, phone, email, user_id, status FROM job_applications ORDER BY id DESC LIMIT 50")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "job_title": r[1], "name": r[2], "username": r[3], "phone": r[4], "email": r[5], "user_id": r[6], "status": r[7]} for r in rows]

def set_application_status(app_id, status):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE job_applications SET status=%s WHERE id=%s RETURNING user_id, name, job_title", (status, app_id))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return {"user_id": row[0], "name": row[1], "job_title": row[2]} if row else None

def get_config(key, default=None):
    if not DATABASE_URL: return default
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT value FROM site_config WHERE key=%s", (key,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return json.loads(row[0])
    return default

def set_config(key, value):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO site_config (key, value) VALUES (%s, %s)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """, (key, json.dumps(value, ensure_ascii=False)))
    conn.commit()
    cur.close()
    conn.close()

def get_stats():
    if not DATABASE_URL: return {"customers":0,"messages":0,"price_inquiries":0,"products":0,"promos":0}
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), COALESCE(SUM(message_count),0) FROM customers")
    cust_count, msg_count = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM price_inquiries")
    price_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM products")
    product_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM promos")
    promo_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"customers": cust_count, "messages": msg_count, "price_inquiries": price_count, "products": product_count, "promos": promo_count}

def get_customers_list():
    if not DATABASE_URL: return []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, name, username, message_count, last_seen FROM customers ORDER BY last_seen DESC LIMIT 200")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"user_id": r[0], "name": r[1], "username": r[2], "message_count": r[3], "last_seen": str(r[4])} for r in rows]

def set_session(chat_id, role, employee_id=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sessions (chat_id, role, employee_id) VALUES (%s, %s, %s)
        ON CONFLICT (chat_id) DO UPDATE SET role = EXCLUDED.role, employee_id = EXCLUDED.employee_id, created_at = NOW()
    """, (chat_id, role, employee_id))
    conn.commit()
    cur.close()
    conn.close()

def get_session(chat_id):
    if not DATABASE_URL: return None
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT role, employee_id FROM sessions WHERE chat_id=%s", (chat_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"role": row[0], "employee_id": row[1]}
    return None

def clear_session(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE chat_id=%s", (chat_id,))
    conn.commit()
    cur.close()
    conn.close()

def is_admin_chat(chat_id):
    if str(chat_id) == str(OWNER_CHAT_ID): return True
    session = get_session(chat_id)
    return session is not None and session["role"] == "admin"

def is_technical_chat(chat_id):
    session = get_session(chat_id)
    return session is not None and session["role"] in ("admin", "technical")

def is_team_leader_or_admin(chat_id):
    if is_admin_chat(chat_id): return True
    session = get_session(chat_id)
    if session and session["role"] == "employee" and session.get("employee_id"):
        emp = get_employee_by_id(session["employee_id"])
        return emp is not None and emp.get("role") == "team_leader"
    return False

def generate_temp_password():
    import random as _r, string as _s
    return ''.join(_r.choices(_s.ascii_uppercase + _s.digits, k=8))

def add_employee(username, password, full_name, position, salary):
    first_name_part = full_name.strip().split(' ')[0].lower() if full_name else username
    safe_part = ''.join(c for c in first_name_part if c.isalnum()) or username
    internal_email = f"{safe_part}@marshalom"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM employees WHERE internal_email=%s", (internal_email,))
    if cur.fetchone()[0] > 0:
        cur.execute("SELECT COUNT(*) FROM employees WHERE internal_email LIKE %s", (f"{safe_part}%@marshalom",))
        count = cur.fetchone()[0]
        internal_email = f"{safe_part}{count+1}@marshalom"
    cur.execute("""
        INSERT INTO employees (username, password, full_name, position, salary, must_change_password, internal_email)
        VALUES (%s,%s,%s,%s,%s,TRUE,%s) RETURNING id
    """, (username, password, full_name, position, salary, internal_email))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return new_id

def get_employee_by_credentials(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, full_name, position, salary, bonus, warnings, tasks, role, must_change_password, internal_email FROM employees WHERE username=%s AND password=%s", (username, password))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"id": row[0], "full_name": row[1], "position": row[2], "salary": row[3], "bonus": row[4],
                "warnings": row[5], "tasks": row[6], "role": row[7], "must_change_password": row[8], "internal_email": row[9]}
    return None

def get_employee_by_id(employee_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, full_name, position, salary, bonus, warnings, tasks, role, must_change_password, telegram_chat_id, internal_email FROM employees WHERE id=%s", (employee_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "full_name": row[2], "position": row[3], "salary": row[4],
                "bonus": row[5], "warnings": row[6], "tasks": row[7], "role": row[8],
                "must_change_password": row[9], "telegram_chat_id": row[10], "internal_email": row[11]}
    return None

def get_employee_by_username(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, full_name, position, salary, bonus, warnings, tasks, role, must_change_password, telegram_chat_id, internal_email FROM employees WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "full_name": row[2], "position": row[3], "salary": row[4],
                "bonus": row[5], "warnings": row[6], "tasks": row[7], "role": row[8],
                "must_change_password": row[9], "telegram_chat_id": row[10], "internal_email": row[11]}
    return None

def list_employees():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, full_name, position, role FROM employees ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "username": r[1], "full_name": r[2], "position": r[3], "role": r[4]} for r in rows]

def update_employee_field(username, field, value, append=False):
    conn = get_db_connection()
    cur = conn.cursor()
    if append:
        cur.execute(f"UPDATE employees SET {field} = {field} || %s WHERE username=%s", (f"\n• {value}", username))
    else:
        cur.execute(f"UPDATE employees SET {field} = %s WHERE username=%s", (value, username))
    conn.commit()
    cur.close()
    conn.close()

def set_employee_password(username, new_password, must_change=False):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE employees SET password=%s, must_change_password=%s WHERE username=%s", (new_password, must_change, username))
    conn.commit()
    cur.close()
    conn.close()

def set_employee_role(username, role):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE employees SET role=%s WHERE username=%s", (role, username))
    conn.commit()
    cur.close()
    conn.close()

def set_employee_chat_id(employee_id, chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE employees SET telegram_chat_id=%s WHERE id=%s", (chat_id, employee_id))
    conn.commit()
    cur.close()
    conn.close()

def add_feedback(user_id, name, username, text):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO feedback (user_id, name, username, text) VALUES (%s,%s,%s,%s)", (user_id, name, username, text))
    conn.commit()
    cur.close()
    conn.close()

def get_recent_feedback(limit=20):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, username, text, created_at FROM feedback ORDER BY id DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"name": r[0], "username": r[1], "text": r[2], "created_at": str(r[3])} for r in rows]

def add_testimonial(name, username, message):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO testimonials (name, username, message) VALUES (%s,%s,%s)", (name, username, message))
    conn.commit()
    cur.close()
    conn.close()

def get_testimonials(limit=30):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, username, message, created_at FROM testimonials ORDER BY id DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"name": r[0], "username": r[1], "message": r[2], "created_at": str(r[3])} for r in rows]

def send_internal_message(sender_name, sender_username, sender_user_id, recipient_type, recipient_username, message):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO internal_messages (sender_name, sender_username, sender_user_id, recipient_type, recipient_username, message)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (sender_name, sender_username, sender_user_id, recipient_type, recipient_username, message))
    conn.commit()
    cur.close()
    conn.close()

def get_inbox(recipient_type=None, recipient_username=None, limit=50):
    conn = get_db_connection()
    cur = conn.cursor()
    if recipient_type == 'admin':
        cur.execute("SELECT sender_name, sender_username, sender_user_id, recipient_type, recipient_username, message, created_at FROM internal_messages ORDER BY id DESC LIMIT %s", (limit,))
    else:
        cur.execute("""
            SELECT sender_name, sender_username, sender_user_id, recipient_type, recipient_username, message, created_at
            FROM internal_messages WHERE recipient_username=%s ORDER BY id DESC LIMIT %s
        """, (recipient_username, limit))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"sender_name": r[0], "sender_username": r[1], "sender_user_id": r[2], "recipient_type": r[3],
             "recipient_username": r[4], "message": r[5], "created_at": str(r[6])} for r in rows]

# ===== New Functions =====
def get_applications():
    if not DATABASE_URL: return []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, photo_url, file_url FROM applications ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "name": r[1], "photo_url": r[2], "file_url": r[3]} for r in rows]

def add_application(name, photo_url, file_url):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO applications (name, photo_url, file_url) VALUES (%s,%s,%s) RETURNING id", (name, photo_url, file_url))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return new_id

def delete_application(app_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM applications WHERE id=%s", (app_id,))
    conn.commit()
    cur.close()
    conn.close()

def get_custom_pages():
    if not DATABASE_URL: return []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, icon, content FROM custom_pages ORDER BY page_order ASC, id ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "title": r[1], "icon": r[2], "content": r[3]} for r in rows]

def add_custom_page(title, icon, content):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(page_order), -1) + 1 FROM custom_pages")
    new_order = cur.fetchone()[0]
    cur.execute("INSERT INTO custom_pages (title, icon, content, page_order) VALUES (%s,%s,%s,%s) RETURNING id", (title, icon, content, new_order))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return new_id

def delete_custom_page(page_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM custom_pages WHERE id=%s", (page_id,))
    conn.commit()
    cur.close()
    conn.close()

def update_page_order(order_list):
    conn = get_db_connection()
    cur = conn.cursor()
    for idx, page_id in enumerate(order_list):
        cur.execute("UPDATE custom_pages SET page_order=%s WHERE id=%s", (idx, page_id))
    conn.commit()
    cur.close()
    conn.close()

def get_page_order():
    return get_config('page_order', [])

def set_page_order(order_list):
    set_config('page_order', order_list)

def get_theme():
    default = {
        "header_animation": "blink",
        "footer_ticker": True,
        "background_photo": None,
        "background_photo_2": None,
        "primary_color": "#4a9eff",
        "card_color": "#17212b",
        "card_shadow": "medium",
        "font_family": "Segoe UI",
        "button_style": "rounded"
    }
    saved = get_config('theme', {})
    return {**default, **saved}

def set_theme(theme_dict):
    set_config('theme', theme_dict)

def get_settings():
    default = {
        "bot_name": "MarshalomSupportBot",
        "welcome_message": "✨ እንኳን ደህና መጡ!",
        "working_hours": "8:00 - 22:00",
        "holiday_message": "በዓል ነው! እንኳን ደስ አላችሁ!",
        "admin_notify": True
    }
    saved = get_config('settings', {})
    return {**default, **saved}

def set_settings(settings_dict):
    set_config('settings', settings_dict)

def ask_deepseek(text):
    if not DEEPSEEK_API_KEY: return None
    try:
        url = "https://api.deepseek.com/chat/completions"
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "system", "content": "አንተ Marshalom AI ነህ"}, {"role": "user", "content": text}],
            "max_tokens": 300
        }
        response = requests.post(url, json=payload, headers=headers, timeout=25)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        return None
    except Exception as e:
        print(f"DeepSeek exception: {e}")
        return None

def post_random_promo():
    promos = load_promos()
    if not promos: return
    promo_text = random.choice(promos)
    reply_markup = {'inline_keyboard': [[{'text': '💬 ዋጋ ጠይቁ', 'url': f'https://t.me/{BOT_USERNAME}?start=price'}]]}
    try:
        requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': CHANNEL_ID, 'text': promo_text, 'reply_markup': reply_markup})
        print(f"Posted promo to {CHANNEL_ID}")
    except Exception as e:
        print(f"Failed to post promo: {e}")

def schedule_daily_promos():
    scheduler = BackgroundScheduler(timezone=ETHIOPIA_TZ)
    post_hours = [9, 12, 15, 17, 19]
    for hour in post_hours:
        scheduler.add_job(post_random_promo, 'cron', hour=hour, minute=random.randint(0, 30))
    scheduler.start()
    print("✅ Promo scheduler started.")

def verify_telegram_webapp_data(init_data):
    try:
        parsed = dict(parse_qsl(init_data))
        received_hash = parsed.pop('hash', None)
        if not received_hash: return None
        data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(parsed.items()))
        secret_key = hmac.new(b"WebAppData", TELEGRAM_TOKEN.encode(), hashlib.sha256).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if computed_hash == received_hash:
            user_data = json.loads(parsed.get('user', '{}'))
            return user_data
        return None
    except Exception as e:
        print(f"WebApp verify error: {e}")
        return None

def download_telegram_photo_as_base64(file_id):
    try:
        file_info = requests.get(f"{TELEGRAM_URL}/getFile", params={'file_id': file_id}, timeout=15).json()
        if not file_info.get('ok'): return None
        file_path = file_info['result']['file_path']
        file_bytes = requests.get(f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}", timeout=20).content
        import base64 as _b64
        ext = file_path.split('.')[-1] if '.' in file_path else 'jpg'
        return f"data:image/{ext};base64,{_b64.b64encode(file_bytes).decode()}"
    except Exception as e:
        print(f"download_telegram_photo_as_base64 error: {e}")
        return None

CATALOG_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Shalom Technology</title>
</head>
<body>
<h1>Shalom Technology</h1>
<p>እንኳን ደህና መጡ!</p>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Admin Dashboard</title>
</head>
<body>
<h1>⚙️ Admin Dashboard</h1>
<p>ሙሉ ቁጥጥር እዚህ ነው!</p>
</body>
</html>
"""

# ===== Routes =====
@app.route('/')
def index():
    return "Marshalom Bot is running! 🤖"

@app.route('/webapp')
def webapp_catalog():
    return render_template_string(CATALOG_HTML)

@app.route('/admin')
def admin_dashboard():
    return render_template_string(ADMIN_HTML)

@app.route('/test')
def test():
    return "Test endpoint working!"

@app.route('/api/products')
def api_products():
    return jsonify(get_products())

@app.route('/api/promos')
def api_promos():
    return jsonify(get_promos_multilang())

@app.route('/api/jobs')
def api_jobs():
    return jsonify(get_jobs())

@app.route('/api/applications')
def api_applications():
    return jsonify(get_applications())

@app.route('/api/custom_pages')
def api_custom_pages():
    return jsonify(get_custom_pages())

@app.route('/api/theme')
def api_theme():
    return jsonify(get_theme())

@app.route('/api/testimonials')
def api_testimonials():
    return jsonify(get_testimonials())

# ===== Start =====
schedule_daily_promos()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
