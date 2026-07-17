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

# ===== Session Management =====
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

# ===== Employee Management =====
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
            "messages": [{"role": "system", "content": "አንተ Marshalom AI ነህ — የ Shalom Technology ረዳት"}, {"role": "user", "content": text}],
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

# ===== HTML Pages =====
CATALOG_HTML = """
<!DOCTYPE html>
<html lang="am">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Shalom Technology</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',system-ui,sans-serif; }
body { background:#0b1219; min-height:100vh; color:#fff; }
.app-container { max-width:420px; width:100%; margin:0 auto; min-height:100vh; background:#17212b; overflow:hidden; padding:14px; position:relative; }
.header { text-align:center; padding-bottom:12px; border-bottom:1px solid #2b3a4a; margin-bottom:12px; }
.header .top-row { display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; }
.header .lang-selector { display:flex; gap:4px; }
.header .lang-selector button { background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.08); color:#8aa3b5; padding:3px 8px; border-radius:12px; font-size:10px; cursor:pointer; }
.header .lang-selector button.active { background:rgba(74,158,255,0.2); border-color:#4a9eff; color:#4a9eff; }
.header .logo-img { width:40px; height:40px; border-radius:10px; object-fit:cover; box-shadow:0 2px 10px rgba(0,0,0,0.4); animation:logoSpin 6s ease-in-out infinite; }
@keyframes logoSpin { 0%{transform:rotateY(0deg) rotateX(0deg);} 25%{transform:rotateY(360deg) rotateX(0deg);} 50%{transform:rotateY(360deg) rotateX(360deg);} 100%{transform:rotateY(360deg) rotateX(360deg);} }
.menu-btn { transition:transform 0.2s ease; border-radius:14px; padding:10px 4px; text-align:center; font-size:9px; font-weight:500; cursor:pointer; color:#e0edf5; border:none; box-shadow:0 4px 15px rgba(0,0,0,0.3); }
.menu-btn:active { transform:scale(0.93); }
.menu-btn .icon { font-size:22px; display:block; margin-bottom:2px; }
.menu-btn:nth-child(1){background:linear-gradient(135deg,#2a3a4a,#1a2a3a);}
.menu-btn:nth-child(2){background:linear-gradient(135deg,#4a2a22,#3a1a12);}
.menu-btn:nth-child(3){background:linear-gradient(135deg,#4a3a1a,#3a2a0a);}
.menu-btn:nth-child(4){background:linear-gradient(135deg,#1a4a3a,#0a3a2a);}
.menu-btn:nth-child(5){background:linear-gradient(135deg,#3a2a5a,#2a1a4a);}
.menu-btn:nth-child(6){background:linear-gradient(135deg,#4a2a3a,#3a1a2a);}
.menu-btn:nth-child(7){background:linear-gradient(135deg,#4a3a1a,#3a2a0a);}
.menu-btn:nth-child(8){background:linear-gradient(135deg,#1a4a3a,#0a3a2a);}
.menu-btn:nth-child(9){background:linear-gradient(135deg,#2a3a5a,#1a2a4a);}
.menu-btn:nth-child(10){background:linear-gradient(135deg,#1a4a3a,#0a3a2a);}
.menu-btn:nth-child(11){background:linear-gradient(135deg,#4a2a1a,#3a1a0a);}
.menu-btn:nth-child(12){background:linear-gradient(135deg,#2a4a4a,#1a3a3a);}
.menu-btn:nth-child(13){background:linear-gradient(135deg,#4a4a1a,#3a3a0a);}
.menu-btn:nth-child(14){background:linear-gradient(135deg,#4a2a2a,#3a1a1a);}
.menu-btn:nth-child(15){background:linear-gradient(135deg,#1a2a4a,#0a1a3a);}
.menu-btn:nth-child(16){background:linear-gradient(135deg,#3a2a5a,#2a1a4a);}
.menu-btn:nth-child(17){background:linear-gradient(135deg,#4a2a3a,#3a1a2a);}
.promo-anim-card { animation:slideInFade 0.5s ease; }
@keyframes slideInFade { from{opacity:0;transform:translateX(-15px);} to{opacity:1;transform:translateX(0);} }
.product-card { animation:productRotateIn 0.6s ease; cursor:pointer; background:rgba(255,255,255,0.04); border-radius:14px; overflow:hidden; border:1px solid rgba(255,255,255,0.06); }
@keyframes productRotateIn { from{opacity:0;transform:rotateY(15deg) scale(0.9);} to{opacity:1;transform:rotateY(0) scale(1);} }
.fullscreen-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.92); z-index:999; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:20px; }
.fullscreen-overlay img { max-width:100%; max-height:60%; border-radius:12px; }
.fullscreen-overlay .close-fs { position:absolute; top:20px; right:20px; font-size:28px; color:#fff; cursor:pointer; }
.header h1 { font-size:18px; font-weight:700; background:linear-gradient(90deg,#4a9eff,#7ac7ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-top:4px; }
.header .sub { font-size:11px; color:#8aa3b5; }
.pages { padding:6px 0 80px; }
.page { display:none; animation:fadeSlide 0.25s ease; }
.page.active { display:block; }
@keyframes fadeSlide { 0%{opacity:0;transform:translateY(10px);} 100%{opacity:1;transform:translateY(0);} }
.page-title { font-size:15px; font-weight:600; color:#fff; display:flex; align-items:center; gap:6px; margin-bottom:10px; }
.back-btn { background:rgba(255,255,255,0.08); border:none; color:#fff; font-size:18px; padding:2px 12px; border-radius:30px; cursor:pointer; }
.home-btn { background:rgba(255,255,255,0.08); border:none; color:#4a9eff; font-size:16px; padding:2px 10px; border-radius:30px; cursor:pointer; }
.menu-grid { display:grid; grid-template-columns:1fr 1fr 1fr; gap:6px; margin-bottom:12px; }
.section-title { color:#b8a84a; font-size:13px; font-weight:600; margin-bottom:8px; }
.product-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:10px; }
.product-card .promo-img { width:100%; height:100px; object-fit:cover; background:linear-gradient(135deg,#1a2a3a,#2a3a4a); }
.product-card .info { padding:6px 8px; text-align:center; }
.product-card .name { font-weight:600; font-size:11px; color:#b8a84a; }
.product-card .desc { font-size:9px; color:#8aa3b5; margin:2px 0 4px; white-space:pre-line; max-height:60px; overflow-y:auto; }
.product-card .ask-btn { width:100%; padding:5px; border:none; border-radius:8px; color:#fff; font-weight:600; font-size:10px; cursor:pointer; background:linear-gradient(135deg,#4a3a1a,#3a2a0a); }
.channel-box { padding:8px; background:rgba(74,158,255,0.08); border-radius:12px; text-align:center; border:1px dashed #4a9eff; margin-bottom:10px; }
.channel-box a { color:#4a9eff; font-weight:600; text-decoration:none; font-size:12px; }
.promo-banner { background:linear-gradient(135deg,#4a2a2a,#3a1a1a); border-radius:12px; padding:10px 14px; margin-top:10px; display:flex; align-items:center; gap:10px; border:1px solid #4a3a1a; }
.promo-banner .text { font-size:12px; color:#c0d8e8; flex:1; font-weight:600; }
.bottom-nav { position:fixed; bottom:0; left:50%; transform:translateX(-50%); max-width:420px; width:100%; background:rgba(15,26,36,0.96); backdrop-filter:blur(14px); border-top:1px solid #2b3a4a; display:flex; justify-content:space-around; padding:8px 0 14px; }
.nav-item { color:#6a8a9e; font-size:8px; text-align:center; cursor:pointer; padding:2px 6px; }
.nav-item.active { color:#4a9eff; }
.nav-item .icon { font-size:16px; display:block; }
.btn-primary { background:#4a9eff; border:none; border-radius:30px; padding:10px; color:#fff; font-weight:600; font-size:13px; width:100%; cursor:pointer; margin-top:4px; }
.btn-primary.gold { background:#b8a84a; color:#1a1a2e; }
.card-box { background:rgba(255,255,255,0.04); border-radius:12px; padding:10px; border:1px solid rgba(255,255,255,0.06); text-align:center; cursor:pointer; }
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.grid3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:6px; }
.input-field { width:100%; padding:10px; margin-bottom:8px; background:rgba(255,255,255,0.05); border:1px solid #2b3a4a; border-radius:10px; color:#fff; font-size:13px; }
.stat-box { background:rgba(255,255,255,0.04); border-radius:8px; padding:6px; text-align:center; }
.stat-num { font-size:16px; font-weight:700; }
.stat-label { font-size:7px; color:#8aa3b5; }
.empty-msg { text-align:center; opacity:0.6; margin-top:30px; font-size:12px; }
.ticker { overflow:hidden; white-space:nowrap; background:#17212b; padding:4px 0; border-top:1px solid #2b3a4a; }
.ticker-wrap { display:inline-block; animation:ticker 20s linear infinite; }
.ticker-item { display:inline-block; padding:0 12px; font-size:12px; color:#8aa3b5; }
@keyframes ticker { 0%{transform:translateX(0);} 100%{transform:translateX(-50%);} }
.blink { animation:blink 2s infinite; }
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }
.slider-container { position:relative; }
.slider-img { width:100%; height:150px; object-fit:cover; }
.slider-dots { text-align:center; margin-top:4px; }
.dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:#555; margin:0 3px; cursor:pointer; }
.dot.active { background:#4a9eff; }
</style>
</head>
<body>
<div class="app-container">
    <div class="header">
        <div class="top-row">
            <img class="logo-img" src="/static/logo.jpg" />
            <div class="lang-selector" id="langSelector">
                <button class="active" data-lang="am" onclick="switchLanguage('am')">አማ</button>
                <button data-lang="en" onclick="switchLanguage('en')">EN</button>
                <button data-lang="ti" onclick="switchLanguage('ti')">ትግ</button>
                <button data-lang="or" onclick="switchLanguage('or')">ኦሮ</button>
            </div>
        </div>
        <h1 id="mainTitle" class="blink">Shalom Technology</h1>
        <div class="sub" id="mainSub">✨ የእርስዎ የደህንነት አጋር ✨</div>
    </div>
    <div class="pages" id="pagesContainer">
        <div class="page active" id="page-home">
            <div id="homeHeroBox" style="background:linear-gradient(135deg,#1a2a3a,#243447); border-radius:18px; padding:22px 16px; text-align:center; border:1px solid rgba(74,158,255,0.15); box-shadow:0 8px 24px rgba(0,0,0,0.3);">
                <img src="/static/logo.jpg" style="width:70px; height:70px; border-radius:16px; object-fit:cover; box-shadow:0 4px 16px rgba(0,0,0,0.4); animation:logoSpin 6s ease-in-out infinite;" />
                <div style="color:#fff; font-size:16px; font-weight:700; margin-top:10px;">Shalom Technology</div>
                <div style="color:#9bb0c0; font-size:11px; margin-top:2px;">✨ የእርስዎ የደህንነት አጋር ✨</div>
                <button class="btn-primary gold" style="margin-top:16px;" onclick="toggleHomeMenu()">🚀 Marshalom Application</button>
            </div>
            <div id="homeMenuGrid" style="display:none; margin-top:12px;">
                <div class="menu-grid" id="menuGrid">
                    <div class="menu-btn" onclick="showPage('page-products')"><span class="icon">🛍️</span><span data-key="m1">ምርቶች</span></div>
                    <div class="menu-btn" onclick="showPage('page-call')"><span class="icon">📞</span><span data-key="m2">ይደውሉ</span></div>
                    <div class="menu-btn" onclick="showPage('page-social')"><span class="icon">🌐</span><span data-key="m3">ማህበራዊ</span></div>
                    <div class="menu-btn" onclick="showPage('page-share')"><span class="icon">👥</span><span data-key="m4">ማጋሪያ</span></div>
                    <div class="menu-btn" onclick="showPage('page-news')"><span class="icon">📰</span><span data-key="m5">ዜና</span></div>
                    <div class="menu-btn" onclick="showPage('page-applications')"><span class="icon">📱</span><span data-key="m6">አፕሊኬሽን</span></div>
                    <div class="menu-btn" onclick="showPage('page-jobs')"><span class="icon">💼</span><span data-key="m7">ክፍት ስራ</span></div>
                    <div class="menu-btn" onclick="showPage('page-discount')"><span class="icon">🎁</span><span data-key="m8">ቅናሽ</span></div>
                    <div class="menu-btn" onclick="showPage('page-ai')"><span class="icon">🤖</span><span data-key="m9">ረዳት</span></div>
                    <div class="menu-btn" onclick="showPage('page-support')"><span class="icon">🛡️</span><span data-key="m10">ድጋፍ</span></div>
                    <div class="menu-btn" onclick="showPage('page-promo')"><span class="icon">📢</span><span data-key="m11">ማስታወቂያ</span></div>
                    <div class="menu-btn" onclick="showPage('page-tips')"><span class="icon">💡</span><span data-key="m12">ምክሮች</span></div>
                    <div class="menu-btn" onclick="showPage('page-banks')"><span class="icon">🏦</span><span data-key="m13">ባንክ</span></div>
                    <div class="menu-btn" onclick="showPage('page-feedback')"><span class="icon">💬</span><span data-key="m14">አስተያየት</span></div>
                    <div class="menu-btn" onclick="showPage('page-admin')"><span class="icon">⚙️</span><span data-key="m15">አድሚን</span></div>
                    <div class="menu-btn" onclick="showPage('page-teamleader')"><span class="icon">👔</span><span data-key="m16">ቲም ሊደር</span></div>
                    <div class="menu-btn" onclick="showPage('page-employee')"><span class="icon">👤</span><span data-key="m17">ሰራተኛ</span></div>
                </div>
            </div>
            <div class="channel-box">
                📢 <a href="https://t.me/MarshalomTech" target="_blank">@MarshalomTech</a>
            </div>
            <div class="promo-banner" onclick="showPage('page-promo')" style="cursor:pointer; margin-top:10px;">
                <span style="font-size:18px;">🔥</span>
                <span class="text" id="homePromoText">✨ ማስታወቂያ ለማየት እዚህ ይጫኑ</span>
            </div>
        </div>
        <div class="page" id="page-products">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="pTitle">🛍️ ምርቶች</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div class="product-grid" id="productGrid"><p class="empty-msg">⏳ እየጫነ ...</p></div>
        </div>
        <div class="page" id="page-call">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="callTitle">📞 ይደውሉ</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div class="grid2" style="margin-top:6px;">
                <a href="tel:0931556590" class="card-box" style="text-decoration:none; color:inherit;"><div style="font-size:14px; font-weight:700; color:#fff;">0931556590</div><div style="font-size:9px; color:#8aa3b5;">ኢትዮ ቴሌኮም</div></a>
                <a href="tel:+251799556590" class="card-box" style="text-decoration:none; color:inherit;"><div style="font-size:14px; font-weight:700; color:#fff;">+251799556590</div><div style="font-size:9px; color:#8aa3b5;">ሳፋሪኮም</div></a>
                <a href="tel:+251967386958" class="card-box" style="text-decoration:none; color:inherit;"><div style="font-size:14px; font-weight:700; color:#fff;">+251967386958</div><div style="font-size:9px; color:#8aa3b5;">ሳፋሪኮም</div></a>
                <a href="https://wa.me/251799556590" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:20px; display:block;">💬</span><div style="font-size:9px; color:#8aa3b5;">WhatsApp</div></a>
                <a href="https://t.me/MarshalomTech" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:20px; display:block;">✈️</span><div style="font-size:9px; color:#8aa3b5;">ቴሌግራም</div></a>
            </div>
        </div>
        <div class="page" id="page-social">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="socialTitle">🌐 ማህበራዊ</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div class="grid3" style="margin-top:6px;">
                <a href="https://tiktok.com/@marshalomcctv" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:24px; display:block;">🎵</span><span style="font-size:8px; color:#c0d8e8;">TikTok</span></a>
                <a href="https://youtube.com/@ShalomTechnology" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:24px; display:block;">▶️</span><span style="font-size:8px; color:#c0d8e8;">YouTube</span></a>
                <a href="https://facebook.com/share/1YEeCpFBgp" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:24px; display:block;">📘</span><span style="font-size:8px; color:#c0d8e8;">Facebook</span></a>
                <a href="https://instagram.com/marshalom" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:24px; display:block;">📸</span><span style="font-size:8px; color:#c0d8e8;">Instagram</span></a>
                <a href="https://twitter.com/marshalom" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:24px; display:block;">🐦</span><span style="font-size:8px; color:#c0d8e8;">Twitter/X</span></a>
                <a href="https://linkedin.com/company/marshalom" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:24px; display:block;">💼</span><span style="font-size:8px; color:#c0d8e8;">LinkedIn</span></a>
            </div>
        </div>
        <div class="page" id="page-share">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="shareTitle">👥 ማጋሪያ</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div style="background:rgba(255,255,255,0.03); border-radius:12px; padding:10px; border:1px solid rgba(255,255,255,0.06); font-size:11px; color:#c0d8e8; line-height:1.7; white-space:pre-line; margin-bottom:8px;">
                ✨ እንኳን ደህና መጡ ወደ ማርሻሎም! ✨
                እኛ በኤሌክትሮኒክስ እና በደህንነት ካሜራዎች ላይ ጥራት ያለው አገልግሎት የምንሰጥ ታማኝ የቴክኖሎጂ አጋርዎ ነን።
            </div>
            <button class="btn-primary" onclick="shareChannel()">📤 ቻናላችንን ያጋሩ</button>
            <div class="grid3" style="margin-top:8px;">
                <a href="https://wa.me/?text=Check%20out%20Shalom%20Technology%3A%20https%3A%2F%2Ft.me%2FMarshalomTech" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:18px; display:block;">💬</span><span style="font-size:7px; color:#c0d8e8;">WhatsApp</span></a>
                <a href="https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Ft.me%2FMarshalomTech" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:18px; display:block;">📘</span><span style="font-size:7px; color:#c0d8e8;">Facebook</span></a>
                <a href="https://t.me/share/url?url=https%3A%2F%2Ft.me%2FMarshalomTech" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:18px; display:block;">✈️</span><span style="font-size:7px; color:#c0d8e8;">Telegram</span></a>
                <a href="sms:?body=Check%20out%20Shalom%20Technology%3A%20https%3A%2F%2Ft.me%2FMarshalomTech" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:18px; display:block;">💬</span><span style="font-size:7px; color:#c0d8e8;">SMS</span></a>
                <a href="https://instagram.com/marshalom" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:18px; display:block;">📸</span><span style="font-size:7px; color:#c0d8e8;">Instagram</span></a>
                <a href="https://twitter.com/intent/tweet?text=Check%20out%20Shalom%20Technology%3A%20https%3A%2F%2Ft.me%2FMarshalomTech" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:18px; display:block;">🐦</span><span style="font-size:7px; color:#c0d8e8;">Twitter</span></a>
            </div>
            <div style="background:linear-gradient(135deg,#4a3a1a,#3a2a0a); border-radius:12px; padding:12px; margin-top:10px; text-align:center; border:1px solid #b8a84a;">
                <div style="font-size:20px;">🎁</div>
                <div style="color:#b8a84a; font-weight:700;">ቅናሽ</div>
                <div style="color:#c0d8e8; font-size:12px;">ሁሉም ምርቶች 30% ቅናሽ እስከ ወር መጨረሻ!</div>
            </div>
        </div>
        <div class="page" id="page-news">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="newsTitle">📰 ዜና</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px 10px; margin-bottom:5px; border-left:3px solid #4a9eff;">
                <div style="color:#b8a84a; font-weight:600; font-size:11px;">📸 አዲስ ካሜራ ፊት ብቻ ሳይሆን የእግር ንዝረትን ይለያል!</div>
                <div style="color:#c0d8e8; font-size:10px;">የቻይና ኩባንያ አዲስ AI ካሜራ አስገባ — ሰዎችን በእግራቸው እንቅስቃሴ ይለያል!</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px 10px; margin-bottom:5px; border-left:3px solid #4a9eff;">
                <div style="color:#b8a84a; font-weight:600; font-size:11px;">🚀 በአሜሪካ የሰማይ ላይ ካሜራ ተፈተሸ</div>
                <div style="color:#c0d8e8; font-size:10px;">ሰዎችን ከ5 ኪሎ ሜትር ርቀት የሚያውቅ ካሜራ ተፈተሸ!</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px 10px; margin-bottom:5px; border-left:3px solid #ff6b6b;">
                <div style="color:#ff6b6b; font-weight:600; font-size:11px;">😂 አስቂኝ ዜና!</div>
                <div style="color:#c0d8e8; font-size:10px;">ማርሻሎም ለቦቱ ምስጢር ቁጥር "777" ደብቆታል! 🤫😂</div>
            </div>
        </div>
        <div class="page" id="page-applications">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="applicationsTitle">📱 አፕሊኬሽን</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div id="applicationsGrid" class="product-grid"><p class="empty-msg">⏳ እየጫነ ...</p></div>
        </div>
        <div class="page" id="page-jobs">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="jobsTitle">💼 ክፍት ስራ</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div id="jobsList"><p class="empty-msg">⏳ እየጫነ ...</p></div>
        </div>
        <div class="page" id="page-discount">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="discountTitle">🎁 ቅናሽ</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div id="discountBox" style="background:linear-gradient(135deg,#4a3a1a,#3a2a0a); border-radius:16px; padding:20px 12px; text-align:center; color:#b8a84a; border:1px solid #4a3a1a;">
                <div style="font-size:30px;">🎁</div>
                <div id="discountContent" style="font-size:13px; color:#c0d8e8; margin-top:6px;">⏳ እየጫነ ...</div>
            </div>
        </div>
        <div class="page" id="page-ai">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="aiTitle">🤖 ረዳት</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div id="aiChatWindow" style="background:rgba(0,0,0,0.15); border-radius:12px; padding:8px; height:340px; overflow-y:auto; margin-bottom:8px; display:flex; flex-direction:column; gap:6px;"></div>
            <div style="display:flex; gap:6px;">
                <input type="text" id="aiInput" placeholder="መልእክት ይጻፉ..." class="input-field" style="margin:0; flex:1;" onkeypress="if(event.key==='Enter') sendAIMessage()">
                <button class="btn-primary" style="width:60px; margin:0;" onclick="sendAIMessage()">➤</button>
            </div>
        </div>
        <div class="page" id="page-support">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="supportTitle">🛡️ ድጋፍ</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div style="text-align:center;">
                <div style="font-size:32px;">🛡️</div>
                <p style="color:#c0d8e8; font-size:13px; font-weight:600;">24/7 ደንበኛ ድጋፍ</p>
                <div class="grid3" style="margin-top:6px;">
                    <a href="tel:0931556590" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:28px; display:block;">📞</span><span style="font-size:9px; color:#c0d8e8;">ስልክ</span></a>
                    <a href="https://wa.me/251799556590" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:28px; display:block;">💬</span><span style="font-size:9px; color:#c0d8e8;">ዋትሳፕ</span></a>
                    <a href="https://t.me/MarshalomTech" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:28px; display:block;">✈️</span><span style="font-size:9px; color:#c0d8e8;">ቴሌግራም</span></a>
                </div>
            </div>
        </div>
        <div class="page" id="page-promo">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="promoTitle">📢 ማስታወቂያ</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div id="promoList"><p class="empty-msg">⏳ እየጫነ ...</p></div>
        </div>
        <div class="page" id="page-tips">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="tipsTitle">💡 ምክሮች</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px; margin-bottom:4px;">
                <div style="color:#b8a84a; font-size:11px;">💡 ምክር 1</div>
                <div style="color:#c0d8e8; font-size:11px;">ካሜራ ሲጭኑ የፀሐይ ብርሃን ወደሚያገኝ ቦታ ይጫኑ!</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px; margin-bottom:4px;">
                <div style="color:#b8a84a; font-size:11px;">💡 ምክር 2</div>
                <div style="color:#c0d8e8; font-size:11px;">የካሜራ ስርዓትን በየጊዜው ያሻሽሉ!</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px;">
                <div style="color:#b8a84a; font-size:11px;">💡 ምክር 3</div>
                <div style="color:#c0d8e8; font-size:11px;">ካሜራዎ በ4G/Wi-Fi ሲገናኝ የይለፍ ቃል ጠንካራ ያድርጉ!</div>
            </div>
        </div>
        <div class="page" id="page-banks">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="banksTitle">🏦 ባንክ</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div id="banksList"><p class="empty-msg">⏳ እየጫነ ...</p></div>
        </div>
        <div class="page" id="page-feedback">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="feedbackTitle">💬 አስተያየት</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div style="background:rgba(255,255,255,0.03); border-radius:12px; padding:10px; margin-bottom:10px;">
                <div style="color:#b8a84a; font-size:12px; font-weight:600; margin-bottom:6px;">✍️ ህዝባዊ አስተያየት</div>
                <textarea id="testimonialInput" class="input-field" rows="2" placeholder="ስለ አገልግሎታችን ምን ይላሉ?"></textarea>
                <button class="btn-primary" onclick="submitTestimonial()">📤 ላክ</button>
            </div>
            <div style="background:rgba(74,158,255,0.04); border-radius:12px; padding:10px; margin-bottom:10px; border:1px solid rgba(74,158,255,0.08);">
                <div style="color:#4a9eff; font-size:12px; font-weight:600; margin-bottom:6px;">📩 የግል መልእክት ወደ አድሚን</div>
                <textarea id="privateMessageInput" class="input-field" rows="2" placeholder="መልእክትዎን ይጻፉ..."></textarea>
                <button class="btn-primary gold" onclick="submitPrivateMessage()">📤 ላክ</button>
            </div>
            <div id="testimonialsList"><p class="empty-msg">⏳ እየጫነ ...</p></div>
        </div>
        <div class="page" id="page-admin">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="adminTitle">⚙️ አድሚን</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div id="adminContent"><p class="empty-msg">⏳ በማረጋገጥ ላይ...</p></div>
        </div>
        <div class="page" id="page-teamleader">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="tlTitle">👔 ቲም ሊደር</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div id="tlLoginBox">
                <input type="text" id="tlUsername" placeholder="Username" class="input-field">
                <input type="password" id="tlPassword" placeholder="Password" class="input-field">
                <button class="btn-primary" onclick="teamLeaderLogin()">🔓 ግባ</button>
            </div>
            <div id="tlContent" style="display:none;"></div>
        </div>
        <div class="page" id="page-employee">
            <div class="page-title">
                <button class="back-btn" onclick="showPage('page-home')">‹</button>
                <span id="empTitle">👤 ሰራተኛ</span>
                <button class="home-btn" onclick="showPage('page-home')">🏠</button>
            </div>
            <div id="empLoginBox">
                <input type="text" id="empUsername" placeholder="Username" class="input-field">
                <input type="password" id="empPassword" placeholder="Password" class="input-field">
                <button class="btn-primary" onclick="employeeLogin()">🔓 ግባ</button>
            </div>
            <div id="empContent" style="display:none;"></div>
        </div>
    </div>
    <div class="ticker">
        <div class="ticker-wrap">
            <span class="ticker-item">🛍️ ምርቶች</span>
            <span class="ticker-item">📞 ይደውሉ</span>
            <span class="ticker-item">🌐 ማህበራዊ</span>
            <span class="ticker-item">👥 ማጋሪያ</span>
            <span class="ticker-item">📰 ዜና</span>
            <span class="ticker-item">📱 አፕሊኬሽን</span>
            <span class="ticker-item">💼 ስራ</span>
            <span class="ticker-item">🎁 ቅናሽ</span>
            <span class="ticker-item">🤖 ረዳት</span>
            <span class="ticker-item">🛡️ ድጋፍ</span>
            <span class="ticker-item">📢 ማስታወቂያ</span>
            <span class="ticker-item">💡 ምክሮች</span>
            <span class="ticker-item">🏦 ባንክ</span>
            <span class="ticker-item">💬 አስተያየት</span>
            <span class="ticker-item">⚙️ አድሚን</span>
            <span class="ticker-item">👔 ቲም ሊደር</span>
            <span class="ticker-item">👤 ሰራተኛ</span>
        </div>
    </div>
    <div class="bottom-nav">
        <div class="nav-item active" onclick="showPage('page-home')"><span class="icon">🏠</span><span data-key="n1">መነሻ</span></div>
        <div class="nav-item" onclick="showPage('page-products')"><span class="icon">🛍️</span><span data-key="n2">ምርቶች</span></div>
        <div class="nav-item" onclick="showPage('page-ai')"><span class="icon">🤖</span><span data-key="n3">ረዳት</span></div>
        <div class="nav-item" onclick="showPage('page-share')"><span class="icon">👥</span><span data-key="n4">አጋራ</span></div>
        <div class="nav-item" onclick="showPage('page-jobs')"><span class="icon">💼</span><span data-key="n5">ስራ</span></div>
    </div>
</div>
<script>
const tg = window.Telegram.WebApp;
tg.ready(); tg.expand();
const initData = tg.initData;
let currentLang = 'am';
let allProducts = [];
let allPromos = [];
let allJobs = [];
let allApplications = [];
let allBanks = [];
let allTestimonials = [];

const translations = {
    am: { title:'Shalom Technology', sub:'✨ የእርስዎ የደህንነት አጋር ✨', m1:'ምርቶች',m2:'ይደውሉ',m3:'ማህበራዊ',m4:'ማጋሪያ',m5:'ዜና',m6:'አፕሊኬሽን',m7:'ክፍት ስራ',m8:'ቅናሽ', m9:'ረዳት',m10:'ድጋፍ',m11:'ማስታወቂያ',m12:'ምክሮች',m13:'ባንክ',m14:'አስተያየት',m15:'አድሚን',m16:'ቲም ሊደር',m17:'ሰራተኛ', n1:'መነሻ',n2:'ምርቶች',n3:'ረዳት',n4:'አጋራ',n5:'ስራ', pTitle:'🛍️ ምርቶች', callTitle:'📞 ይደውሉ', socialTitle:'🌐 ማህበራዊ', shareTitle:'👥 ማጋሪያ', newsTitle:'📰 ዜና', applicationsTitle:'📱 አፕሊኬሽን', jobsTitle:'💼 ክፍት ስራ', discountTitle:'🎁 ቅናሽ', aiTitle:'🤖 ረዳት', supportTitle:'🛡️ ድጋፍ', promoTitle:'📢 ማስታወቂያ', tipsTitle:'💡 ምክሮች', banksTitle:'🏦 ባንክ', feedbackTitle:'💬 አስተያየት', adminTitle:'⚙️ አድሚን', tlTitle:'👔 ቲም ሊደር', empTitle:'👤 ሰራተኛ', askPrice:'💬 ዋጋ ጠይቁ', applyBtn:'📝 አመልክት', phonePlaceholder:'ስልክ ቁጥር' },
    en: { title:'Shalom Technology', sub:'✨ Your Security Partner ✨', m1:'Products',m2:'Call',m3:'Social',m4:'Share',m5:'News',m6:'Applications',m7:'Jobs',m8:'Discount', m9:'Assistant',m10:'Support',m11:'Promo',m12:'Tips',m13:'Banks',m14:'Feedback',m15:'Admin',m16:'Team Leader',m17:'Employee', n1:'Home',n2:'Products',n3:'Assistant',n4:'Share',n5:'Jobs', pTitle:'🛍️ Products', callTitle:'📞 Call', socialTitle:'🌐 Social', shareTitle:'👥 Share', newsTitle:'📰 News', applicationsTitle:'📱 Applications', jobsTitle:'💼 Jobs', discountTitle:'🎁 Discount', aiTitle:'🤖 Assistant', supportTitle:'🛡️ Support', promoTitle:'📢 Promo', tipsTitle:'💡 Tips', banksTitle:'🏦 Banks', feedbackTitle:'💬 Feedback', adminTitle:'⚙️ Admin', tlTitle:'👔 Team Leader', empTitle:'👤 Employee', askPrice:'💬 Ask Price', applyBtn:'📝 Apply', phonePlaceholder:'Phone Number' },
    ti: { title:'Shalom Technology', sub:'✨ ናይ ሓልዎት ኣጋርኩም ✨', m1:'ምርቶች',m2:'ደውሉ',m3:'ማህበራዊ',m4:'ኣጋሩ',m5:'ዜና',m6:'አፕሊኬሽን',m7:'ስራ',m8:'ቅናሽ', m9:'ረዳት',m10:'ድጋፍ',m11:'ማስታወቂያ',m12:'ምኽርታት',m13:'ባንክ',m14:'አስተያየት',m15:'ኣድሚን',m16:'መራሒ ጉጅለ',m17:'ሰራተኛ', n1:'መነሻ',n2:'ምርቶች',n3:'ረዳት',n4:'ኣጋሩ',n5:'ስራ', pTitle:'🛍️ ምርቶች', callTitle:'📞 ደውሉ', socialTitle:'🌐 ማህበራዊ', shareTitle:'👥 ኣጋሩ', newsTitle:'📰 ዜና', applicationsTitle:'📱 አፕሊኬሽን', jobsTitle:'💼 ስራ', discountTitle:'🎁 ቅናሽ', aiTitle:'🤖 ረዳት', supportTitle:'🛡️ ድጋፍ', promoTitle:'📢 ማስታወቂያ', tipsTitle:'💡 ምኽርታት', banksTitle:'🏦 ባንክ', feedbackTitle:'💬 አስተያየት', adminTitle:'⚙️ ኣድሚን', tlTitle:'👔 መራሒ ጉጅለ', empTitle:'👤 ሰራተኛ', askPrice:'💬 ዋጋ ሕተት', applyBtn:'📝 ኣመልክት', phonePlaceholder:'ቁጽሪ ስልኪ' },
    or: { title:'Shalom Technology', sub:'✨ Michuu Nageenya Keessanii ✨', m1:'Oomishaalee',m2:'Bilbilaa',m3:'Hawaasa',m4:'Qooda',m5:'Oduu',m6:'Applications',m7:'Hojii',m8:'Hir\'aa', m9:'Gargaaraa',m10:'Deggersa',m11:'Beeksisa',m12:'Gorsa',m13:'Baankii',m14:'Yaada',m15:'Admin',m16:'Hoogganaa',m17:'Hojjetaa', n1:'Mana',n2:'Oomishaalee',n3:'Gargaaraa',n4:'Qooda',n5:'Hojii', pTitle:'🛍️ Oomishaalee', callTitle:'📞 Bilbilaa', socialTitle:'🌐 Hawaasa', shareTitle:'👥 Qooda', newsTitle:'📰 Oduu', applicationsTitle:'📱 Applications', jobsTitle:'💼 Hojii', discountTitle:'🎁 Hir\'aa', aiTitle:'🤖 Gargaaraa', supportTitle:'🛡️ Deggersa', promoTitle:'📢 Beeksisa', tipsTitle:'💡 Gorsa', banksTitle:'🏦 Baankii', feedbackTitle:'💬 Yaada', adminTitle:'⚙️ Admin', tlTitle:'👔 Hoogganaa', empTitle:'👤 Hojjetaa', askPrice:'💬 Gaafii Gatii', applyBtn:'📝 Iyyadhu', phonePlaceholder:'Lakkoofsa bilbila' }
};

function switchLanguage(lang) {
    currentLang = lang;
    const t = translations[lang];
    document.querySelectorAll('.lang-selector button').forEach(b => b.classList.toggle('active', b.dataset.lang === lang));
    document.getElementById('mainTitle').textContent = t.title;
    document.getElementById('mainSub').textContent = t.sub;
    document.querySelectorAll('[data-key]').forEach(el => {
        const key = el.dataset.key;
        if (t[key]) el.textContent = t[key];
    });
    renderProducts(); renderPromos(); renderJobs(); renderApplications(); renderBanks(); renderTestimonials();
}

function toggleHomeMenu() {
    const grid = document.getElementById('homeMenuGrid');
    grid.style.display = grid.style.display === 'none' ? 'block' : 'none';
}

function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const target = document.getElementById(pageId);
    if (target) target.classList.add('active');
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const navMap = {'page-home':0,'page-products':1,'page-ai':2,'page-share':3,'page-jobs':4};
    if (navMap[pageId] !== undefined) {
        document.querySelectorAll('.nav-item')[navMap[pageId]].classList.add('active');
    }
    if (pageId === 'page-products') loadProducts();
    if (pageId === 'page-promo') loadPromos();
    if (pageId === 'page-jobs') loadJobs();
    if (pageId === 'page-applications') loadApplications();
    if (pageId === 'page-banks') loadBanks();
    if (pageId === 'page-feedback') loadTestimonials();
}

function shareChannel() {
    tg.openTelegramLink('https://t.me/share/url?url=' + encodeURIComponent('https://t.me/MarshalomTech'));
}

async function loadProducts() {
    const res = await fetch('/api/products');
    allProducts = await res.json();
    renderProducts();
}
function renderProducts() {
    const t = translations[currentLang];
    const el = document.getElementById('productGrid');
    if (!allProducts || !allProducts.length) { el.innerHTML = '<p class="empty-msg">ምንም ምርት የለም</p>'; return; }
    el.innerHTML = allProducts.map((p, idx) => `
        <div class="product-card" style="animation-delay:${idx * 0.08}s;">
            <div class="slider-container">
                <img class="slider-img" src="${p.photos && p.photos[0] ? p.photos[0] : (p.photo_url || '/static/logo.jpg')}" onclick='openFullscreen(this.src, ${JSON.stringify(p.name)})' />
                ${p.photos && p.photos.length > 1 ? `<div class="slider-dots">${p.photos.map((_, i) => `<span class="dot ${i===0?'active':''}" onclick="changeSlide(${idx}, ${i})"></span>`).join('')}</div>` : ''}
            </div>
            <div class="info">
                <div class="name">${p.name}</div>
                <div class="desc">${p.description || ''}</div>
                <button class="ask-btn" onclick='askPrice(${p.id}, ${JSON.stringify(p.name)})'>${t.askPrice}</button>
            </div>
        </div>
    `).join('');
}
function changeSlide(idx, dotIdx) {
    const container = document.querySelectorAll('.product-card')[idx];
    if (!container) return;
    const img = container.querySelector('.slider-img');
    const product = allProducts[idx];
    if (!product || !product.photos || !product.photos[dotIdx]) return;
    img.src = product.photos[dotIdx];
    container.querySelectorAll('.dot').forEach((d, i) => d.classList.toggle('active', i === dotIdx));
}
function openFullscreen(src, name) {
    const overlay = document.createElement('div');
    overlay.className = 'fullscreen-overlay';
    overlay.innerHTML = `<span class="close-fs" onclick="this.parentElement.remove()">✕</span><img src="${src}"/><div style="color:#fff; margin-top:12px; font-size:14px; font-weight:600;">${name}</div>`;
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
    document.body.appendChild(overlay);
}
async function askPrice(productId, productName) {
    await fetch('/api/ask_price', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({initData, product_id:productId, product_name:productName})
    });
    alert('✅ ጥያቄዎ ተልኳል!');
}

async function loadPromos() {
    const res = await fetch('/api/promos');
    allPromos = await res.json();
    renderPromos();
}
function renderPromos() {
    const t = translations[currentLang];
    const el = document.getElementById('promoList');
    const promos = (allPromos || []).slice(0,3);
    if (!promos.length) { el.innerHTML = '<p class="empty-msg">ምንም ማስታወቂያ የለም</p>'; return; }
    el.innerHTML = promos.map((p, i) => `
        <div class="promo-anim-card" style="display:flex; gap:8px; align-items:center; background:rgba(255,255,255,0.03); border-radius:10px; padding:8px; border-left:4px solid #4a9eff; margin-bottom:6px;">
            <div style="flex:1; color:#c0d8e8; font-size:11px;">${p[currentLang] || p.am}</div>
            <img src="/static/product${(i%5)+1}.jpg" style="width:60px; height:60px; border-radius:8px; object-fit:cover; flex-shrink:0;" />
        </div>
    `).join('');
    const homeText = document.getElementById('homePromoText');
    if (promos.length && homeText) homeText.textContent = (promos[0][currentLang] || promos[0].am);
    const discountEl = document.getElementById('discountContent');
    if (discountEl && promos.length) discountEl.textContent = promos[0][currentLang] || promos[0].am;
}

async function loadJobs() {
    const res = await fetch('/api/jobs');
    allJobs = await res.json();
    renderJobs();
}
function renderJobs() {
    const t = translations[currentLang];
    const el = document.getElementById('jobsList');
    if (!allJobs || !allJobs.length) { el.innerHTML = '<p class="empty-msg">ለጊዜው ክፍት የስራ ቦታ የለም</p>'; return; }
    el.innerHTML = allJobs.map(j => `
        <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px; margin-bottom:6px; border-left:4px solid #4a9eff;">
            <h3 style="color:#fff; font-size:12px;">${j.title}</h3>
            <p style="color:#9bb0c0; font-size:10px;">${j.location || ''}</p>
            <p style="color:#c0d8e8; font-size:10px; margin-top:4px;">${j.description || ''}</p>
            ${j.pdf_url ? `<a href="${j.pdf_url}" target="_blank" style="color:#4a9eff; font-size:10px;">📄 PDF ዝርዝር አውርድ</a>` : ''}
            <input type="text" id="phone-${j.id}" placeholder="${t.phonePlaceholder}" class="input-field" style="margin-top:6px;">
            <button class="btn-primary" onclick="applyJob(${j.id}, ${JSON.stringify(j.title)})">${t.applyBtn}</button>
        </div>
    `).join('');
}
async function applyJob(jobId, jobTitle) {
    const phone = document.getElementById('phone-'+jobId).value;
    await fetch('/api/jobs/apply', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({initData, job_id:jobId, job_title:jobTitle, phone})
    });
    alert('✅ ማመልከቻዎ ተልኳል!');
}

async function loadApplications() {
    const res = await fetch('/api/applications');
    allApplications = await res.json();
    renderApplications();
}
function renderApplications() {
    const el = document.getElementById('applicationsGrid');
    if (!allApplications || !allApplications.length) { el.innerHTML = '<p class="empty-msg">ምንም አፕሊኬሽን የለም</p>'; return; }
    el.innerHTML = allApplications.map(a => `
        <div class="product-card">
            <img class="promo-img" src="${a.photo_url || '/static/logo.jpg'}" />
            <div class="info">
                <div class="name">${a.name}</div>
                ${a.file_url ? `<a href="${a.file_url}" target="_blank" class="ask-btn" style="display:block; text-decoration:none;">⬇️ አውርድ</a>` : ''}
            </div>
        </div>
    `).join('');
}

async function loadBanks() {
    const res = await fetch('/api/config/banks');
    allBanks = await res.json();
    renderBanks();
}
function renderBanks() {
    const el = document.getElementById('banksList');
    const banks = allBanks && allBanks.length ? allBanks : [
        {bank:'የንግድ ባንክ', number:'1000453578058', owner:'Marshalom Tesfay'},
        {bank:'ቴሌብር 1', number:'0931556590', owner:'Marshalom Tesfay'},
        {bank:'ቴሌብር 2', number:'0967386958', owner:'Lwam Alem'}
    ];
    el.innerHTML = banks.map(b => `
        <div class="card-box" style="cursor:default; text-align:left; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="color:#b8a84a; font-weight:600; font-size:12px;">${b.bank}</div>
                <div style="color:#fff; font-size:14px; font-weight:700;">${b.number}</div>
                <div style="color:#8aa3b5; font-size:10px;">${b.owner}</div>
            </div>
            <button onclick="copyNumber('${b.number}', this)" style="background:#2b3a4a; border:none; color:#4a9eff; padding:6px 10px; border-radius:8px; font-size:10px;">📋 ኮፒ</button>
        </div>
    `).join('');
}
function copyNumber(number, btn) {
    navigator.clipboard.writeText(number).then(() => {
        btn.textContent = '✅';
        setTimeout(() => { btn.textContent = '📋 ኮፒ'; }, 1500);
    }).catch(() => {
        const ta = document.createElement('textarea');
        ta.value = number;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        btn.textContent = '✅';
        setTimeout(() => { btn.textContent = '📋 ኮፒ'; }, 1500);
    });
}

async function loadTestimonials() {
    const res = await fetch('/api/testimonials');
    allTestimonials = await res.json();
    renderTestimonials();
}
function renderTestimonials() {
    const el = document.getElementById('testimonialsList');
    if (!allTestimonials || !allTestimonials.length) { el.innerHTML = '<p class="empty-msg">ምንም አስተያየት የለም</p>'; return; }
    el.innerHTML = allTestimonials.map(t => `
        <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px; margin-bottom:6px; border-left:3px solid #b8a84a;">
            <div style="color:#b8a84a; font-size:11px; font-weight:600;">${t.name} ${t.username ? '(@'+t.username+')' : ''}</div>
            <div style="color:#c0d8e8; font-size:11px;">${t.message}</div>
        </div>
    `).join('');
}
async function submitTestimonial() {
    const message = document.getElementById('testimonialInput').value.trim();
    if (!message) return;
    await fetch('/api/testimonials/add', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({initData, message})
    });
    document.getElementById('testimonialInput').value = '';
    loadTestimonials();
    alert('🙏 አመሰግናለሁ!');
}
async function submitPrivateMessage() {
    const message = document.getElementById('privateMessageInput').value.trim();
    if (!message) return;
    await fetch('/api/message/send', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({initData, recipient_type:'admin', message})
    });
    document.getElementById('privateMessageInput').value = '';
    alert('✅ መልእክትዎ ተልኳል!');
}

function addChatBubble(text, isUser) {
    const win = document.getElementById('aiChatWindow');
    const bubble = document.createElement('div');
    bubble.style.cssText = `max-width:80%; padding:8px 10px; border-radius:12px; font-size:11px; line-height:1.5; white-space:pre-line; ${isUser ? 'align-self:flex-end; background:#4a9eff; color:#fff;' : 'align-self:flex-start; background:#232e3c; color:#e0edf5;'}`;
    bubble.textContent = text;
    win.appendChild(bubble);
    win.scrollTop = win.scrollHeight;
}
async function sendAIMessage() {
    const input = document.getElementById('aiInput');
    const message = input.value.trim();
    if (!message) return;
    addChatBubble(message, true);
    input.value = '';
    addChatBubble('⏳ ...', false);
    const win = document.getElementById('aiChatWindow');
    const res = await fetch('/api/ai_chat', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({initData, message})
    });
    const data = await res.json();
    win.removeChild(win.lastChild);
    addChatBubble(data.reply || 'ስህተት', false);
}

async function employeeLogin() {
    const username = document.getElementById('empUsername').value;
    const password = document.getElementById('empPassword').value;
    const res = await fetch('/api/employee/login', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({username, password})
    });
    const data = await res.json();
    if (!data.ok) { alert('❌ የተሳሳተ'); return; }
    document.getElementById('empLoginBox').style.display = 'none';
    const el = document.getElementById('empContent');
    el.style.display = 'block';
    const p = data.profile;
    el.innerHTML = `
        <div style="background:rgba(255,255,255,0.04); border-radius:14px; padding:14px;">
            <div style="text-align:center; font-size:32px;">👤</div>
            <div style="text-align:center; color:#fff; font-weight:700; font-size:14px;">${p.full_name}</div>
            <div style="text-align:center; color:#8aa3b5; font-size:11px;">${p.position}</div>
            <div style="font-size:11px; color:#c0d8e8; line-height:1.8; margin-top:8px;">
                <b>💰 ደመወዝ:</b> ${p.salary || '-'}<br>
                <b>🎁 ቦነስ:</b><br>${(p.bonus || 'የለም').replace(/\\n/g,'<br>')}<br>
                <b>⚠️ ማስጠንቀቂያ:</b><br>${(p.warnings || 'የለም').replace(/\\n/g,'<br>')}<br>
                <b>📋 ስራዎች:</b><br>${(p.tasks || 'የለም').replace(/\\n/g,'<br>')}
            </div>
        </div>
    `;
}
async function teamLeaderLogin() {
    const username = document.getElementById('tlUsername').value;
    const password = document.getElementById('tlPassword').value;
    const res = await fetch('/api/employee/login', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({username, password})
    });
    const data = await res.json();
    if (!data.ok || data.profile.role !== 'team_leader') { alert('❌ የተሳሳተ'); return; }
    document.getElementById('tlLoginBox').style.display = 'none';
    const el = document.getElementById('tlContent');
    el.style.display = 'block';
    const p = data.profile;
    const empRes = await fetch('/api/team/employees', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({tl_username:username, tl_password:password})
    });
    const employees = await empRes.json();
    el.innerHTML = `
        <div style="text-align:center; margin-bottom:10px;">
            <div style="font-size:28px;">👔</div>
            <div style="color:#fff; font-weight:700;">${p.full_name}</div>
            <div style="color:#8aa3b5; font-size:11px;">🌟 ቲም ሊደር</div>
        </div>
        <div id="tlEmployeeList">
            ${(employees || []).map(e => `
                <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px; margin-bottom:6px;">
                    <b style="color:#fff; font-size:12px;">${e.full_name}</b> <span style="color:#8aa3b5; font-size:10px;">(${e.position})</span>
                    <div style="display:flex; gap:4px; margin-top:6px;">
                        <button style="flex:1; font-size:9px; padding:5px; border:none; border-radius:6px; background:#2b3a4a; color:#fff;" onclick="tlResetPassword('${e.username}')">🔐 Reset</button>
                        <button style="flex:1; font-size:9px; padding:5px; border:none; border-radius:6px; background:#2b3a4a; color:#fff;" onclick="tlAssignTask('${e.username}')">📋 Task</button>
                        <button style="flex:1; font-size:9px; padding:5px; border:none; border-radius:6px; background:#2b3a4a; color:#fff;" onclick="tlGiveBonus('${e.username}')">🎁 Bonus</button>
                    </div>
                </div>
            `).join('') || '<p class="empty-msg">ምንም ሰራተኛ የለም</p>'}
        </div>
    `;
}
async function tlResetPassword(username) {
    const res = await fetch('/api/team/reset_password', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({tl_username:document.getElementById('tlUsername').value, tl_password:document.getElementById('tlPassword').value, username})
    });
    const data = await res.json();
    if (data.ok) alert('✅ አዲስ password: ' + data.temp_password);
}
async function tlAssignTask(username) {
    const task = prompt('📋 አዲስ ስራ:');
    if (!task) return;
    await fetch('/api/team/update', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({tl_username:document.getElementById('tlUsername').value, tl_password:document.getElementById('tlPassword').value, username, field:'tasks', value:task})
    });
    alert('✅ ተመድቧል!');
}
async function tlGiveBonus(username) {
    const bonus = prompt('🎁 ቦነስ:');
    if (!bonus) return;
    await fetch('/api/team/update', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({tl_username:document.getElementById('tlUsername').value, tl_password:document.getElementById('tlPassword').value, username, field:'bonus', value:bonus})
    });
    alert('✅ ተጨምሯል!');
}

loadProducts(); loadPromos(); loadJobs(); loadApplications(); loadBanks(); loadTestimonials();
</script>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="am">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Admin Dashboard</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',system-ui,sans-serif; }
body { background:#0b1219; color:#fff; padding:20px; }
.dash-container { max-width:600px; margin:0 auto; }
h1 { font-size:24px; margin-bottom:20px; color:#4a9eff; }
.section { background:rgba(255,255,255,0.04); border-radius:12px; padding:16px; margin-bottom:16px; border:1px solid rgba(255,255,255,0.06); }
.section h3 { color:#b8a84a; font-size:16px; margin-bottom:10px; }
.section label { color:#c0d8e8; font-size:13px; display:block; margin:8px 0 4px; }
.section input, .section textarea, .section select { width:100%; padding:8px 12px; border-radius:8px; border:1px solid #2b3a4a; background:#232e3c; color:#fff; font-size:14px; outline:none; margin-bottom:8px; }
.section textarea { resize:vertical; min-height:60px; }
.save-btn { background:#4a9eff; color:#fff; border:none; padding:10px 20px; border-radius:30px; font-size:14px; font-weight:600; cursor:pointer; width:100%; transition:all 0.2s; }
.save-btn:active { transform:scale(0.97); }
.del-btn { background:#ff6b6b; color:#fff; border:none; padding:4px 10px; border-radius:16px; font-size:11px; cursor:pointer; margin-left:8px; }
.list-item { background:rgba(255,255,255,0.03); border-radius:8px; padding:8px 12px; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center; font-size:13px; }
.list-item .del { color:#ff6b6b; cursor:pointer; }
.drag-item { background:rgba(255,255,255,0.05); border-radius:8px; padding:8px 12px; margin-bottom:4px; display:flex; justify-content:space-between; align-items:center; cursor:grab; border:1px solid rgba(255,255,255,0.05); }
.drag-item:active { cursor:grabbing; }
.stats-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px; }
.stat-box { background:rgba(255,255,255,0.04); border-radius:8px; padding:10px; text-align:center; }
.stat-num { font-size:20px; font-weight:700; }
.stat-label { font-size:10px; color:#8aa3b5; }
.status-msg { color:#4aff8a; text-align:center; margin-top:8px; font-size:13px; }
.empty-msg { text-align:center; color:#6a8a9e; padding:20px 0; }
</style>
</head>
<body>
<div class="dash-container">
    <h1>⚙️ Admin Dashboard</h1>
    <div id="statusMsg" class="status-msg"></div>
    <div class="section">
        <h3>📊 ስታት</h3>
        <div class="stats-grid" id="statsGrid">
            <div class="stat-box"><div class="stat-num" id="statCustomers">0</div><div class="stat-label">👥 ደንበኞች</div></div>
            <div class="stat-box"><div class="stat-num" id="statMessages">0</div><div class="stat-label">💬 መልእክቶች</div></div>
            <div class="stat-box"><div class="stat-num" id="statInquiries">0</div><div class="stat-label">💰 የዋጋ ጥያቄ</div></div>
            <div class="stat-box"><div class="stat-num" id="statProducts">0</div><div class="stat-label">🛍️ ምርቶች</div></div>
            <div class="stat-box"><div class="stat-num" id="statPromos">0</div><div class="stat-label">📢 ማስታወቂያ</div></div>
            <div class="stat-box"><div class="stat-num" id="statApps">0</div><div class="stat-label">📱 አፕሊኬሽን</div></div>
        </div>
    </div>
    <div class="section">
        <h3>📌 የገጽ ቅደም ተከተል (Drag & Drop)</h3>
        <div id="pageOrderList"></div>
        <button class="save-btn" onclick="savePageOrder()">💾 ቅደም ተከተል አስቀምጥ</button>
    </div>
    <div class="section">
        <h3>➕ አዲስ ገጽ ፍጠር</h3>
        <input type="text" id="newPageTitle" placeholder="የገጹ ርዕስ">
        <input type="text" id="newPageIcon" placeholder="አዶ (ለምሳሌ 📄)">
        <textarea id="newPageContent" placeholder="የገጹ ይዘት"></textarea>
        <button class="save-btn" onclick="createPage()">📄 ገጽ ፍጠር</button>
        <div id="pagesList"></div>
    </div>
    <div class="section">
        <h3>🎨 ጭብጥ ማስተካከያ</h3>
        <label>ዋና ቀለም</label>
        <input type="color" id="themePrimary" value="#4a9eff">
        <label>የካርድ ቀለም</label>
        <input type="color" id="themeCard" value="#17212b">
        <label>የፊደል አይነት</label>
        <select id="themeFont">
            <option value="Segoe UI">Segoe UI</option>
            <option value="Arial">Arial</option>
            <option value="Times New Roman">Times New Roman</option>
        </select>
        <button class="save-btn" onclick="saveTheme()">💾 ጭብጥ አስቀምጥ</button>
    </div>
    <div class="section">
        <h3>⚙️ የስርዓት ምርጫዎች</h3>
        <label>የቦት ስም</label>
        <input type="text" id="settingsBotName" value="MarshalomSupportBot">
        <label>የእንኳን ደህና መጡ መልእክት</label>
        <input type="text" id="settingsWelcome" value="✨ እንኳን ደህና መጡ!">
        <label>የስራ ሰዓት</label>
        <input type="text" id="settingsHours" value="8:00 - 22:00">
        <button class="save-btn" onclick="saveSettings()">💾 ምርጫዎች አስቀምጥ</button>
    </div>
    <div class="section">
        <h3>🧩 አዲስ ባህሪ ጨምር</h3>
        <input type="text" id="newFeatureName" placeholder="የባህሪው ስም">
        <input type="text" id="newFeatureIcon" placeholder="አዶ (ለምሳሌ ⭐)">
        <button class="save-btn" onclick="addFeature()">➕ ባህሪ ጨምር</button>
        <div id="featuresList"></div>
    </div>
</div>
<script>
const tg = window.Telegram.WebApp;
tg.ready(); tg.expand();
const initData = tg.initData;
let currentPageOrder = [];
let currentPages = [];
let currentFeatures = [];

async function loadStats() {
    const res = await fetch('/api/admin/stats', {headers:{'X-Init-Data':initData}});
    const s = await res.json();
    if (s.customers !== undefined) {
        document.getElementById('statCustomers').textContent = s.customers;
        document.getElementById('statMessages').textContent = s.messages;
        document.getElementById('statInquiries').textContent = s.price_inquiries;
        document.getElementById('statProducts').textContent = s.products;
        document.getElementById('statPromos').textContent = s.promos;
    }
    const appRes = await fetch('/api/applications');
    const apps = await appRes.json();
    document.getElementById('statApps').textContent = apps.length || 0;
}

async function loadPageOrder() {
    const res = await fetch('/api/admin/page_order', {headers:{'X-Init-Data':initData}});
    currentPageOrder = await res.json();
    renderPageOrder();
}

function renderPageOrder() {
    const el = document.getElementById('pageOrderList');
    const defaultPages = ['page-home','page-products','page-call','page-social','page-share','page-news','page-applications','page-jobs','page-discount','page-ai','page-support','page-promo','page-tips','page-banks','page-feedback','page-admin','page-teamleader','page-employee'];
    const order = currentPageOrder.length ? currentPageOrder : defaultPages;
    el.innerHTML = order.map((p, i) => `
        <div class="drag-item" draggable="true" data-index="${i}" data-id="${p}">
            <span>${i+1}. ${p}</span>
            <span style="color:#6a8a9e; font-size:11px;">↕</span>
        </div>
    `).join('');
    let dragStart = null;
    el.querySelectorAll('.drag-item').forEach(item => {
        item.addEventListener('dragstart', (e) => {
            dragStart = parseInt(item.dataset.index);
            item.style.opacity = '0.5';
        });
        item.addEventListener('dragend', () => { item.style.opacity = '1'; });
        item.addEventListener('dragover', (e) => { e.preventDefault(); });
        item.addEventListener('drop', (e) => {
            e.preventDefault();
            const dragEnd = parseInt(item.dataset.index);
            if (dragStart !== null && dragStart !== dragEnd) {
                const items = order;
                const [removed] = items.splice(dragStart, 1);
                items.splice(dragEnd, 0, removed);
                currentPageOrder = items;
                renderPageOrder();
            }
        });
    });
}

async function savePageOrder() {
    await fetch('/api/admin/page_order', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data':initData},
        body:JSON.stringify({order:currentPageOrder})
    });
    showStatus('✅ ቅደም ተከተል ተቀምጧል!');
}

async function createPage() {
    const title = document.getElementById('newPageTitle').value.trim();
    const icon = document.getElementById('newPageIcon').value.trim() || '📄';
    const content = document.getElementById('newPageContent').value.trim();
    if (!title) { alert('ርዕስ ያስፈልጋል'); return; }
    await fetch('/api/admin/custom_pages', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data':initData},
        body:JSON.stringify({title, icon, content})
    });
    document.getElementById('newPageTitle').value = '';
    document.getElementById('newPageIcon').value = '';
    document.getElementById('newPageContent').value = '';
    showStatus('✅ ገጽ ተፈጥሯል!');
    loadPages();
}

async function loadPages() {
    const res = await fetch('/api/custom_pages');
    currentPages = await res.json();
    const el = document.getElementById('pagesList');
    if (!currentPages.length) { el.innerHTML = '<p class="empty-msg">ምንም ብጁ ገጽ የለም</p>'; return; }
    el.innerHTML = currentPages.map(p => `
        <div class="list-item">
            <span>${p.icon || '📄'} ${p.title}</span>
            <span class="del" onclick="deletePage(${p.id})">🗑️</span>
        </div>
    `).join('');
}

async function deletePage(id) {
    if (!confirm('እርግጠኛ ነህ?')) return;
    await fetch(`/api/admin/custom_pages/${id}`, {method:'DELETE', headers:{'X-Init-Data':initData}});
    showStatus('🗑️ ገጽ ተሰርዟል');
    loadPages();
}

async function saveTheme() {
    const theme = {
        primary_color: document.getElementById('themePrimary').value,
        card_color: document.getElementById('themeCard').value,
        font_family: document.getElementById('themeFont').value
    };
    await fetch('/api/admin/theme', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data':initData},
        body:JSON.stringify(theme)
    });
    showStatus('✅ ጭብጥ ተቀምጧል!');
}

async function saveSettings() {
    const settings = {
        bot_name: document.getElementById('settingsBotName').value,
        welcome_message: document.getElementById('settingsWelcome').value,
        working_hours: document.getElementById('settingsHours').value
    };
    await fetch('/api/admin/settings', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data':initData},
        body:JSON.stringify(settings)
    });
    showStatus('✅ ምርጫዎች ተቀምጠዋል!');
}

async function addFeature() {
    const name = document.getElementById('newFeatureName').value.trim();
    const icon = document.getElementById('newFeatureIcon').value.trim() || '🧩';
    if (!name) { alert('ስም ያስፈልጋል'); return; }
    await fetch('/api/admin/custom_pages', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data':initData},
        body:JSON.stringify({title:name, icon:icon, content:'# ባህሪ\\nአዲስ ባህሪ እዚህ ይጨመራል'})
    });
    document.getElementById('newFeatureName').value = '';
    document.getElementById('newFeatureIcon').value = '';
    showStatus('✅ ባህሪ ተጨምሯል!');
    loadFeatures();
}

async function loadFeatures() {
    const res = await fetch('/api/custom_pages');
    const pages = await res.json();
    const el = document.getElementById('featuresList');
    const features = pages.filter(p => p.title.includes('🧩') || p.content.includes('ባህሪ'));
    if (!features.length) { el.innerHTML = '<p class="empty-msg">ምንም ተጨማሪ ባህሪ የለም</p>'; return; }
    el.innerHTML = features.map(f => `
        <div class="list-item">
            <span>${f.icon || '🧩'} ${f.title}</span>
            <span class="del" onclick="deletePage(${f.id})">🗑️</span>
        </div>
    `).join('');
}

function showStatus(msg) {
    const el = document.getElementById('statusMsg');
    el.textContent = msg;
    setTimeout(() => { el.textContent = ''; }, 3000);
}

loadStats(); loadPageOrder(); loadPages(); loadFeatures();

(async () => {
    const res = await fetch('/api/admin/verify', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({initData})
    });
    const data = await res.json();
    if (!data.ok) {
        document.querySelector('.dash-container').innerHTML = '<h1>🚫 ተደራሽነት የለዎትም</h1>';
    }
})();
</script>
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

@app.route('/api/config/banks')
def api_config_banks():
    banks = get_config('banks', [])
    if not banks:
        banks = [
            {"bank": "የንግድ ባንክ", "number": "1000453578058", "owner": "Marshalom Tesfay"},
            {"bank": "ቴሌብር 1", "number": "0931556590", "owner": "Marshalom Tesfay"},
            {"bank": "ቴሌብር 2", "number": "0967386958", "owner": "Lwam Alem"}
        ]
    return jsonify(banks)

@app.route('/api/jobs/apply', methods=['POST'])
def api_jobs_apply():
    body = request.get_json(silent=True) or {}
    user = verify_telegram_webapp_data(body.get('initData', ''))
    job_id = body.get('job_id')
    job_title = body.get('job_title', 'ያልታወቀ ስራ')
    phone = body.get('phone', '')
    name = user.get('first_name', '') if user else body.get('name', 'ስም የለም')
    username = user.get('username', '') if user else ''
    user_id = user.get('id') if user else None
    app_id = add_job_application(job_id, job_title, user_id, name, username, phone)
    caption = f"💼 አዲስ የስራ ማመልከቻ! (ID: {app_id})\nስራ: {job_title}\nስም: {name} (@{username or 'የለም'})\nስልክ: {phone}"
    requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': HR_CHANNEL_ID, 'text': caption})
    requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': OWNER_CHAT_ID, 'text': caption})
    return jsonify({"ok": True})

@app.route('/api/ask_price', methods=['POST'])
def api_ask_price():
    body = request.get_json(silent=True) or {}
    user = verify_telegram_webapp_data(body.get('initData', ''))
    product_name = body.get('product_name', 'ያልታወቀ ምርት')
    if not user: return jsonify({"ok": False, "error": "verification failed"}), 403
    user_id = user.get('id')
    name = (user.get('first_name', '') + ' ' + user.get('last_name', '')).strip()
    username = user.get('username', '')
    upsert_customer(user_id, name, username)
    log_price_inquiry(user_id, name, username, product_name)
    caption = f"💰 የዋጋ ጥያቄ!\nምርት: {product_name}\nስም: {name} (@{username or 'የለም'})\nመታወቂያ: {user_id}"
    requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': PRICE_CHANNEL_ID, 'text': caption})
    requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': OWNER_CHAT_ID, 'text': caption})
    return jsonify({"ok": True})

@app.route('/api/ai_chat', methods=['POST'])
def api_ai_chat():
    body = request.get_json(silent=True) or {}
    user = verify_telegram_webapp_data(body.get('initData', ''))
    user_message = body.get('message', '').strip()
    if not user_message: return jsonify({"ok": False, "error": "empty"}), 400
    name = (user.get('first_name', '') if user else '') or 'ደንበኛ'
    username = user.get('username', '') if user else ''
    user_id = user.get('id') if user else None
    if user_id: upsert_customer(user_id, name, username)
    ai_reply = ask_deepseek(user_message)
    if ai_reply:
        requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': AI_CHANNEL_ID, 'text': f"🤖 AI ውይይት\nደንበኛ: {name} (@{username or 'የለም'})\nጥያቄ: {user_message}\nምላሽ: {ai_reply}"})
        return jsonify({"ok": True, "reply": ai_reply})
    else:
        busy_msg = """🌟 ማርሻሎም ረዳት\nአሁን ብዙ ጥያቄዎች በመምጣት ላይ ናቸው። ትንሽ ይጠብቁ።"""
        return jsonify({"ok": True, "reply": busy_msg})

@app.route('/api/testimonials/add', methods=['POST'])
def api_testimonials_add():
    body = request.get_json(silent=True) or {}
    user = verify_telegram_webapp_data(body.get('initData', ''))
    name = user.get('first_name', '') if user else body.get('name', 'ስም የለም')
    username = user.get('username', '') if user else ''
    message = body.get('message', '').strip()
    if not message: return jsonify({"ok": False}), 400
    add_testimonial(name, username, message)
    return jsonify({"ok": True})

@app.route('/api/message/send', methods=['POST'])
def api_message_send():
    body = request.get_json(silent=True) or {}
    user = verify_telegram_webapp_data(body.get('initData', ''))
    sender_name = user.get('first_name', '') if user else body.get('name', 'ስም የለም')
    sender_username = user.get('username', '') if user else ''
    sender_user_id = user.get('id') if user else None
    message = body.get('message', '').strip()
    if not message: return jsonify({"ok": False}), 400
    send_internal_message(sender_name, sender_username, sender_user_id, 'admin', None, message)
    requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': OWNER_CHAT_ID, 'text': f"📩 አዲስ መልእክት!\nከ: {sender_name} (@{sender_username or 'የለም'})\n{message}"})
    return jsonify({"ok": True})

# ===== Admin Routes =====
def require_admin():
    init_data = request.headers.get('X-Init-Data', '')
    user = verify_telegram_webapp_data(init_data)
    if not user: return False
    return is_admin_chat(user.get('id'))

@app.route('/api/admin/verify', methods=['POST'])
def api_admin_verify():
    body = request.get_json(silent=True) or {}
    user = verify_telegram_webapp_data(body.get('initData', ''))
    if user and is_admin_chat(user.get('id')):
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 403

@app.route('/api/admin/stats')
def api_admin_stats():
    if not require_admin(): return jsonify({"error": "forbidden"}), 403
    return jsonify(get_stats())

@app.route('/api/admin/page_order', methods=['GET', 'POST'])
def api_admin_page_order():
    if not require_admin(): return jsonify({"error": "forbidden"}), 403
    if request.method == 'GET':
        return jsonify(get_page_order())
    else:
        body = request.get_json(silent=True) or {}
        order_list = body.get('order', [])
        update_page_order(order_list)
        set_page_order(order_list)
        return jsonify({"ok": True})

@app.route('/api/admin/custom_pages', methods=['POST'])
def api_admin_add_custom_page():
    if not require_admin(): return jsonify({"error": "forbidden"}), 403
    body = request.get_json(silent=True) or {}
    new_id = add_custom_page(body.get('title'), body.get('icon', '📄'), body.get('content', ''))
    return jsonify({"ok": True, "id": new_id})

@app.route('/api/admin/custom_pages/<int:page_id>', methods=['DELETE'])
def api_admin_delete_custom_page(page_id):
    if not require_admin(): return jsonify({"error": "forbidden"}), 403
    delete_custom_page(page_id)
    return jsonify({"ok": True})

@app.route('/api/admin/theme', methods=['POST'])
def api_admin_theme():
    if not require_admin(): return jsonify({"error": "forbidden"}), 403
    body = request.get_json(silent=True) or {}
    set_theme(body)
    return jsonify({"ok": True})

@app.route('/api/admin/settings', methods=['POST'])
def api_admin_settings():
    if not require_admin(): return jsonify({"error": "forbidden"}), 403
    body = request.get_json(silent=True) or {}
    set_settings(body)
    return jsonify({"ok": True})

@app.route('/api/admin/config/banks', methods=['POST'])
def api_admin_config_banks():
    if not require_admin(): return jsonify({"error": "forbidden"}), 403
    body = request.get_json(silent=True) or {}
    set_config('banks', body.get('value', []))
    return jsonify({"ok": True})

@app.route('/api/admin/applications', methods=['POST'])
def api_admin_add_application():
    if not require_admin(): return jsonify({"error": "forbidden"}), 403
    body = request.get_json(silent=True) or {}
    new_id = add_application(body.get('name'), body.get('photo_url'), body.get('file_url'))
    return jsonify({"ok": True, "id": new_id})

@app.route('/api/admin/applications/<int:app_id>', methods=['DELETE'])
def api_admin_delete_application(app_id):
    if not require_admin(): return jsonify({"error": "forbidden"}), 403
    delete_application(app_id)
    return jsonify({"ok": True})

@app.route('/api/employee/login', methods=['POST'])
def api_employee_login():
    body = request.get_json(silent=True) or {}
    emp = get_employee_by_credentials(body.get('username', '').strip(), body.get('password', '').strip())
    if not emp: return jsonify({"ok": False, "error": "invalid"}), 401
    return jsonify({"ok": True, "profile": emp})

@app.route('/api/team/employees', methods=['POST'])
def api_team_employees():
    body = request.get_json(silent=True) or {}
    emp = get_employee_by_credentials(body.get('tl_username', '').strip(), body.get('tl_password', '').strip())
    if not emp or emp.get('role') != 'team_leader': return jsonify({"error": "forbidden"}), 403
    return jsonify(list_employees())

@app.route('/api/team/update', methods=['POST'])
def api_team_update():
    body = request.get_json(silent=True) or {}
    emp = get_employee_by_credentials(body.get('tl_username', '').strip(), body.get('tl_password', '').strip())
    if not emp or emp.get('role') != 'team_leader': return jsonify({"error": "forbidden"}), 403
    username = body.get('username'); field = body.get('field'); value = body.get('value')
    if field not in ('bonus', 'warnings', 'tasks'): return jsonify({"error": "invalid"}), 400
    update_employee_field(username, field, value, append=True)
    return jsonify({"ok": True})

@app.route('/api/team/reset_password', methods=['POST'])
def api_team_reset_password():
    body = request.get_json(silent=True) or {}
    emp = get_employee_by_credentials(body.get('tl_username', '').strip(), body.get('tl_password', '').strip())
    if not emp or emp.get('role') != 'team_leader': return jsonify({"error": "forbidden"}), 403
    username = body.get('username')
    target = get_employee_by_username(username)
    if not target: return jsonify({"error": "not found"}), 404
    temp_pw = generate_temp_password()
    set_employee_password(username, temp_pw, must_change=True)
    return jsonify({"ok": True, "temp_password": temp_pw})

# ===== Webhook =====
@app.route('/', methods=['POST'])
def webhook():
    if not TELEGRAM_TOKEN: return "TELEGRAM_TOKEN not set", 500
    try:
        data = request.get_json(silent=True)
        if not data or 'message' not in data:
            return "OK"
        msg = data['message']
        chat_id = msg['chat']['id']
        user = msg.get('from', {})
        text = msg.get('text', '')
        name = user.get('first_name', '')
        if user.get('last_name'): name += ' ' + user['last_name']
        username = user.get('username', '')
        user_id = user.get('id', '')
        url = f"{TELEGRAM_URL}/sendMessage"
        upsert_customer(user_id, name, username)

        if text == '777':
            requests.post(url, json={'chat_id': chat_id, 'text': '🎵 እንኳን ደህና መጡ አለቃ! 777 ስርዓት ንቁ ነው! 🔥'})
            return "OK"

        if text.startswith('/admin'):
            parts = text.split(' ', 1)
            if len(parts) == 2:
                if (ADMIN_PASSWORD and parts[1].strip() == ADMIN_PASSWORD) or (ADMIN_PASSWORD_2 and parts[1].strip() == ADMIN_PASSWORD_2):
                    set_session(chat_id, 'admin')
                    requests.post(url, json={'chat_id': chat_id, 'text': '✅ የአድሚን መዳረሻ ተፈቅዷል!'})
                else:
                    requests.post(url, json={'chat_id': chat_id, 'text': '❌ የተሳሳተ የይለፍ ቃል።'})
            elif is_admin_chat(chat_id):
                send_with_webapp_button(chat_id, '⚙️ የአድሚን ዳሽቦርድ', '⚙️ ዳሽቦርድ ክፈት', '/webapp#page-admin')
            else:
                requests.post(url, json={'chat_id': chat_id, 'text': '🔒 /admin የይለፍ_ቃል'})
            return "OK"

        if text.startswith('/start'):
            welcome = """✨ እንኳን ደህና መጡ ወደ SHALOM TECHNOLOGY! ✨
🎥📷🔒 እኛ በኤሌክትሮኒክስ እና በደህንነት ካሜራዎች ላይ ጥራት ያለው አገልግሎት የምንሰጥ ታማኝ የቴክኖሎጂ አጋርዎ ነን።"""
            requests.post(url, json={'chat_id': chat_id, 'text': welcome})
            send_with_webapp_button(chat_id, '🛍️ ካታሎግ ለማየት ይህን ይጫኑ', '🛍️ ምርቶች ይመልከቱ', '/webapp')
            return "OK"

        ai_reply = ask_deepseek(text)
        if ai_reply:
            requests.post(url, json={'chat_id': chat_id, 'text': f"🤖 {ai_reply}"})
        else:
            requests.post(url, json={'chat_id': chat_id, 'text': '🌟 ማርሻሎም ረዳት\nትንሽ ይጠብቁ።'})
        return "OK"
    except Exception as e:
        print(f"Error: {e}")
        return "OK"

# ===== Start =====
schedule_daily_promos()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
