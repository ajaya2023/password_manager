"""
浏览器自动填充模块 - 使用Native Messaging与浏览器扩展通信
"""
import json
import struct
import sys
import threading
from typing import Dict, Optional
import urllib.parse
from src.core.password_manager import PasswordManager

class BrowserConnector:
    """浏览器连接器"""
    
    def __init__(self, password_manager: PasswordManager):
        self.pm = password_manager
        self.running = False
    
    def start(self):
        """启动监听浏览器消息"""
        self.running = True
        thread = threading.Thread(target=self._listen_for_messages)
        thread.daemon = True
        thread.start()
    
    def stop(self):
        """停止监听"""
        self.running = False
    
    def _listen_for_messages(self):
        """监听来自浏览器扩展的消息"""
        while self.running:
            try:
                # 读取消息长度（4字节）
                raw_length = sys.stdin.buffer.read(4)
                if not raw_length:
                    break
                
                message_length = struct.unpack('=I', raw_length)[0]
                
                # 读取消息内容
                message = sys.stdin.buffer.read(message_length).decode('utf-8')
                request = json.loads(message)
                
                # 处理请求
                response = self._handle_request(request)
                
                # 发送响应
                self._send_response(response)
                
            except Exception as e:
                self._send_response({
                    'success': False,
                    'error': str(e)
                })
    
    def _handle_request(self, request: Dict) -> Dict:
        """处理浏览器请求"""
        action = request.get('action')
        
        if action == 'get_credentials':
            return self._get_credentials_for_url(request.get('url'))
        
        elif action == 'save_credentials':
            return self._save_credentials(request)
        
        elif action == 'check_status':
            return {
                'success': True,
                'unlocked': self.pm.is_unlocked
            }
        
        else:
            return {
                'success': False,
                'error': f'Unknown action: {action}'
            }
    
    def _get_credentials_for_url(self, url: str) -> Dict:
        """获取URL对应的凭据"""
        if not self.pm.is_unlocked:
            return {
                'success': False,
                'error': 'Password manager is locked'
            }
        
        try:
            # 解析URL获取域名
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc
            
            # 搜索匹配的密码
            entries = self.pm.search_passwords(domain)
            
            if entries:
                # 获取第一个匹配的完整密码信息
                password_data = self.pm.get_password(entries[0]['id'])
                
                return {
                    'success': True,
                    'credentials': {
                        'username': password_data['username'],
                        'password': password_data['password']
                    }
                }
            
            return {
                'success': True,
                'credentials': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _save_credentials(self, request: Dict) -> Dict:
        """保存新凭据"""
        if not self.pm.is_unlocked:
            return {
                'success': False,
                'error': 'Password manager is locked'
            }
        
        try:
            url = request.get('url')
            username = request.get('username')
            password = request.get('password')
            
            # 解析URL获取域名作为标题
            parsed = urllib.parse.urlparse(url)
            title = parsed.netloc
            
            # 保存密码
            entry_id = self.pm.add_password(
                title=title,
                password=password,
                url=url,
                username=username,
                category='web'
            )
            
            return {
                'success': True,
                'entry_id': entry_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _send_response(self, response: Dict):
        """发送响应到浏览器扩展"""
        message = json.dumps(response)
        encoded_message = message.encode('utf-8')
        
        # 发送消息长度（4字节）
        sys.stdout.buffer.write(struct.pack('=I', len(encoded_message)))
        # 发送消息内容
        sys.stdout.buffer.write(encoded_message)
        sys.stdout.buffer.flush()

# Native Messaging Host 配置文件（需要安装到系统）
NATIVE_HOST_MANIFEST = {
    "name": "com.passwordmanager.native",
    "description": "Password Manager Native Host",
    "path": "/usr/local/bin/password-manager-host",
    "type": "stdio",
    "allowed_origins": [
        "chrome-extension://YOUR_EXTENSION_ID/",
        "moz-extension://YOUR_EXTENSION_ID/"
    ]
}
