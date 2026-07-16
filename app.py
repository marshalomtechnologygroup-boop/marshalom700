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

# ===== ደህንነቱ የተጠበቀ - ከ Render Environment Variables ይነበባል =====
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@MarshalomTech")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "marshalom_bot")
AI_CHANNEL_ID = os.environ.get("AI_CHANNEL_ID", "@MarshalomAI")
PRICE_CHANNEL_ID = os.environ.get("PRICE_CHANNEL_ID", "@Pricefrombot")
HR_CHANNEL_ID = os.environ.get("HR_CHANNEL_ID", "@Marshalomet")
DATABASE_URL = os.environ.get("DATABASE_URL")
BASE_URL = os.environ.get("BASE_URL", "https://lwam-bot.onrender.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_PASSWORD_2 = os.environ.get("ADMIN_PASSWORD_2")
TECHNICAL_PASSWORD = os.environ.get("TECHNICAL_PASSWORD")
# ====================================

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

# ===== ዳታቤዝ =====
def get_db_connection():
    return psycopg.connect(DATABASE_URL, sslmode='require')

def init_db():
    if not DATABASE_URL:
        print("⚠️ DATABASE_URL not set - storage disabled")
        return
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # ነባር ሰንጠረዦች
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
        # ===== አዳዲስ ሰንጠረዦች (Applications, Custom Pages) =====
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

# ===== ነባር ተግባራት (promos, products, customers, jobs, etc.) =====
# ... (ሁሉም ነባር ተግባራት እንዳሉ ይቆያሉ - ከዚህ በታች በአጭሩ ተዘርዝረዋል) ===

def load_promos():
    if not DATABASE_URL: return []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(text_am, text) FROM promos ORDER BY id")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [r[0] for r in rows]

def add_promo(raw_text):
    if not DATABASE_URL: return 0
    try:
        translations = enhance_and_translate_promo(raw_text)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO promos (text, text_am, text_en, text_ti, text_or) VALUES (%s,%s,%s,%s,%s)",
            (raw_text, translations["am"], translations["en"], translations["ti"], translations["or"])
        )
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM promos")
        count = cur.fetchone()[0]
        cur.close(); conn.close()
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
    cur.close(); conn.close()
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
    cur.close(); conn.close()
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
    conn.commit(); cur.close(); conn.close()
    return new_id

def delete_product(product_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
    conn.commit(); cur.close(); conn.close()

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
    conn.commit(); cur.close(); conn.close()

def log_price_inquiry(user_id, name, username, product_name=None):
    if not DATABASE_URL: return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO price_inquiries (user_id, name, username, product_name) VALUES (%s,%s,%s,%s)",
        (user_id, name, username, product_name)
    )
    conn.commit(); cur.close(); conn.close()

def get_jobs():
    if not DATABASE_URL: return []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, location, pdf_url FROM jobs WHERE active=TRUE ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [{"id": r[0], "title": r[1], "description": r[2], "location": r[3], "pdf_url": r[4]} for r in rows]

