# Python 密码管理器

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Framework](https://img.shields.io/badge/UI-PyQt6-brightgreen.svg)](https://www.riverbankcomputing.com/software/pyqt/)

一个安全、跨平台的密码管理器，使用 Python 和 PyQt6 构建。它提供了图形用户界面（GUI）以及与浏览器集成的能力(未完成)，旨在提供一个安全、便捷的密码管理解决方案。

## ✨ 主要特性

- **图形用户界面 (GUI)**: 一个使用 PyQt6 构建的、直观易用的桌面应用程序。
- **安全第一**:
  - 使用主密码加密所有存储的凭据。
  - 使用 AES-256 加密算法。
  - 密码数据储存在本地。
- **强密码生成器**: 内置工具，可生成可定制的、高强度的随机密码。
- **快速搜索**: 轻松搜索和检索您保存的任何凭据。


## 🚀 使用说明

点击即用

## 📂 项目结构

```
.
├── main.py                # 主程序入口，处理命令行参数和模式切换
├── src/
│   ├── gui/
│   │   └── main_window.py   # PyQt6 GUI 主窗口实现
│   ├── browser/
│   │   └── auto_fill.py     # 处理浏览器 Native Messaging 的逻辑
│   └── core/
│       └── password_manager.py # 核心业务逻辑，包括加密、存储和密码管理
├── assets/                  # 存放图标、图片等静态资源
└── README.md              # 本文档
```

## 🤝 贡献代码

欢迎您为这个项目做出贡献！请遵循以下步骤：

1.  **Fork** 本仓库。
2.  创建您的新功能分支 (`git checkout -b feature/AmazingFeature`)。
3.  提交您的更改 (`git commit -m 'Add some AmazingFeature'`)。
4.  将您的分支推送到远程仓库 (`git push origin feature/AmazingFeature`)。
5.  创建一个 **Pull Request**。

## 📄 许可证

本项目采用 [MIT 许可证](https://opensource.org/licenses/MIT)。
