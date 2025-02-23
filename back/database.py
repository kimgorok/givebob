# database.py
import sqlite3
from datetime import datetime
import json

def init_db():
    conn = sqlite3.connect('menu.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS menu_data
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         created_at TIMESTAMP NOT NULL,
         menus TEXT NOT NULL)
    ''')
    conn.commit()
    conn.close()

def save_menu(menu_data):
    conn = sqlite3.connect('menu.db')
    c = conn.cursor()
    c.execute(
        'INSERT INTO menu_data (created_at, menus) VALUES (?, ?)',
        (datetime.now(), json.dumps(menu_data))
    )
    conn.commit()
    conn.close()

def get_latest_menu():
    conn = sqlite3.connect('menu.db')
    c = conn.cursor()
    c.execute(
        'SELECT created_at, menus FROM menu_data ORDER BY created_at DESC LIMIT 1'
    )
    result = c.fetchone()
    conn.close()
    
    if result:
        return {
            'created_at': datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S.%f'),
            'menus': json.loads(result[1])
        }
    return None