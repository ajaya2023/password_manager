"""
密码管理器核心模块
"""
import secrets
import string
from typing import List, Dict, Optional
from .crypto import CryptoManager
from .storage import SecureStorage

class PasswordManager:
    """密码管理器核心类"""
    
    def __init__(self, storage_path: str = None):
        self.crypto = CryptoManager()
        self.storage = SecureStorage(storage_path) if storage_path else SecureStorage()
        self.master_password = None
        self.is_unlocked = False
    
    def setup_master_password(self, master_password: str) -> bool:
        """设置主密码"""
        if len(master_password) < 8:
            raise ValueError("主密码至少需要8个字符")
        
        # 哈希并保存主密码
        password_hash = self.crypto.hash_master_password(master_password)
        if self.storage.save_master_password(password_hash):
            self.master_password = master_password
            self.is_unlocked = True
            return True
        return False
    
    def unlock(self, master_password: str) -> bool:
        """解锁密码管理器"""
        stored_hash = self.storage.get_master_password_hash()
        if not stored_hash:
            raise ValueError("未设置主密码，请先设置主密码")
        
        if self.crypto.verify_master_password(master_password, stored_hash):
            self.master_password = master_password
            self.is_unlocked = True
            return True
        return False
    
    def lock(self):
        """锁定密码管理器"""
        self.master_password = None
        self.is_unlocked = False
    
    def add_password(self, title: str, password: str, 
                    url: str = None, username: str = None, 
                    notes: str = None, category: str = "general") -> int:
        """添加密码条目"""
        if not self.is_unlocked:
            raise PermissionError("密码管理器已锁定")
        
        # 加密密码
        encrypted_data = self.crypto.encrypt_data(password, self.master_password)
        
        # 准备条目数据
        entry_data = {
            'title': title,
            'url': url,
            'username': username,
            'encrypted_password': encrypted_data['encrypted_data'],
            'salt': encrypted_data['salt'],
            'iv': encrypted_data['iv'],
            'notes': notes,
            'category': category
        }
        
        # 保存到存储
        return self.storage.save_password_entry(entry_data)
    
    def get_password(self, entry_id: int) -> Optional[Dict]:
        """获取密码"""
        if not self.is_unlocked:
            raise PermissionError("密码管理器已锁定")
        
        entry = self.storage.get_password_entry(entry_id)
        if not entry:
            return None
        
        # 解密密码
        encrypted_dict = {
            'encrypted_data': entry['encrypted_password'],
            'salt': entry['salt'],
            'iv': entry['iv']
        }
        
        decrypted_password = self.crypto.decrypt_data(
            encrypted_dict, 
            self.master_password
        )
        
        # 返回完整信息
        return {
            'id': entry['id'],
            'title': entry['title'],
            'url': entry['url'],
            'username': entry['username'],
            'password': decrypted_password,
            'notes': entry['notes'],
            'category': entry['category'],
            'created_at': entry['created_at'],
            'last_modified': entry['last_modified']
        }
    
    def search_passwords(self, query: str = "", category: str = None) -> List[Dict]:
        """搜索密码（不返回实际密码）"""
        if not self.is_unlocked:
            raise PermissionError("密码管理器已锁定")
        
        return self.storage.search_entries(query, category)
    
    def generate_password(self, length: int = 16, 
                         use_uppercase: bool = True,
                         use_lowercase: bool = True,
                         use_digits: bool = True,
                         use_symbols: bool = True) -> str:
        """生成安全密码"""
        characters = ""
        
        if use_uppercase:
            characters += string.ascii_uppercase
        if use_lowercase:
            characters += string.ascii_lowercase
        if use_digits:
            characters += string.digits
        if use_symbols:
            characters += string.punctuation
        
        if not characters:
            raise ValueError("至少需要选择一种字符类型")
        
        # 使用secrets生成加密安全的随机密码
        password = ''.join(secrets.choice(characters) for _ in range(length))
        
        return password
    
    def delete_password(self, entry_id: int) -> bool:
        """删除密码条目"""
        if not self.is_unlocked:
            raise PermissionError("密码管理器已锁定")
        
        return self.storage.delete_entry(entry_id)