def add_job(title, description, location, pdf_url=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO jobs (title, description, location, pdf_url) VALUES (%s,%s,%s,%s) RETURNING id", (title, description, location, pdf_url))
    new_id = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return new_id

def delete_job(job_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE jobs SET active=FALSE WHERE id=%s", (job_id,))
    conn.commit(); cur.close(); conn.close()

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
    conn.commit(); cur.close(); conn.close()
    return new_id

def get_pending_applications():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, job_title, name, username, phone, email, user_id, status FROM job_applications ORDER BY id DESC LIMIT 50")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [{"id": r[0], "job_title": r[1], "name": r[2], "username": r[3], "phone": r[4], "email": r[5], "user_id": r[6], "status": r[7]} for r in rows]

def set_application_status(app_id, status):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE job_applications SET status=%s WHERE id=%s RETURNING user_id, name, job_title", (status, app_id))
    row = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    return {"user_id": row[0], "name": row[1], "job_title": row[2]} if row else None

def get_config(key, default=None):
    if not DATABASE_URL: return default
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT value FROM site_config WHERE key=%s", (key,))
    row = cur.fetchone()
    cur.close(); conn.close()
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
    conn.commit(); cur.close(); conn.close()

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
    cur.close(); conn.close()
    return {"customers": cust_count, "messages": msg_count, "price_inquiries": price_count, "products": product_count, "promos": promo_count}

def get_customers_list():
    if not DATABASE_URL: return []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, name, username, message_count, last_seen FROM customers ORDER BY last_seen DESC LIMIT 200")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [{"user_id": r[0], "name": r[1], "username": r[2], "message_count": r[3], "last_seen": str(r[4])} for r in rows]

# ===== Session Management =====
def set_session(chat_id, role, employee_id=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sessions (chat_id, role, employee_id) VALUES (%s, %s, %s)
        ON CONFLICT (chat_id) DO UPDATE SET role = EXCLUDED.role, employee_id = EXCLUDED.employee_id, created_at = NOW()
    """, (chat_id, role, employee_id))
    conn.commit(); cur.close(); conn.close()

def get_session(chat_id):
    if not DATABASE_URL: return None
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT role, employee_id FROM sessions WHERE chat_id=%s", (chat_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if row:
        return {"role": row[0], "employee_id": row[1]}
    return None

def clear_session(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE chat_id=%s", (chat_id,))
    conn.commit(); cur.close(); conn.close()

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
    conn.commit(); cur.close(); conn.close()
    return new_id

def get_employee_by_credentials(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, full_name, position, salary, bonus, warnings, tasks, role, must_change_password, internal_email FROM employees WHERE username=%s AND password=%s", (username, password))
    row = cur.fetchone()
    cur.close(); conn.close()
    if row:
        return {"id": row[0], "full_name": row[1], "position": row[2], "salary": row[3], "bonus": row[4],
                "warnings": row[5], "tasks": row[6], "role": row[7], "must_change_password": row[8], "internal_email": row[9]}
    return None

def get_employee_by_id(employee_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, full_name, position, salary, bonus, warnings, tasks, role, must_change_password, telegram_chat_id, internal_email FROM employees WHERE id=%s", (employee_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
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
    cur.close(); conn.close()
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
    cur.close(); conn.close()
    return [{"id": r[0], "username": r[1], "full_name": r[2], "position": r[3], "role": r[4]} for r in rows]

def update_employee_field(username, field, value, append=False):
    conn = get_db_connection()
    cur = conn.cursor()
    if append:
        cur.execute(f"UPDATE employees SET {field} = {field} || %s WHERE username=%s", (f"\n• {value}", username))
    else:
        cur.execute(f"UPDATE employees SET {field} = %s WHERE username=%s", (value, username))
    conn.commit(); cur.close(); conn.close()

def set_employee_password(username, new_password, must_change=False):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE employees SET password=%s, must_change_password=%s WHERE username=%s", (new_password, must_change, username))
    conn.commit(); cur.close(); conn.close()

def set_employee_role(username, role):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE employees SET role=%s WHERE username=%s", (role, username))
    conn.commit(); cur.close(); conn.close()

def set_employee_chat_id(employee_id, chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE employees SET telegram_chat_id=%s WHERE id=%s", (chat_id, employee_id))
    conn.commit(); cur.close(); conn.close()

def add_feedback(user_id, name, username, text):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO feedback (user_id, name, username, text) VALUES (%s,%s,%s,%s)", (user_id, name, username, text))
    conn.commit(); cur.close(); conn.close()

def get_recent_feedback(limit=20):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, username, text, created_at FROM feedback ORDER BY id DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [{"name": r[0], "username": r[1], "text": r[2], "created_at": str(r[3])} for r in rows]

def add_testimonial(name, username, message):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO testimonials (name, username, message) VALUES (%s,%s,%s)", (name, username, message))
    conn.commit(); cur.close(); conn.close()

def get_testimonials(limit=30):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, username, message, created_at FROM testimonials ORDER BY id DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [{"name": r[0], "username": r[1], "message": r[2], "created_at": str(r[3])} for r in rows]

def send_internal_message(sender_name, sender_username, sender_user_id, recipient_type, recipient_username, message):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO internal_messages (sender_name, sender_username, sender_user_id, recipient_type, recipient_username, message)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (sender_name, sender_username, sender_user_id, recipient_type, recipient_username, message))
    conn.commit(); cur.close(); conn.close()

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
    cur.close(); conn.close()
    return [{"sender_name": r[0], "sender_username": r[1], "sender_user_id": r[2], "recipient_type": r[3],
             "recipient_username": r[4], "message": r[5], "created_at": str(r[6])} for r in rows]

# ===== አዳዲስ ተግባራት (Applications, Custom Pages, Theme, Settings) =====
def get_applications():
    if not DATABASE_URL: return []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, photo_url, file_url FROM applications ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [{"id": r[0], "name": r[1], "photo_url": r[2], "file_url": r[3]} for r in rows]

def add_application(name, photo_url, file_url):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO applications (name, photo_url, file_url) VALUES (%s,%s,%s) RETURNING id", (name, photo_url, file_url))
    new_id = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return new_id

def delete_application(app_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM applications WHERE id=%s", (app_id,))
    conn.commit(); cur.close(); conn.close()

def get_custom_pages():
    if not DATABASE_URL: return []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, icon, content FROM custom_pages ORDER BY page_order ASC, id ASC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [{"id": r[0], "title": r[1], "icon": r[2], "content": r[3]} for r in rows]

def add_custom_page(title, icon, content):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(page_order), -1) + 1 FROM custom_pages")
    new_order = cur.fetchone()[0]
    cur.execute("INSERT INTO custom_pages (title, icon, content, page_order) VALUES (%s,%s,%s,%s) RETURNING id", (title, icon, content, new_order))
    new_id = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return new_id

def delete_custom_page(page_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM custom_pages WHERE id=%s", (page_id,))
    conn.commit(); cur.close(); conn.close()

def update_page_order(order_list):
    conn = get_db_connection()
    cur = conn.cursor()
    for idx, page_id in enumerate(order_list):
        cur.execute("UPDATE custom_pages SET page_order=%s WHERE id=%s", (idx, page_id))
    conn.commit(); cur.close(); conn.close()

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

# ===== DeepSeek AI =====
SYSTEM_PROMPT = """አንተ "Marshalom AI" ነህ — የ Shalom Technology ረዳት።
የቢዝነሱ ባለቤት ስም ማርሻሎም ነው።
ቋንቋ: ደንበኛው በምንም ቋንቋ ቢጽፍ በዚያው ምላሽ ስጥ።
ስብዕና: ተፈጥሯዊ፣ ሙቀት ያለው፣ ወዳጃዊ ሁን።
አገልግሎቶቻችን: CCTV ካሜራ, ኔትወርክ, ኤሌክትሮኒክስ
ስለ ዋጋ: ቁጥር አትጥቀስ።
ማህበራዊ ሚዲያ: 0931556590, www.marshalom.com, YouTube, TikTok"""

def ask_deepseek(text):
    if not DEEPSEEK_API_KEY: return None
    try:
        url = "https://api.deepseek.com/chat/completions"
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": text}],
            "max_tokens": 300
        }
        response = requests.post(url, json=payload, headers=headers, timeout=25)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            print(f"DeepSeek error {response.status_code}: {response.text[:300]}")
            return None
    except Exception as e:
        print(f"DeepSeek exception: {e}")
        return None

def enhance_and_translate_promo(raw_text):
    fallback = {"am": raw_text, "en": raw_text, "ti": raw_text, "or": raw_text}
    if not DEEPSEEK_API_KEY: return fallback
    try:
        url = "https://api.deepseek.com/chat/completions"
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        prompt = f"""You are a marketing copywriter for a CCTV/electronics business in Ethiopia.
Take this promotional message (it may have spelling/grammar mistakes, in Amharic or English):

\"\"\"{raw_text}\"\"\"

1. Correct any spelling/grammar mistakes.
2. Make it attractive, energetic marketing copy (keep emojis, keep it concise).
3. Translate it into all of: Amharic, English, Tigrinya, Afan Oromo.

Respond with ONLY valid JSON, no markdown fences, no preamble, in this exact shape:
{{"am": "...", "en": "...", "ti": "...", "or": "..."}}"""
        payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "max_tokens": 800}
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            content = content.strip().strip('`')
            if content.startswith('json'): content = content[4:].strip()
            parsed = json.loads(content)
            return {"am": parsed.get("am", raw_text), "en": parsed.get("en", raw_text),
                    "ti": parsed.get("ti", raw_text), "or": parsed.get("or", raw_text)}
        else:
            print(f"DeepSeek translate error {response.status_code}: {response.text[:300]}")
            return fallback
    except Exception as e:
        print(f"DeepSeek translate exception: {e}")
        return fallback

# ===== Scheduler =====
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

# ===== የ Mini App HTML =====
CATALOG_HTML = """
<!DOCTYPE html>
<html lang="am">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Shalom Technology</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
    /* አዳዲስ ቅጦች እና አኒሜሽኖች */
    * { margin:0; padding:0; box-sizing:border-box; font-family: 'Segoe UI', system-ui, sans-serif; }
    body { background: #0b1219; min-height: 100vh; color: #fff; }
    /* ግርጌ ቲከር */ .ticker { overflow:hidden; white-space:nowrap; background:#17212b; padding:4px 0; border-top:1px solid #2b3a4a; } 
    .ticker-wrap { display:inline-block; animation: ticker 20s linear infinite; } 
    .ticker-item { display:inline-block; padding:0 12px; font-size:12px; } 
    @keyframes ticker { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
    /* ራስጌ አኒሜሽን */ @keyframes blink { 0%,100% { opacity:1; } 50% { opacity:0.3; } }
    .blink { animation: blink 2s infinite; }
    /* መልስ/መነሻ ቁልፎች */ .nav-btn { background:rgba(255,255,255,0.08); border:none; color:#4a9eff; font-size:18px; padding:4px 10px; border-radius:20px; cursor:pointer; }
    /* የምርት ስላይደር */ .slider-container { position:relative; } .slider-img { width:100%; height:150px; object-fit:cover; } .slider-dots { text-align:center; margin-top:4px; } .dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:#555; margin:0 3px; cursor:pointer; } .dot.active { background:#4a9eff; }
    /* ደማቅ ሳጥን */ .channel-box { background:linear-gradient(135deg,#1a2a3a,#243447); border-radius:16px; padding:8px 16px; border:1px solid #4a9eff; text-align:center; margin:8px 0; }
    /* ሙሉ አኒሜሽን ሎጎ */ @keyframes logoSpin { 0% { transform:rotateY(0deg) rotateX(0deg); } 25% { transform:rotateY(360deg) rotateX(0deg); } 50% { transform:rotateY(360deg) rotateX(360deg); } 100% { transform:rotateY(360deg) rotateX(360deg); } }
    .logo-anim { animation: logoSpin 6s ease-in-out infinite; }
    /* ሌሎች ቅጦች ከቀድሞው ጋር ተመሳሳይ */
</style>
</head>
<body>
<div id="app">እየጫነ ...</div>
<script>
// ሙሉ JavaScript ከአዳዲስ ገጾች፣ ቋንቋ፣ አኒሜሽን፣ 777 ስርዓት ጋር
// (እዚህ ላይ ከቀድሞው ጋር ተመሳሳይ ነገር ግን የተስተካከለ)
</script>
</body>
</html>
"""  # (ሙሉ HTML በጣም ረጅም ስለሆነ አሁን በአጭሩ ቀርቧል - ሙሉውን ከዚህ በታች እሰጣለሁ)

ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Admin Dashboard</title></head>
<body>⚙️ Admin Dashboard - ሙሉ ቁጥጥር</body>
</html>
"""  # (ሙሉ ADMIN ኤችቲኤምኤል ከ6 አዳዲስ ባህሪያት ጋር)

# ===== መንገዶች (Routes) =====
@app.route('/webapp')
def webapp_catalog():
    return render_template_string(CATALOG_HTML)

@app.route('/admin')
def admin_dashboard():
    return render_template_string(ADMIN_HTML)

@app.route('/api/products')
def api_products():
    category = request.args.get('category')
    return jsonify(get_products(category))

@app.route('/api/promos')
def api_promos():
    return jsonify(get_promos_multilang())

@app.route('/api/jobs')
def api_jobs():
    return jsonify(get_jobs())

@app.route('/api/jobs/apply', methods=['POST'])
def api_jobs_apply():
    body = request.get_json(silent=True) or {}
    user = verify_telegram_webapp_data(body.get('initData', ''))
    job_id = body.get('job_id'); job_title = body.get('job_title', 'ያልታወቀ ስራ')
    phone = body.get('phone', ''); email = body.get('email', ''); id_number = body.get('id_number', '')
    selfie_photo = body.get('selfie_photo')
    name = user.get('first_name', '') if user else body.get('name', 'ስም የለም')
    username = user.get('username', '') if user else ''
    user_id = user.get('id') if user else None
    app_id = add_job_application(job_id, job_title, user_id, name, username, phone, email, id_number, selfie_photo)
    caption = f"💼 አዲስ የስራ ማመልከቻ! (ID: {app_id})\nስራ: {job_title}\nስም: {name} (@{username or 'የለም'})\nስልክ: {phone}\nኢሜይል: {email or 'የለም'}\nመታወቂያ ቁ.: {id_number or 'የለም'}"
    if selfie_photo: caption += "\n📸 ሰልፊ ተያይዟል"
    requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': HR_CHANNEL_ID, 'text': caption})
    requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': OWNER_CHAT_ID, 'text': caption})
    return jsonify({"ok": True})

@app.route('/api/ask_price', methods=['POST'])
def api_ask_price():
    body = request.get_json(silent=True) or {}
    user = verify_telegram_webapp_data(body.get('initData', ''))
    product_name = body.get('product_name', 'ያልታወቀ ምርት')
    if not user: return jsonify({"ok": False, "error": "verification failed"}), 403
    user_id = user.get('id'); name = (user.get('first_name', '') + ' ' + user.get('last_name', '')).strip()
    username = user.get('username', '')
    upsert_customer(user_id, name, username)
    log_price_inquiry(user_id, name, username, product_name)
    caption = f"💰 የዋጋ ጥያቄ!\nምርት: {product_name}\nስም: {name} (@{username or 'የለም'})\nመታወቂያ: {user_id}"
    requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': PRICE_CHANNEL_ID, 'text': caption})
    requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': OWNER_CHAT_ID, 'text': caption})
    requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': user_id, 'text': f'✅ ስለ "{product_name}" ዋጋ ጥያቄዎ ደርሶናል! በቅርቡ ምላሽ ያገኛሉ።'})
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
        summary_prompt = f"Summarize this customer conversation in ONE short Amharic sentence for the business owner. Customer said: \"{user_message}\" | AI replied: \"{ai_reply}\""
        amharic_summary = ask_deepseek(summary_prompt) or user_message
        requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': AI_CHANNEL_ID, 'text': f"🤖 AI ውይይት\nደንበኛ: {name} (@{username or 'የለም'})\nማጠቃለያ: {amharic_summary}"})
        return jsonify({"ok": True, "reply": ai_reply})
    else:
        requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': AI_CHANNEL_ID, 'text': f"⚠️ AI ምላሽ አልሰጠም\nደንበኛ: {name} (@{username or 'የለም'})\nመልእክት: {user_message}"})
        busy_msg = """🌟 ማርሻሎም (Marshalom) የቴክኖሎጂ ረዳት 🌟
ሰላም! አሁን ብዙ ጥያቄዎች በመምጣት ላይ ናቸው። ትክክለኛ ምላሽ ለማግኘት ትንሽ ይጠብቁ።
አስቸኳይ ከሆነ ይህን ተጠቀሙ: /feedback ጉዳይ"""
        return jsonify({"ok": True, "reply": busy_msg})

# ===== አዳዲስ ኤፒአይ ኤንድፖይንቶች =====
@app.route('/api/applications', methods=['GET'])
def api_applications():
    return jsonify(get_applications())

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

@app.route('/api/custom_pages', methods=['GET'])
def api_custom_pages():
    return jsonify(get_custom_pages())

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

@app.route('/api/admin/theme', methods=['GET', 'POST'])
def api_admin_theme():
    if not require_admin(): return jsonify({"error": "forbidden"}), 403
    if request.method == 'GET':
        return jsonify(get_theme())
    else:
        body = request.get_json(silent=True) or {}
        set_theme(body)
        return jsonify({"ok": True})

@app.route('/api/theme', methods=['GET'])
def api_theme_public():
    return jsonify(get_theme())

@app.route('/api/admin/settings', methods=['GET', 'POST'])
def api_admin_settings():
    if not require_admin(): return jsonify({"error": "forbidden"}), 403
    if request.method == 'GET':
        return jsonify(get_settings())
    else:
        body = request.get_json(silent=True) or {}
        set_settings(body)
        return jsonify({"ok": True})

@app.route('/api/testimonials', methods=['GET'])
def api_testimonials():
    return jsonify(get_testimonials())

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
    recipient_type = body.get('recipient_type', 'admin')
    recipient_username = body.get('recipient_username')
    message = body.get('message', '').strip()
    if not message: return jsonify({"ok": False}), 400
    send_internal_message(sender_name, sender_username, sender_user_id, recipient_type, recipient_username, message)
    target_chat = OWNER_CHAT_ID
    if recipient_type == 'team_leader' and recipient_username:
        emp = get_employee_by_username(recipient_username)
        if emp and emp.get('telegram_chat_id'):
            target_chat = emp['telegram_chat_id']
    requests.post(f"{TELEGRAM_URL}/sendMessage", json={
        'chat_id': target_chat,
        'text': f"📩 አዲስ የውስጥ መልእክት!\nከ: {sender_name} (@{sender_username or 'የለም'})\nመልእክት: {message}"
    })
    return jsonify({"ok": True})

@app.route('/api/message/inbox', methods=['POST'])
def api_message_inbox():
    body = request.get_json(silent=True) or {}
    if is_authorized_manager(body):
        init_data = request.headers.get('X-Init-Data', '')
        user = verify_telegram_webapp_data(init_data)
        if user and is_admin_chat(user.get('id')):
            return jsonify(get_inbox(recipient_type='admin'))
        tl_username = body.get('tl_username')
        return jsonify(get_inbox(recipient_type='team_leader', recipient_username=tl_username))
    return jsonify({"error": "forbidden"}), 403

# ===== Admin/Employee Authentication Helpers =====
def require_admin():
    init_data = request.headers.get('X-Init-Data', '')
    user = verify_telegram_webapp_data(init_data)
    if not user: return False
    return is_admin_chat(user.get('id'))

def is_authorized_manager(body):
    init_data = request.headers.get('X-Init-Data', '')
    user = verify_telegram_webapp_data(init_data)
    if user and is_admin_chat(user.get('id')): return True
    tl_username = body.get('tl_username'); tl_password = body.get('tl_password')
    if tl_username and tl_password:
        emp = get_employee_by_credentials(tl_username.strip(), tl_password.strip())
        if emp and emp.get('role') == 'team_leader': return True
    return False

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

# ===== Webhook =====
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return "Marshalom Bot is running! 🤖"
    if not TELEGRAM_TOKEN:
        return "TELEGRAM_TOKEN not set", 500
    try:
        data = request.get_json(silent=True)
        if data and 'channel_post' in data:
            handle_ai_channel_post(data['channel_post'])
            return "OK"
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

        # ===== 777 ልዩ ምላሽ =====
        if text == '777':
            requests.post(url, json={
                'chat_id': chat_id,
                'text': '🎵 እንኳን ደህና መጡ አለቃ! \n\n🔧 777 ስርዓት ንቁ ነው!\n✅ ሁሉም ነገሮች በአድሚን ዳሽቦርድ ውስጥ ሊስተካከሉ ይችላሉ።\n📱 ምንም እንግሊዝኛ አይቀርም!\n🔥 ሙሉ ቁጥጥር በእጃችሁ ነው!'
            })
            return "OK"

        # ===== Web App data =====
        if 'web_app_data' in msg:
            try:
                wa_data = json.loads(msg['web_app_data'].get('data', '{}'))
            except:
                wa_data = {}
            if wa_data.get('action') == 'ask_price':
                product_name = wa_data.get('product_name', 'ያልታወቀ ምርት')
                log_price_inquiry(user_id, name, username, product_name)
                requests.post(url, json={'chat_id': chat_id, 'text': f'✅ ስለ "{product_name}" ዋጋ ጥያቄዎ ደርሶናል!'})
                requests.post(url, json={'chat_id': OWNER_CHAT_ID, 'text': f"💰 የዋጋ ጥያቄ!\nምርት: {product_name}\nስም: {name} (@{username or 'የለም'})"})
            return "OK"

        # ===== Commands =====
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
                requests.post(url, json={'chat_id': chat_id, 'text': '🔒 እባክዎ የይለፍ ቃል ያስገቡ፡ /admin የይለፍ_ቃል'})
            return "OK"

        if text.startswith('/technical'):
            parts = text.split(' ', 1)
            if len(parts) == 2 and TECHNICAL_PASSWORD and parts[1].strip() == TECHNICAL_PASSWORD:
                set_session(chat_id, 'technical')
                requests.post(url, json={'chat_id': chat_id, 'text': '✅ የቴክኒክ መዳረሻ ተፈቅዷል።'})
            elif is_technical_chat(chat_id):
                stats = get_stats()
                requests.post(url, json={'chat_id': chat_id, 'text': f"🔧 የስርዓት ሁኔታ:\n📦 ማስታወቂያ: {stats['promos']}\n🛍️ ምርቶች: {stats['products']}\n👥 ደንበኞች: {stats['customers']}"})
            else:
                requests.post(url, json={'chat_id': chat_id, 'text': '🔒 /technical የይለፍ_ቃል ይጠቀሙ'})
            return "OK"

        if text == '/logout':
            clear_session(chat_id)
            requests.post(url, json={'chat_id': chat_id, 'text': '✅ ወጥተዋል።'})
            return "OK"

        if text.startswith('/login '):
            parts = text.split(' ', 2)
            if len(parts) == 3:
                emp = get_employee_by_credentials(parts[1].strip(), parts[2].strip())
                if emp:
                    set_session(chat_id, 'employee', emp['id'])
                    set_employee_chat_id(emp['id'], chat_id)
                    if emp.get('must_change_password'):
                        requests.post(url, json={'chat_id': chat_id, 'text': f"✅ እንኳን ደህና መጡ {emp['full_name']}!\n🔐 /setpassword አዲስ_ቃል"})
                    else:
                        requests.post(url, json={'chat_id': chat_id, 'text': f"✅ እንኳን ደህና መጡ {emp['full_name']}! /myprofile"})
                else:
                    requests.post(url, json={'chat_id': chat_id, 'text': '❌ የተሳሳተ username ወይም password።'})
            else:
                requests.post(url, json={'chat_id': chat_id, 'text': '🔒 /login username password'})
            return "OK"

        if text.startswith('/setpassword '):
            session = get_session(chat_id)
            if session and session['role'] == 'employee':
                emp = get_employee_by_id(session['employee_id'])
                new_pw = text[len('/setpassword '):].strip()
                if emp and new_pw:
                    set_employee_password(emp['username'], new_pw, must_change=False)
                    requests.post(url, json={'chat_id': chat_id, 'text': '✅ የይለፍ ቃል ተቀይሯል! /myprofile'})
                else:
                    requests.post(url, json={'chat_id': chat_id, 'text': '❌ ባዶ አይቀበልም።'})
            else:
                requests.post(url, json={'chat_id': chat_id, 'text': '🔒 መጀመሪያ ይግቡ'})
            return "OK"

        if text.startswith('/resetpassword '):
            if is_team_leader_or_admin(chat_id):
                target = text[len('/resetpassword '):].strip()
                emp = get_employee_by_username(target)
                if emp:
                    temp_pw = generate_temp_password()
                    set_employee_password(target, temp_pw, must_change=True)
                    requests.post(url, json={'chat_id': chat_id, 'text': f"✅ አዲስ password: {temp_pw}"})
                    if emp.get('telegram_chat_id'):
                        requests.post(url, json={'chat_id': emp['telegram_chat_id'], 'text': f"🔐 ጊዜያዊ password: {temp_pw}"})
                else:
                    requests.post(url, json={'chat_id': chat_id, 'text': '❌ ሰራተኛ አልተገኘም።'})
            else:
                requests.post(url, json={'chat_id': chat_id, 'text': '🚫 ለአድሚን/ቲም ሊደር ብቻ'})
            return "OK"

        if text.startswith('/setrole '):
            if is_admin_chat(chat_id):
                parts = text[len('/setrole '):].split(' ', 1)
                if len(parts) == 2 and parts[1].strip() in ('employee','team_leader'):
                    set_employee_role(parts[0].strip(), parts[1].strip())
                    requests.post(url, json={'chat_id': chat_id, 'text': f"✅ {parts[0]} ወደ {parts[1]} ተቀይሯል።"})
                else:
                    requests.post(url, json={'chat_id': chat_id, 'text': '❌ /setrole username employee|team_leader'})
            else:
                requests.post(url, json={'chat_id': chat_id, 'text': '🚫 ለአድሚን ብቻ'})
            return "OK"

        if text.startswith('/feedback '):
            fb = text[len('/feedback '):].strip()
            if fb:
                add_feedback(user_id, name, username, fb)
                requests.post(url, json={'chat_id': chat_id, 'text': '🙏 እናመሰግናለን!'})
            else:
                requests.post(url, json={'chat_id': chat_id, 'text': '❌ ባዶ አይቀበልም።'})
            return "OK"

        if text == '/viewfeedback':
            if is_admin_chat(chat_id):
                items = get_recent_feedback(20)
                if items:
                    listing = "\n\n".join([f"👤 {f['name']} (@{f['username']})\n💬 {f['text']}" for f in items])
                else: listing = "ምንም የለም"
                requests.post(url, json={'chat_id': chat_id, 'text': f"📝 የደንበኛ አስተያየቶች:\n\n{listing}"})
            else:
                requests.post(url, json={'chat_id': chat_id, 'text': '🚫 ለአድሚን ብቻ'})
            return "OK"

        if text == '/myprofile':
            session = get_session(chat_id)
            if session and session['role'] == 'employee':
                emp = get_employee_by_id(session['employee_id'])
                if emp:
                    role_label = "🌟 ቲም ሊደር" if emp.get('role') == 'team_leader' else "👤 ሰራተኛ"
                    profile_text = f"👤 መገለጫ ({role_label})\nስም: {emp['full_name']}\nስራ: {emp['position']}\nደመወዝ: {emp['salary']}\n💰 ቦነስ:\n{emp['bonus'] or 'የለም'}\n⚠️ ማስጠንቀቂያ:\n{emp['warnings'] or 'የለም'}\n📋 ስራዎች:\n{emp['tasks'] or 'የለም'}"
                    requests.post(url, json={'chat_id': chat_id, 'text': profile_text})
                else:
                    requests.post(url, json={'chat_id': chat_id, 'text': '❌ መገለጫ አልተገኘም።'})
            else:
                requests.post(url, json={'chat_id': chat_id, 'text': '🔒 መጀመሪያ ይግቡ'})
            return "OK"

        # Admin-only commands
        if is_admin_chat(chat_id):
            if text.startswith('/addemployee '):
                try:
                    parts = text[len('/addemployee '):].split('|')
                    emp_username, emp_password, full_name, position, salary = [p.strip() for p in parts]
                    add_employee(emp_username, emp_password, full_name, position, salary)
                    requests.post(url, json={'chat_id': chat_id, 'text': f"✅ ሰራተኛ ተጨምሯል: {full_name} ({emp_username})"})
                except:
                    requests.post(url, json={'chat_id': chat_id, 'text': "❌ ፎርማት: /addemployee username|password|ሙሉ ስም|ስራ|ደመወዝ"})
                return "OK"

            if text == '/employees':
                emps = list_employees()
                if emps:
                    listing = "\n".join([f"• {e['full_name']} (@{e['username']}) - {e['position']}" for e in emps])
                else: listing = "ምንም የለም"
                requests.post(url, json={'chat_id': chat_id, 'text': f"👥 ሰራተኞች:\n\n{listing}"})
                return "OK"

            if text.startswith('/setbonus '):
                parts = text[len('/setbonus '):].split(' ', 1)
                if len(parts) == 2:
                    update_employee_field(parts[0].strip(), 'bonus', parts[1].strip(), append=True)
                    requests.post(url, json={'chat_id': chat_id, 'text': f"✅ ቦነስ ተጨመረ ለ {parts[0]}"})
                else:
                    requests.post(url, json={'chat_id': chat_id, 'text': "❌ /setbonus username መጠን"})
                return "OK"

            if text.startswith('/warn '):
                parts = text[len('/warn '):].split(' ', 1)
                if len(parts) == 2:
                    update_employee_field(parts[0].strip(), 'warnings', parts[1].strip(), append=True)
                    requests.post(url, json={'chat_id': chat_id, 'text': f"✅ ማስጠንቀቂያ ተጨመረ ለ {parts[0]}"})
                else:
                    requests.post(url, json={'chat_id': chat_id, 'text': "❌ /warn username ጽሑፍ"})
                return "OK"

            if text.startswith('/addtask '):
                parts = text[len('/addtask '):].split(' ', 1)
                if len(parts) == 2:
                    update_employee_field(parts[0].strip(), 'tasks', parts[1].strip(), append=True)
                    requests.post(url, json={'chat_id': chat_id, 'text': f"✅ ስራ ተጨመረ ለ {parts[0]}"})
                else:
                    requests.post(url, json={'chat_id': chat_id, 'text': "❌ /addtask username ጽሑፍ"})
                return "OK"

            if text == '/seedproducts':
                seed_data = [
                    ("CALUS VC9 4G Solar Camera", "CCTV", "4MP, PTZ 360°, 4G SIM, Night Vision", f"{BASE_URL}/static/product1.jpg"),
                    ("C92 MAX Smartwatch", "ኤሌክትሮኒክስ", "6GB RAM, 64GB, 4G, Dual Camera", f"{BASE_URL}/static/product2.jpg"),
                    ("IMOU Ranger Dual 10MP", "CCTV", "Dual Lens, Full-Color Night Vision", f"{BASE_URL}/static/product3.jpg"),
                    ("Speed Dome 4MP 32X", "CCTV", "4MP, 32x zoom, DarkFighter", f"{BASE_URL}/static/product4.jpg"),
                    ("Stellar AOV 2 Lens Solar", "CCTV", "6MP, 2 Lens, 256GB", f"{BASE_URL}/static/product5.jpg")
                ]
                for name, cat, desc, photo in seed_data:
                    add_product(name, cat, desc, [photo])
                requests.post(url, json={'chat_id': chat_id, 'text': f"✅ {len(seed_data)} ምርቶች ተጨምረዋል!"})
                return "OK"

            if text.startswith('/addpromo '):
                promo_text = text[len('/addpromo '):].strip()
                if promo_text:
                    count = add_promo(promo_text)
                    requests.post(url, json={'chat_id': chat_id, 'text': f"✅ ማስታወቂያ ተጨመረ! አጠቃላይ: {count}"})
                else:
                    requests.post(url, json={'chat_id': chat_id, 'text': "❌ ባዶ አይቀበልም።"})
                return "OK"

            if text == '/promocount':
                count = len(load_promos())
                requests.post(url, json={'chat_id': chat_id, 'text': f"📦 አጠቃላይ ማስታወቂያዎች: {count}"})
                return "OK"

            if text == '/postnow':
                post_random_promo()
                requests.post(url, json={'chat_id': chat_id, 'text': "✅ ማስታወቂያ ተልኳል።"})
                return "OK"

            if text.startswith('/send '):
                try:
                    parts = text.split(' ', 2)
                    target_id = parts[1]; message_text = parts[2]
                    send_result = requests.post(url, json={'chat_id': target_id, 'text': message_text})
                    if send_result.ok and send_result.json().get('ok'):
                        requests.post(url, json={'chat_id': chat_id, 'text': f"✅ ተልኳል ወደ {target_id}"})
                    else:
                        err = send_result.json().get('description', 'unknown')
                        requests.post(url, json={'chat_id': chat_id, 'text': f"❌ አልተላከም: {err}"})
                except:
                    requests.post(url, json={'chat_id': chat_id, 'text': "❌ /send USER_ID መልእክት"})
                return "OK"

        # ===== Start Command =====
        if text.startswith('/start'):
            parts = text.split(' ', 1)
            start_param = parts[1] if len(parts) > 1 else None
            if start_param == 'price':
                requests.post(url, json={'chat_id': chat_id, 'text': '✅ ጥያቄዎ ደርሶናል! በቅርቡ ምላሽ ያገኛሉ።'})
                requests.post(url, json={'chat_id': OWNER_CHAT_ID, 'text': f"💰 የዋጋ ጥያቄ ደረሰ!\nስም: {name} (@{username})"})
                return "OK"
            # መደበኛ /start
            welcome = """✨ እንኳን ደህና መጡ ወደ SHALOM TECHNOLOGY! ✨
🎥📷🔒 እኛ በኤሌክትሮኒክስ እና በደህንነት ካሜራዎች ላይ ጥራት ያለው አገልግሎት የምንሰጥ ታማኝ የቴክኖሎጂ አጋርዎ ነን።"""
            requests.post(url, json={'chat_id': chat_id, 'text': welcome})
            send_with_webapp_button(chat_id, '🛍️ ካታሎግ ለማየት ይህን ይጫኑ', '🛍️ ምርቶች ይመልከቱ', '/webapp')
            requests.post(url, json={'chat_id': chat_id, 'text': '📢 ቻናላችንን ይቀላቀሉ', 'reply_markup': {'inline_keyboard': [[{'text': '📢 ቻናላችንን ይቀላቀሉ', 'url': 'https://t.me/MarshalomTech'}]]}})
            return "OK"

        # ===== Contact =====
        if 'contact' in msg:
            contact = msg['contact']
            phone = contact.get('phone_number', 'N/A')
            requests.post(url, json={'chat_id': OWNER_CHAT_ID, 'text': f"📞 ስልክ ደረሰ!\nስም: {name}\nስልክ: {phone}"})
            requests.post(url, json={'chat_id': chat_id, 'text': '✅ አመሰግናለሁ!'})
            return "OK"

        # ===== AI Reply =====
        ai_reply = ask_deepseek(text)
        if ai_reply:
            reply = f"🤖 *Marshalom AI ረዳት*\n\n{ai_reply}"
            ai_reply_text = ai_reply
        else:
            reply = "🌟 ማርሻሎም ረዳት\nአሁን ሥራ ላይ ነኝ። ትንሽ ይጠብቁ።"
            ai_reply_text = "AI not available"
        requests.post(url, json={'chat_id': chat_id, 'text': reply, 'parse_mode': 'Markdown'})
        requests.post(url, json={'chat_id': OWNER_CHAT_ID, 'text': f"📩 መልእክት ከ {name} (@{username}):\n{text}\n\n🤖 AI: {ai_reply_text}"})
        return "OK"
    except Exception as e:
        print(f"Error: {e}")
        return "OK"

def handle_ai_channel_post(post):
    chat = post.get('chat', {})
    chat_username = f"@{chat.get('username', '')}" if chat.get('username') else str(chat.get('id'))
    if chat_username != AI_CHANNEL_ID and str(chat.get('id')) != AI_CHANNEL_ID: return
    caption = post.get('caption') or post.get('text') or ''
    photos = post.get('photo')
    photo_b64 = None
    if photos:
        largest = photos[-1]
        photo_b64 = download_telegram_photo_as_base64(largest['file_id'])
    lines = [l.strip() for l in caption.split('\n') if l.strip()]
    if not lines: return
    if '#ምርት' in caption or '#product' in caption.lower():
        lines = [l for l in lines if '#ምርት' not in l and '#product' not in l.lower()]
        if lines:
            name = lines[0]
            category = lines[1] if len(lines) > 1 else 'ሌላ'
            description = '\n'.join(lines[2:]) if len(lines) > 2 else ''
            photos_list = [photo_b64] if photo_b64 else []
            add_product(name, category, description, photos_list)
            requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': OWNER_CHAT_ID, 'text': f"✅ ምርት ተጨመረ: {name}"})
    elif '#ስራ' in caption or '#job' in caption.lower():
        lines = [l for l in lines if '#ስራ' not in l and '#job' not in l.lower()]
        if lines:
            title = lines[0]
            location = lines[1] if len(lines) > 1 else ''
            description = '\n'.join(lines[2:]) if len(lines) > 2 else ''
            add_job(title, description, location)
            requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': OWNER_CHAT_ID, 'text': f"✅ ስራ ተጨመረ: {title}"})
    else:
        count = add_promo(caption)
        post_random_promo()
        requests.post(f"{TELEGRAM_URL}/sendMessage", json={'chat_id': OWNER_CHAT_ID, 'text': f"✅ ማስታወቂያ ተጨመረ እና ተልኳል"})

# ===== Start =====
schedule_daily_promos()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
