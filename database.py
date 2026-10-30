import os
import sqlite3
import hashlib
import secrets
import smtplib
import json
from email.message import EmailMessage
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

# ==================================================
# SEND PASSWORD RESET EMAIL
# ==================================================

def send_password_reset_email(recipient_email, reset_code):

    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        raise ValueError(
            "Email configuration is missing."
        )

    message = EmailMessage()

    message["Subject"] = "SongPersona AI - Password Reset Code"
    message["From"] = EMAIL_ADDRESS
    message["To"] = recipient_email

    message.set_content(
        f"""Hello,

We received a request to reset your SongPersona AI password.

Your password reset code is:

{reset_code}

This code is valid for 4 minutes.

If you did not request a password reset, you can safely ignore this email.

Regards,
SongPersona AI
"""
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as server:

        server.starttls()

        server.login(
            EMAIL_ADDRESS,
            EMAIL_APP_PASSWORD
        )

        server.send_message(message)

DATABASE_NAME = "songpersona.db"


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_connection():
    return sqlite3.connect(DATABASE_NAME)


# ==================================================
# CREATE TABLES
# ==================================================

def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # ----------------------------------------------
    # Users
    # ----------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # ----------------------------------------------
    # Saved Songs
    # ----------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            emotion TEXT,
            emotion_score REAL,
            similarity REAL,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ----------------------------------------------
    # Password Reset Codes
    # ----------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            code_hash TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ----------------------------------------------
    # Music Profiles
    # ----------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS music_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            personality TEXT NOT NULL,
            emotion_profile TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

# ==================================================
# PASSWORD HASHING
# ==================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# ==================================================
# CREATE USER
# ==================================================

def create_user(name, email, password): 

    conn = get_connection()
    cursor = conn.cursor()

    try:

        hashed_password = hash_password(
            password
        )

        cursor.execute("""
            INSERT INTO users
            (name, email, password)
            VALUES (?, ?, ?)
        """, (
            name,
            email,
            hashed_password
        ))

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


# ==================================================
# LOGIN
# ==================================================

def login_user(email, password):

    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(
        password
    )

    cursor.execute("""
        SELECT id, name, email
        FROM users
        WHERE email = ?
        AND password = ?
    """, (
        email,
        hashed_password
    ))

    user = cursor.fetchone()

    conn.close()

    return user


# ==================================================
# SAVE SONG
# ==================================================

def save_song(
    user_id,
    title,
    artist,
    emotion=None,
    emotion_score=None,
    similarity=None
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO saved_songs
        (
            user_id,
            title,
            artist,
            emotion,
            emotion_score,
            similarity
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        title,
        artist,
        emotion,
        emotion_score,
        similarity
    ))

    conn.commit()
    conn.close()


# ==================================================
# GET SAVED SONGS
# ==================================================

def get_saved_songs(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            artist,
            emotion,
            emotion_score,
            similarity,
            saved_at
        FROM saved_songs
        WHERE user_id = ?
        ORDER BY saved_at DESC
    """, (user_id,))

    songs = cursor.fetchall()

    conn.close()

    return songs


# ==================================================
# REMOVE SAVED SONG
# ==================================================

def remove_saved_song(song_id, user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM saved_songs
        WHERE id = ?
        AND user_id = ?
    """, (
        song_id,
        user_id
    ))

    conn.commit()
    conn.close()


# ==================================================
# FIND USER BY EMAIL
# ==================================================

def get_user_by_email(email):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email
        FROM users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    conn.close()

    return user


# ==================================================
# CREATE PASSWORD RESET CODE
# ==================================================

def create_password_reset_code(
    user_id,
    expiry_minutes=4
):

    # Generate 6-digit code

    code = f"{secrets.randbelow(1000000):06d}"

    code_hash = hashlib.sha256(
        code.encode()
    ).hexdigest()

    expires_at = (
        datetime.now()
        + timedelta(minutes=expiry_minutes)
    ).isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    # Invalidate previous unused codes

    cursor.execute("""
        UPDATE password_reset_codes
        SET used = 1
        WHERE user_id = ?
        AND used = 0
    """, (user_id,))

    # Store new code

    cursor.execute("""
        INSERT INTO password_reset_codes
        (
            user_id,
            code_hash,
            expires_at
        )
        VALUES (?, ?, ?)
    """, (
        user_id,
        code_hash,
        expires_at
    ))

    conn.commit()
    conn.close()

    return code


# ==================================================
# VERIFY PASSWORD RESET CODE
# ==================================================

def verify_password_reset_code(
    user_id,
    code
):

    code_hash = hashlib.sha256(
        code.strip().encode()
    ).hexdigest()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, expires_at
        FROM password_reset_codes
        WHERE user_id = ?
        AND code_hash = ?
        AND used = 0
        ORDER BY created_at DESC
        LIMIT 1
    """, (
        user_id,
        code_hash
    ))

    reset_record = cursor.fetchone()

    if not reset_record:

        conn.close()
        return False

    reset_id = reset_record[0]
    expires_at = datetime.fromisoformat(
        reset_record[1]
    )

    if datetime.now() > expires_at:

        cursor.execute("""
            UPDATE password_reset_codes
            SET used = 1
            WHERE id = ?
        """, (reset_id,))

        conn.commit()
        conn.close()

        return False

    conn.close()

    return True


# ==================================================
# RESET PASSWORD
# ==================================================

def reset_password(
    user_id,
    new_password
):

    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(
        new_password
    )

    # Update user's password
    cursor.execute("""
        UPDATE users
        SET password = ?
        WHERE id = ?
    """, (
        hashed_password,
        user_id
    ))

    changed = cursor.rowcount > 0

    # Mark reset codes as used
    if changed:

        cursor.execute("""
            UPDATE password_reset_codes
            SET used = 1
            WHERE user_id = ?
            AND used = 0
        """, (user_id,))

    conn.commit()
    conn.close()

    return changed

# ==================================================
# SAVE MUSIC PROFILE
# ==================================================

def save_music_profile(
    user_id,
    personality,
    emotion_profile
):

    conn = get_connection()
    cursor = conn.cursor()

    personality_json = json.dumps(
        personality
    )

    emotion_profile_json = json.dumps(
        emotion_profile
    )

    cursor.execute("""
        INSERT INTO music_profiles
        (
            user_id,
            personality,
            emotion_profile
        )
        VALUES (?, ?, ?)

        ON CONFLICT(user_id)
        DO UPDATE SET
            personality = excluded.personality,
            emotion_profile = excluded.emotion_profile,
            updated_at = CURRENT_TIMESTAMP
    """, (
        user_id,
        personality_json,
        emotion_profile_json
    ))

    conn.commit()
    conn.close()

# ==================================================
# GET MUSIC PROFILE
# ==================================================

def get_music_profile(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            personality,
            emotion_profile
        FROM music_profiles
        WHERE user_id = ?
        LIMIT 1
    """, (user_id,))

    profile = cursor.fetchone()

    conn.close()

    if not profile:
        return None

    personality = json.loads(
        profile[0]
    )

    emotion_profile = json.loads(
        profile[1]
    )

    return (
        personality,
        emotion_profile
    )