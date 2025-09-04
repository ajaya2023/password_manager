# Python 密码管理器
# A Password Manager Base on Python
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Framework](https://img.shields.io/badge/UI-PyQt6-brightgreen.svg)](https://www.riverbankcomputing.com/software/pyqt/)

一个安全、跨平台的密码管理器，使用 Python 和 PyQt6 构建。它提供了图形用户界面（GUI）以及与浏览器集成的能力(未完成)，旨在提供一个安全、便捷的密码管理解决方案。
A secure, cross-platform password manager built with Python and PyQt6. It provides a graphical user interface (GUI) and the ability to integrate with browsers (unfinished), aiming to provide a secure and convenient password management solution.


## ✨ 主要特性
## ✨ Key Features

- **图形用户界面 (GUI)**: 一个使用 PyQt6 构建的、直观易用的桌面应用程序。
- **安全第一**:
  - 使用主密码加密所有存储的凭据。
  - 使用 AES-256 加密算法。
  - 密码数据储存在本地。
- **强密码生成器**: 内置工具，可生成可定制的、高强度的随机密码。
- **快速搜索**: 轻松搜索和检索您保存的任何凭据。
- 
- **Graphical User Interface (GUI)**: An intuitive and easy-to-use desktop application built with PyQt6.
- **Safety First**:
- Encrypt all stored credentials with a master password.
- Uses AES-256 encryption algorithm.
- Password data is stored locally.
- **Strong Password Generator**: Built-in tool to generate customizable, strong, random passwords.
- **Quick Search**: Easily search and retrieve any of your saved credentials.

## 🚀 使用说明
## 🚀 Instructions
点击即用
Click to use

## 📂 项目结构
## 📂 Project Structure

```
.
├── main.py               
├── src/
│   ├── gui/
│   │   └── main_window.py 
│   ├── browser/
│   │   └── auto_fill.py     
│   └── core/
│       └── password_manager.py
├── assets/               
└── README.md            
```

## 🤝 贡献代码
## 🤝 Contributing Code

欢迎您为这个项目做出贡献！请遵循以下步骤：
You are welcome to contribute to this project! Please follow these steps:

1.  **Fork** 本仓库。
2.  创建您的新功能分支 (`git checkout -b feature/AmazingFeature`)。
3.  提交您的更改 (`git commit -m 'Add some AmazingFeature'`)。
4.  将您的分支推送到远程仓库 (`git push origin feature/AmazingFeature`)。
5.  创建一个 **Pull Request**。
   
1. **Fork** this repository.
2. Create your new feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push your branch to the remote repository (`git push origin feature/AmazingFeature`).
5. Create a Pull Request.
## 📄 许可证
## 📄 License

本项目采用 [MIT 许可证](https://opensource.org/licenses/MIT)。
This project uses the [MIT License](https://opensource.org/licenses/MIT).
