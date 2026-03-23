"""
SQLite Database for KimiClaw Interface
Local data storage - no external DB needed
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

BASE_DIR = Path("c:/Users/Student/kimiclaw")
DB_PATH = BASE_DIR / "data" / "kimiclaw.db"


class Database:
    """SQLite database for KimiClaw"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                task_id TEXT UNIQUE,
                sector TEXT,
                occupation TEXT,
                title TEXT,
                description TEXT,
                prompt TEXT,
                estimated_hours REAL,
                max_payment REAL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                result_score REAL,
                result_payment REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_runs (
                id INTEGER PRIMARY KEY,
                run_id TEXT UNIQUE,
                mode TEXT,
                status TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                final_balance REAL,
                log_summary TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                run_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level TEXT,
                message TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS economy (
                id INTEGER PRIMARY KEY,
                date TEXT UNIQUE,
                balance REAL,
                transaction_type TEXT,
                amount REAL,
                description TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        self.init_default_tasks()
    
    def init_default_tasks(self):
        tasks = [
            ("coding-task-001", "Technology", "Software Developer", "CSV Statistics",
             "Calculate CSV stats", "Create Python function for CSV statistics", 2, 50.0),
            ("coding-task-002", "Technology", "Web Developer", "FastAPI Todo API",
             "Build Todo API", "Build REST API with FastAPI", 3, 75.0),
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        for task in tasks:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO tasks (task_id, sector, occupation, title, description, prompt, estimated_hours, max_payment)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', task)
            except:
                pass
        conn.commit()
        conn.close()
    
    def get_all_tasks(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks
    
    def get_pending_tasks(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE status = 'pending'")
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks
    
    def get_task_by_id(self, task_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def update_task_status(self, task_id, status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET status = ? WHERE task_id = ?', (status, task_id))
        conn.commit()
        conn.close()
    
    def add_task(self, task):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (task_id, sector, occupation, title, description, prompt, estimated_hours, max_payment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.get('task_id'),
            task.get('sector'),
            task.get('occupation'),
            task.get('title'),
            task.get('description'),
            task.get('prompt'),
            task.get('estimated_hours'),
            task.get('max_payment')
        ))
        conn.commit()
        conn.close()
    
    def record_transaction(self, date, balance, transaction_type, amount, description):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO economy (date, balance, transaction_type, amount, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, balance, transaction_type, amount, description))
        conn.commit()
        conn.close()
    
    def get_current_balance(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM economy ORDER BY date DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        return row['balance'] if row else 100.0
    
    def add_log(self, run_id, level, message):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO logs (run_id, level, message) VALUES (?, ?, ?)',
                      (run_id, level, message))
        conn.commit()
        conn.close()
    
    def get_logs(self, limit=100):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?', (limit,))
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs
