import sqlite3
import json
import pandas as pd
from datetime import datetime
import os

DB_NAME = "receipts.db"

def init_db():
    """Initialize the SQLite database and create the table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            merchant TEXT,
            date TEXT,
            total REAL,
            currency TEXT,
            category TEXT,
            narrative_summary TEXT,
            items TEXT,
            image_path TEXT,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_receipt(data: dict):
    """Save a processed receipt to the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    
    items_json = json.dumps(data.get('items', []))
    
    c.execute('''
        INSERT INTO receipts (merchant, date, total, currency, category, narrative_summary, items, image_path, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('merchant'),
        data.get('date'),
        data.get('total'),
        data.get('currency'),
        data.get('category'),
        data.get('narrative_summary'),
        items_json,
        data.get('image_path'),
        datetime.now()
    ))
    conn.commit()
    conn.close()

def get_all_receipts():
    """Retrieve all receipts from the database as a DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT * FROM receipts ORDER BY created_at DESC", conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def delete_receipt(receipt_id):
    """Delete a receipt from the database by ID and remove its image file."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
  
    c.execute("SELECT image_path FROM receipts WHERE id = ?", (receipt_id,))
    row = c.fetchone()
    
    if row and row[0]:
        from modules.file_manager import delete_image
        delete_image(row[0])
    
    c.execute("DELETE FROM receipts WHERE id = ?", (receipt_id,))
    conn.commit()
    conn.close()
