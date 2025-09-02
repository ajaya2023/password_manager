#!/usr/bin/env python3
"""
密码管理器主程序
"""
import sys
import os
import argparse
import logging
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import PasswordManagerGUI  # 指定具体文件
from src.browser.auto_fill import BrowserConnector
from src.core.password_manager import PasswordManager
os.makedirs(os.path.expanduser('~/.password_manager'), exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/.password_manager/app.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def setup_native_messaging():
    """设置Native Messaging"""
    import json
    import platform
    
    manifest = {
        "name": "com.passwordmanager.native",
        "description": "Password Manager Native Host",
        "path": os.path.abspath(sys.argv[0]),
        "type": "stdio",
        "allowed_origins": [
            "chrome-extension://YOUR_EXTENSION_ID/"
        ]
    }
    
    # 根据操作系统确定安装路径
    system = platform.system()
    
    if system == "Linux":
        # Chrome
        chrome_path = os.path.expanduser(
            "~/.config/google-chrome/NativeMessagingHosts/"
        )
        # Firefox
        firefox_path = os.path.expanduser(
            "~/.mozilla/native-messaging-hosts/"
        )
        paths = [chrome_path, firefox_path]
        
    elif system == "Darwin":  # macOS
        chrome_path = os.path.expanduser(
            "~/Library/Application Support/Google/Chrome/NativeMessagingHosts/"
        )
        firefox_path = os.path.expanduser(
            "~/Library/Application Support/Mozilla/NativeMessagingHosts/"
        )
        paths = [chrome_path, firefox_path]
        
    elif system == "Windows":
        # Windows需要写入注册表
        print("请手动配置Windows注册表以启用Native Messaging")
        return
    
    # 创建目录并写入清单文件
    for path in paths:
        os.makedirs(path, exist_ok=True)
        manifest_file = os.path.join(path, "com.passwordmanager.native.json")
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"已安装Native Messaging清单到: {manifest_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='密码管理器')
    parser.add_argument(
        '--mode', 
        choices=['gui', 'browser', 'cli', 'setup'],
        default='gui',
        help='运行模式'
    )
    parser.add_argument(
        '--install-extension',
        action='store_true',
        help='安装浏览器扩展支持'
    )
    
    args = parser.parse_args()
    
    if args.install_extension:
        setup_native_messaging()
        return
    
    if args.mode == 'gui':
        # GUI模式
        logger.info("启动GUI模式")
        app = QApplication(sys.argv)
        app.setApplicationName("密码管理器")
        
        # 设置应用图标
        # app.setWindowIcon(QIcon('assets/icon.png'))
        
        window = PasswordManagerGUI()
        window.show()
        
        sys.exit(app.exec())
        
    elif args.mode == 'browser':
        # 浏览器Native Messaging模式
        logger.info("启动浏览器连接模式")
        pm = PasswordManager()
        
        # 尝试自动解锁（可以通过环境变量或其他安全方式）
        # 这里需要实现一个安全的解锁机制
        
        connector = BrowserConnector(pm)
        connector.start()
        
        # 保持运行
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            connector.stop()
            
    elif args.mode == 'cli':
        # CLI模式
        run_cli()
        
    elif args.mode == 'setup':
        # 安装设置
        setup_native_messaging()

def run_cli():
    """命令行界面"""
    from src.core.password_manager import PasswordManager
    import getpass
    
    pm = PasswordManager()
    
    print("=== 密码管理器 CLI ===")
    
    # 检查是否需要设置主密码
    if not pm.storage.get_master_password_hash():
        print("首次使用，请设置主密码")
        while True:
            password = getpass.getpass("输入主密码 (至少8个字符): ")
            confirm = getpass.getpass("确认主密码: ")
            
            if password != confirm:
                print("密码不匹配，请重试")
                continue
                
            if len(password) < 8:
                print("密码太短，请重试")
                continue
                
            pm.setup_master_password(password)
            print("主密码设置成功！")
            break
    else:
        # 解锁
        attempts = 3
        while attempts > 0:
            password = getpass.getpass("输入主密码解锁: ")
            if pm.unlock(password):
                print("解锁成功！")
                break
            else:
                attempts -= 1
                print(f"密码错误，剩余尝试次数: {attempts}")
        
        if attempts == 0:
            print("解锁失败，退出")
            return
    
    # 主循环
    while True:
        print("\n" + "="*40)
        print("1. 添加密码")
        print("2. 搜索密码")
        print("3. 生成密码")
        print("4. 删除密码")
        print("5. 退出")
        print("="*40)
        
        choice = input("选择操作 (1-5): ").strip()
        
        if choice == '1':
            # 添加密码
            title = input("标题: ").strip()
            username = input("用户名: ").strip()
            password = getpass.getpass("密码 (留空自动生成): ").strip()
            
            if not password:
                password = pm.generate_password()
                print(f"生成的密码: {password}")
            
            url = input("URL (可选): ").strip()
            notes = input("备注 (可选): ").strip()
            
            entry_id = pm.add_password(
                title=title,
                password=password,
                username=username,
                url=url,
                notes=notes
            )
            
            print(f"密码已保存，ID: {entry_id}")
            
        elif choice == '2':
            # 搜索密码
            query = input("搜索关键词: ").strip()
            results = pm.search_passwords(query)
            
            if results:
                print(f"\n找到 {len(results)} 个结果:")
                for i, entry in enumerate(results, 1):
                    print(f"{i}. {entry['title']} - {entry['username']}")
                
                # 选择查看详情
                select = input("\n输入编号查看详情 (或按Enter跳过): ").strip()
                if select.isdigit():
                    index = int(select) - 1
                    if 0 <= index < len(results):
                        entry = pm.get_password(results[index]['id'])
                        print(f"\n标题: {entry['title']}")
                        print(f"用户名: {entry['username']}")
                        print(f"密码: {entry['password']}")
                        print(f"URL: {entry['url']}")
                        print(f"备注: {entry['notes']}")
            else:
                print("没有找到匹配的密码")
                
        elif choice == '3':
            # 生成密码
            length = input("密码长度 (默认16): ").strip()
            length = int(length) if length.isdigit() else 16
            
            password = pm.generate_password(length=length)
            print(f"生成的密码: {password}")
            
            if input("是否保存此密码? (y/n): ").lower() == 'y':
                title = input("标题: ").strip()
                username = input("用户名: ").strip()
                pm.add_password(title=title, password=password, username=username)
                print("密码已保存")
                
        elif choice == '4':
            # 删除密码
            query = input("搜索要删除的密码: ").strip()
            results = pm.search_passwords(query)
            
            if results:
                print(f"\n找到 {len(results)} 个结果:")
                for i, entry in enumerate(results, 1):
                    print(f"{i}. {entry['title']} - {entry['username']}")
                
                select = input("\n输入要删除的编号: ").strip()
                if select.isdigit():
                    index = int(select) - 1
                    if 0 <= index < len(results):
                        confirm = input(f"确认删除 '{results[index]['title']}'? (y/n): ")
                        if confirm.lower() == 'y':
                            pm.delete_password(results[index]['id'])
                            print("密码已删除")
            else:
                print("没有找到匹配的密码")
                
        elif choice == '5':
            print("再见！")
            break
        else:
            print("无效的选择")

if __name__ == '__main__':
    main()
