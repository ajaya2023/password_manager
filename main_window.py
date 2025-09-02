"""
GUI客户端主窗口
"""
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import pyperclip
from src.core.password_manager import PasswordManager

class PasswordManagerGUI(QMainWindow):
    """密码管理器GUI主窗口"""
    
    def __init__(self):
        super().__init__()
        self.pm = PasswordManager()
        self.init_ui()
        self.check_master_password()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("密码管理器")
        self.setGeometry(100, 100, 900, 600)
        
        # 设置图标和样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #ccc;
                color: black;
            }
            QListWidget {
                background-color: white;
                color: black;
                border: 1px solid #555;
            }
            QLabel {
                color: black;
            }
        """)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧面板 - 密码列表
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索密码...")
        self.search_input.textChanged.connect(self.search_passwords)
        left_layout.addWidget(self.search_input)
        
        # 密码列表
        self.password_list = QListWidget()
        self.password_list.itemClicked.connect(self.on_password_selected)
        left_layout.addWidget(self.password_list)
        
        # 添加按钮
        self.add_button = QPushButton("添加密码")
        self.add_button.clicked.connect(self.show_add_dialog)
        left_layout.addWidget(self.add_button)
        
        main_layout.addWidget(left_panel, 1)
        
        # 右侧面板 - 密码详情
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 详情表单
        form_layout = QFormLayout()
        
        self.title_label = QLabel()
        form_layout.addRow("标题:", self.title_label)
        
        self.url_label = QLabel()
        form_layout.addRow("网址:", self.url_label)
        
        self.username_label = QLabel()
        form_layout.addRow("用户名:", self.username_label)
        
        # 密码显示和复制
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setReadOnly(True)
        password_layout.addWidget(self.password_input)
        
        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setMaximumWidth(40)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.show_password_btn)
        
        self.copy_password_btn = QPushButton("复制")
        self.copy_password_btn.clicked.connect(self.copy_password)
        password_layout.addWidget(self.copy_password_btn)
        
        form_layout.addRow("密码:", password_layout)
        
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(100)
        self.notes_text.setReadOnly(True)
        form_layout.addRow("备注:", self.notes_text)
        
        right_layout.addLayout(form_layout)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        self.delete_button = QPushButton("删除")
        self.delete_button.setStyleSheet("background-color: #f44336;")
        self.delete_button.clicked.connect(self.delete_password)
        button_layout.addWidget(self.delete_button)
        
        right_layout.addLayout(button_layout)
        right_layout.addStretch()
        
        main_layout.addWidget(right_panel, 2)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        lock_action = QAction("锁定", self)
        lock_action.setShortcut("Ctrl+L")
        lock_action.triggered.connect(self.lock_manager)
        file_menu.addAction(lock_action)
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具")
        
        generate_action = QAction("生成密码", self)
        generate_action.setShortcut("Ctrl+G")
        generate_action.triggered.connect(self.show_generate_dialog)
        tools_menu.addAction(generate_action)
    
    def check_master_password(self):
        """检查并设置主密码"""
        if not self.pm.storage.get_master_password_hash():
            # 首次使用，设置主密码
            dialog = SetupMasterPasswordDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                master_password = dialog.get_password()
                self.pm.setup_master_password(master_password)
                self.status_bar.showMessage("主密码设置成功")
                self.load_passwords()
            else:
                sys.exit()
        else:
            # 解锁
            dialog = UnlockDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                master_password = dialog.get_password()
                if self.pm.unlock(master_password):
                    self.status_bar.showMessage("解锁成功")
                    self.load_passwords()
                else:
                    QMessageBox.critical(self, "错误", "密码错误")
                    sys.exit()
            else:
                sys.exit()
    
    def load_passwords(self):
        """加载密码列表"""
        self.password_list.clear()
        passwords = self.pm.search_passwords()
        for pwd in passwords:
            item = QListWidgetItem(f"{pwd['title']} - {pwd['username']}")
            item.setData(Qt.ItemDataRole.UserRole, pwd['id'])
            self.password_list.addItem(item)
    
    def search_passwords(self):
        """搜索密码"""
        query = self.search_input.text()
        self.password_list.clear()
        passwords = self.pm.search_passwords(query)
        for pwd in passwords:
            item = QListWidgetItem(f"{pwd['title']} - {pwd['username']}")
            item.setData(Qt.ItemDataRole.UserRole, pwd['id'])
            self.password_list.addItem(item)
    
    def on_password_selected(self, item):
        """选择密码条目"""
        entry_id = item.data(Qt.ItemDataRole.UserRole)
        entry = self.pm.get_password(entry_id)
        
        if entry:
            self.current_entry_id = entry_id
            self.title_label.setText(entry['title'])
            self.url_label.setText(entry['url'] or "")
            self.username_label.setText(entry['username'] or "")
            self.password_input.setText(entry['password'])
            self.notes_text.setText(entry['notes'] or "")
    
    def toggle_password_visibility(self):
        """切换密码可见性"""
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("🔒")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("👁")
    
    def copy_password(self):
        """复制密码到剪贴板"""
        password = self.password_input.text()
        if password:
            pyperclip.copy(password)
            self.status_bar.showMessage("密码已复制到剪贴板", 3000)
            # 30秒后清除剪贴板
            QTimer.singleShot(30000, lambda: pyperclip.copy(""))
    
    def show_add_dialog(self):
        """显示添加密码对话框"""
        dialog = AddPasswordDialog(self.pm, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_passwords()
            self.status_bar.showMessage("密码添加成功")
    
    def show_generate_dialog(self):
        """显示生成密码对话框"""
        dialog = GeneratePasswordDialog(self.pm, self)
        dialog.exec()
    
    def delete_password(self):
        """删除密码"""
        if hasattr(self, 'current_entry_id'):
            reply = QMessageBox.question(
                self, "确认删除", 
                "确定要删除这个密码吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.pm.delete_password(self.current_entry_id):
                    self.load_passwords()
                    self.clear_details()
                    self.status_bar.showMessage("密码已删除")
    
    def clear_details(self):
        """清空详情面板"""
        self.title_label.clear()
        self.url_label.clear()
        self.username_label.clear()
        self.password_input.clear()
        self.notes_text.clear()
    
    def lock_manager(self):
        """锁定密码管理器"""
        self.pm.lock()
        self.password_list.clear()
        self.clear_details()
        self.check_master_password()

# 对话框类
class SetupMasterPasswordDialog(QDialog):
    """设置主密码对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置主密码")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("请设置主密码（至少8个字符）："))
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("确认密码")
        layout.addWidget(self.confirm_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
# 继续 main_window.py 中的对话框类

    def validate_and_accept(self):
        """验证并接受"""
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if len(password) < 8:
            QMessageBox.warning(self, "错误", "密码至少需要8个字符")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "错误", "两次输入的密码不一致")
            return
        
        self.accept()
    
    def get_password(self):
        """获取密码"""
        return self.password_input.text()

