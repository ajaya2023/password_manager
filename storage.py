"""
本地存储模块 - 使用SQLite加密数据库
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import filelock

class SecureStorage:
    def __init__(self, db_path: str = "~/.password_manager/vault.db"):
        # 1. 先定义 db_path
        self.db_path = os.path.expanduser(db_path)
        
        # 2. 创建目录
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 3. 然后才能使用 db_path 创建 lock
        self.lock = filelock.FileLock(f"{self.db_path}.lock")
        
        # 4. 最后初始化数据库
        self._init_database()

    
    def _init_database(self):
        """初始化数据库"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建主密码表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS master_password (
                    id INTEGER PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建密码条目表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT,
                    username TEXT,
                    encrypted_password TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    iv TEXT NOT NULL,
                    notes TEXT,
                    category TEXT DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_url ON passwords(url)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_category ON passwords(category)
            ''')
            
            conn.commit()
            conn.close()
    
    def save_master_password(self, password_hash: str) -> bool:
        """保存主密码哈希"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 检查是否已存在主密码
                cursor.execute("SELECT COUNT(*) FROM master_password")
                if cursor.fetchone()[0] > 0:
                    cursor.execute("""
                        UPDATE master_password 
                        SET password_hash = ?, last_modified = CURRENT_TIMESTAMP 
                        WHERE id = 1
                    """, (password_hash,))
                else:
                    cursor.execute("""
                        INSERT INTO master_password (password_hash) 
                        VALUES (?)
                    """, (password_hash,))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                print(f"Error saving master password: {e}")
                return False
    
    def get_master_password_hash(self) -> Optional[str]:
        """获取主密码哈希"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM master_password WHERE id = 1")
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
    
    def save_password_entry(self, entry_data: dict) -> int:
        """保存密码条目"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO passwords 
                (title, url, username, encrypted_password, salt, iv, notes, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry_data['title'],
                entry_data.get('url', ''),
                entry_data.get('username', ''),
                entry_data['encrypted_password'],
                entry_data['salt'],
                entry_data['iv'],
                entry_data.get('notes', ''),
                entry_data.get('category', 'general')
            ))
            
            entry_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return entry_id
    
    def get_password_entry(self, entry_id: int) -> Optional[dict]:
        """获取密码条目"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE passwords 
                SET last_accessed = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (entry_id,))
            
            cursor.execute("SELECT * FROM passwords WHERE id = ?", (entry_id,))
            row = cursor.fetchone()
            
            conn.commit()
            conn.close()
            
            return dict(row) if row else None
    
    def search_entries(self, query: str = "", category: str = None) -> List[dict]:
        """搜索密码条目"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if category:
                cursor.execute("""
                    SELECT id, title, url, username, category, created_at, last_modified
                    FROM passwords 
                    WHERE category = ? AND (
                        title LIKE ? OR 
                        url LIKE ? OR 
                        username LIKE ?
                    )
                    ORDER BY last_accessed DESC, last_modified DESC
                """, (category, f"%{query}%", f"%{query}%", f"%{query}%"))
            else:
                cursor.execute("""
                    SELECT id, title, url, username, category, created_at, last_modified
                    FROM passwords 
                    WHERE title LIKE ? OR url LIKE ? OR username LIKE ?
                    ORDER BY last_accessed DESC, last_modified DESC
                """, (f"%{query}%", f"%{query}%", f"%{query}%"))
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return results
    
    def delete_entry(self, entry_id: int) -> bool:
        """删除密码条目"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM passwords WHERE id = ?", (entry_id,))
                conn.commit()
                conn.close()
                return True
            except:
                return False
