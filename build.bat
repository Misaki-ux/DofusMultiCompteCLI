@echo off
setlocal EnableDelayedExpansion

REM Chemin vers python.exe à forcer
set "PYTHON_EXE=C:\Users\Yohann\AppData\Local\Programs\Python\Python312\python.exe"

REM Couleurs ANSI Windows 10+
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "RESET=[0m"

cd /d "%~dp0"

echo %YELLOW%#########################################%RESET%
echo # Build DofusMultiWindows executable from spec   #
echo #########################################%RESET%

REM Suppression des anciens dossiers/fichiers build
for %%F in ("build" "dist") do (
    if exist "%%F" (
        echo %YELLOW%Removing %%F ...%RESET%
        rmdir /s /q "%%F" 2>nul || del /f /q "%%F"
    )
)

echo %YELLOW%#########################################%RESET%
echo # Compiling with Nuitka                 #
echo #########################################%RESET%

REM Lancement de nuitka via python forcé
"%PYTHON_EXE%" -m nuitka --standalone --onefile --windows-console-mode=disable --output-dir=dist --include-data-dir=themes=themes --include-data-dir=config=config --include-data-file=img/logo-close.png=logo-close.png --include-data-file=img/refresh.png=refresh.png --include-data-file=img/close_app.png=close_app.png --include-data-file=img/close_app_pressed.png=close_app_pressed.png --include-data-file=kill_dofus.ps1=kill_dofus.ps1 --include-package=ui --include-package=logic --windows-icon-from-ico=img/logo.ico --enable-plugin=pyside6 "main.py"







if exist "dist\main.exe" (
    echo.
    echo %GREEN%###############################################%RESET%
    echo # ✅ Build complete: dist\main.exe
    echo ###############################################%RESET%
) else (
    echo.
    echo %RED%[❌] Build failed! Check console output for details.%RESET%
)

pause
endlocal
