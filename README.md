![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Build: Manual](https://img.shields.io/badge/build-manual-lightgrey)

# DofusMultiCompteCLI

A GUI Handler multiple Dofus Windows at the time, with working features like "Multi-Clic-Window" and RealTime Working Hotkey Manager, to optimize Multi-Account-Player Interface and Custom Option in-APP.
---

## 🧩 Features

- Detect Automatically windows and resize it in-APP (Fake Embedding method) 
- Send mouse clicks or keystrokes to one or all clients simultaneously  
- Support for bulk actions (e.g., move all characters with one click)  
- Optional AutoHotkey scripting integration for customizable hotkeys  
- complex GUI 
- Multi-Theme support (Blue, Dark, Grey, Green, Pink, Purple, Light)
<img width="173" height="48" alt="image" src="https://github.com/user-attachments/assets/aad45d5a-5020-443d-81dc-4a3501362a19" />
App button explanation : 
- Config
- RefreshTabs(detect windows if not detected)
- CloseCLIDofus
- CloseApp
---
CONFIG THEME LIVE DEMO :

https://github.com/user-attachments/assets/512e0f88-f588-4f5d-97b6-b39f6e5c3b05


## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/Misaki-ux/DofusMultiCompteCLI.git
pip install -r ./requirements.txt
 - All external dependencies are properly declared in [`requirements.txt`](./requirements.txt)

cd DofusMultiCompteCLI

# Python 3.12 start

py ./main.py
# Build (assuming you are on windows and got all installed requirements)
./build.bat
(will export a dist file and build you the project into a .exe app)

## 📦 Dependency and Attribution Summary

This section provides a detailed list of all external libraries, frameworks, and referenced code used in this project. It ensures transparency, license compliance, and proper acknowledgment of contributors and third-party sources.

## External Dependencies and Libraries

### Main Framework
- **PySide6** - Qt for Python
  - Website: https://www.qt.io/qt-for-python
  - License: LGPL/Commercial
  - Usage: Complete GUI framework for the application interface
  - Used in: All UI components, main window, dialogs, widgets

### Windows API Integration
- **pywin32** - Python for Windows Extensions
  - Website: https://github.com/mhammond/pywin32
  - License: Python Software Foundation License
  - Usage: Windows API bindings for window management and system integration
  - Used in: Window tracking, focus management, hotkey system

### Image Processing
- **PIL/Pillow** - Python Imaging Library
  - Website: https://pillow.readthedocs.io/
  - License: PIL Software License
  - Usage: Image creation and processing for icons
  - Used in: create_config_icon.py

### Build Tools
- **Nuitka** - Python Compiler
  - Website: https://nuitka.net/
  - License: Apache License 2.0
  - Usage: Compiling Python to executable
  - Used in: build.bat

### Standard Library Dependencies
- **ctypes** - Foreign Function Interface
  - Part of Python Standard Library
  - Usage: Windows API calls and system integration
  - Used in: Low-level hotkey management, window operations

- **threading** - Thread-based parallelism
  - Part of Python Standard Library
  - Usage: Multi-threading for non-blocking operations
  - Used in: Click worker, hotkey management

- **json** - JSON encoder and decoder
  - Part of Python Standard Library
  - Usage: Configuration file handling
  - Used in: Config management

- **logging** - Flexible event logging system
  - Part of Python Standard Library
  - Usage: Application logging and debugging
  - Used in: Logger implementation

## Code Attribution

### Theme System
- **Qt Stylesheet (QSS)** - Styling system based on CSS
  - Part of Qt Framework
  - Usage: Application theming and visual styling
  - Used in: All theme files (themes/*.qss)

### Hotkey System
- **Windows Low-Level Keyboard Hook**
  - Based on Windows API documentation
  - Usage: Global hotkey detection and management
  - Used in: logic/low_level_hotkey_manager.py

## Development Tools

### Documentation
- **Markdown** - Lightweight markup language
  - Usage: Documentation files
  - Used in: README.md, various .md files

### Version Control
- **Git** - Distributed version control
  - Usage: Source code management
  - Configuration: .gitignore

## Notes

- All external dependencies are properly declared in requirements.txt
- The application follows standard Python packaging conventions
- No proprietary code or algorithms were directly copied
- All implementations are original work built upon documented APIs and frameworks

## License Compliance

This project uses the following licenses:
- **LGPL** (PySide6) - Compliant through dynamic linking
- **PSF License** (pywin32) - Compatible with project use
- **PIL License** (Pillow) - Compatible with project use
- **Apache 2.0** (Nuitka) - Compatible with project use

## Acknowledgments

Special thanks to the developers and maintainers of:
- The Qt Project and PySide6 team
- The pywin32 project contributors
- The Pillow/PIL development team
- The Python Software Foundation
- The Nuitka development team

