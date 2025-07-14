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
cd DofusMultiCompteCLI

# Python 3.12 start

py ./main.py
# Build (assuming you are on windows and got all installed requirements)
./build.bat
(will export a dist file and build you the project into a .exe app)

# Code Citations

## License: GPL_3_0
https://github.com/d1zzy/gogbot/tree/60f078ae278d20b71ca8779491baae6b29d67724/lib/keygen.py

```
, wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR)
```


## License: unknown
https://github.com/LolnationCH/YAPAP/tree/cc08c1f3fce2579925c754f91778dd46760fc248/Windows/Structs.py

```
KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo",
```


## License: MIT
https://github.com/MarkMoretto/python-examples-main/tree/f08f2fe05f30ffc0f2fe369bc1f4da3564702fdf/windows/move_cursor.py

```
.Structure):
    _fields_ = [("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD
```