class UnlockDialog(QDialog):
    """解锁对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("解锁密码管理器")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("请输入主密码："))
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # 按Enter键提交
        self.password_input.returnPressed.connect(self.accept)
    
    def get_password(self):
        """获取密码"""
        return self.password_input.text()

class AddPasswordDialog(QDialog):
    """添加密码对话框"""
    
    def __init__(self, password_manager, parent=None):
        super().__init__(parent)
        self.pm = password_manager
        self.setWindowTitle("添加新密码")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QFormLayout(self)
        
        # 标题
        self.title_input = QLineEdit()
        layout.addRow("标题*:", self.title_input)
        
        # 网址
        self.url_input = QLineEdit()
        layout.addRow("网址:", self.url_input)
        
        # 用户名
        self.username_input = QLineEdit()
        layout.addRow("用户名:", self.username_input)
        
        # 密码
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.password_input)
        
        self.generate_btn = QPushButton("生成")
        self.generate_btn.clicked.connect(self.generate_password)
        password_layout.addWidget(self.generate_btn)
        
        layout.addRow("密码*:", password_layout)
        
        # 分类
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "general", "work", "personal", "finance", "social", "email"
        ])
        layout.addRow("分类:", self.category_combo)
        
        # 备注
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        layout.addRow("备注:", self.notes_input)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_password)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def generate_password(self):
        """生成密码"""
        password = self.pm.generate_password(16)
        self.password_input.setText(password)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
    
    def save_password(self):
        """保存密码"""
        title = self.title_input.text().strip()
        password = self.password_input.text().strip()
        
        if not title or not password:
            QMessageBox.warning(self, "错误", "标题和密码为必填项")
            return
        
        try:
            self.pm.add_password(
                title=title,
                password=password,
                url=self.url_input.text().strip(),
                username=self.username_input.text().strip(),
                notes=self.notes_input.toPlainText().strip(),
                category=self.category_combo.currentText()
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

class GeneratePasswordDialog(QDialog):
    """生成密码对话框"""
    
    def __init__(self, password_manager, parent=None):
        super().__init__(parent)
        self.pm = password_manager
        self.setWindowTitle("密码生成器")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # 密码长度
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("密码长度:"))
        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setMinimum(8)
        self.length_slider.setMaximum(32)
        self.length_slider.setValue(16)
        self.length_slider.valueChanged.connect(self.update_length_label)
        length_layout.addWidget(self.length_slider)
        
        self.length_label = QLabel("16")
        length_layout.addWidget(self.length_label)
        layout.addLayout(length_layout)
        
        # 字符选项
        self.uppercase_check = QCheckBox("大写字母 (A-Z)")
        self.uppercase_check.setChecked(True)
        layout.addWidget(self.uppercase_check)
        
        self.lowercase_check = QCheckBox("小写字母 (a-z)")
        self.lowercase_check.setChecked(True)
        layout.addWidget(self.lowercase_check)
        
        self.digits_check = QCheckBox("数字 (0-9)")
        self.digits_check.setChecked(True)
        layout.addWidget(self.digits_check)
        
        self.symbols_check = QCheckBox("特殊符号 (!@#$%...)")
        self.symbols_check.setChecked(True)
        layout.addWidget(self.symbols_check)
        
        # 生成的密码
        self.password_output = QLineEdit()
        self.password_output.setReadOnly(True)
        self.password_output.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(self.password_output)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("生成")
        self.generate_btn.clicked.connect(self.generate_password)
        button_layout.addWidget(self.generate_btn)
        
        self.copy_btn = QPushButton("复制")
        self.copy_btn.clicked.connect(self.copy_password)
        button_layout.addWidget(self.copy_btn)
        
        layout.addLayout(button_layout)
        
        # 初始生成
        self.generate_password()
    
    def update_length_label(self, value):
        """更新长度标签"""
        self.length_label.setText(str(value))
    
    def generate_password(self):
        """生成密码"""
        try:
            password = self.pm.generate_password(
                length=self.length_slider.value(),
                use_uppercase=self.uppercase_check.isChecked(),
                use_lowercase=self.lowercase_check.isChecked(),
                use_digits=self.digits_check.isChecked(),
                use_symbols=self.symbols_check.isChecked()
            )
            self.password_output.setText(password)
        except ValueError as e:
            QMessageBox.warning(self, "错误", str(e))
    
    def copy_password(self):
        """复制密码"""
        password = self.password_output.text()
        if password:
            pyperclip.copy(password)
            QMessageBox.information(self, "成功", "密码已复制到剪贴板")
