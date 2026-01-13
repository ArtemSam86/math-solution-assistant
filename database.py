import sqlite3
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect('math_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            command TEXT,
            parameters TEXT,
            result TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(user_id, username=None, first_name=None, last_name=None):
    """Добавление пользователя в БД"""
    conn = sqlite3.connect('math_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, last_activity)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (user_id, username, first_name, last_name))
    
    cursor.execute('''
        UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE user_id = ?
    ''', (user_id,))
    
    conn.commit()
    conn.close()

def log_command(user_id, command, parameters=''):
    """Логирование команды"""
    conn = sqlite3.connect('math_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO messages (user_id, command, parameters)
        VALUES (?, ?, ?)
    ''', (user_id, command, parameters))
    
    cursor.execute('''
        UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE user_id = ?
    ''', (user_id,))
    
    conn.commit()
    conn.close()

def log_message(user_id, message, result=''):
    """Логирование сообщения"""
    log_command(user_id, 'message', f"{message}|{result}")

def get_stats():
    """Получение статистики"""
    conn = sqlite3.connect('math_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM messages')
    total_messages = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM users 
        WHERE last_activity >= datetime('now', '-1 day')
    ''')
    active_today = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_users': total_users,
        'total_messages': total_messages,
        'active_today': active_today
    }