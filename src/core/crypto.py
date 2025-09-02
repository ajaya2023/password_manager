"""
加密模块 - 使用AES-256加密和Argon2密钥派生
"""
import os
import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type
import hashlib

class CryptoManager:
    """密码加密管理器"""
    
    def __init__(self):
        self.ph = PasswordHasher()
        self.backend = default_backend()
        
    def derive_key(self, master_password: str, salt: bytes) -> bytes:
        """
        使用Argon2id从主密码派生加密密钥
        
        Args:
            master_password: 主密码
            salt: 盐值
            
        Returns:
            32字节的密钥
        """
        return hash_secret_raw(
            secret=master_password.encode(),
            salt=salt,
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            type=Type.ID
        )
    
    def encrypt_data(self, data: str, master_password: str) -> dict:
        """
        加密数据
        
        Args:
            data: 要加密的数据
            master_password: 主密码
            
        Returns:
            包含加密数据、盐值和IV的字典
        """
        # 生成随机盐值和IV
        salt = os.urandom(16)
        iv = os.urandom(16)
        
        # 派生密钥
        key = self.derive_key(master_password, salt)
        
        # 创建加密器
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # 填充数据
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data.encode()) + padder.finalize()
        
        # 加密
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        
        return {
            'encrypted_data': base64.b64encode(encrypted).decode(),
            'salt': base64.b64encode(salt).decode(),
            'iv': base64.b64encode(iv).decode()
        }
    
    def decrypt_data(self, encrypted_dict: dict, master_password: str) -> str:
        """
        解密数据
        
        Args:
            encrypted_dict: 包含加密数据的字典
            master_password: 主密码
            
        Returns:
            解密后的数据
        """
        # 解码
        encrypted_data = base64.b64decode(encrypted_dict['encrypted_data'])
        salt = base64.b64decode(encrypted_dict['salt'])
        iv = base64.b64decode(encrypted_dict['iv'])
        
        # 派生密钥
        key = self.derive_key(master_password, salt)
        
        # 创建解密器
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        
        # 解密
        decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # 去除填充
        unpadder = padding.PKCS7(128).unpadder()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
        
        return decrypted.decode()
    
    def hash_master_password(self, password: str) -> str:
        """哈希主密码用于验证"""
        return self.ph.hash(password)
    
    def verify_master_password(self, password: str, hash: str) -> bool:
        """验证主密码"""
        try:
            self.ph.verify(hash, password)
            return True
        except:
            return False
