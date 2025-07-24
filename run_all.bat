@echo off
chcp 65001 >nul
setlocal ENABLEDELAYEDEXPANSION

set "EMULATOR_PATH=C:\Users\ADMIN\AppData\Local\Android\Sdk\emulator\emulator.exe"
set "ADB_PATH=C:\Users\ADMIN\AppData\Local\Android\Sdk\platform-tools"
set PATH=%ADB_PATH%;%PATH%

echo Dang tim cac thiet bi ao (AVD)...

for /f "tokens=*" %%i in ('"%EMULATOR_PATH%" -list-avds') do (
    echo Khoi dong may ao %%i...
    start "" "%EMULATOR_PATH%" -avd %%i -no-window -no-audio -gpu off
    timeout /t 5 /nobreak >nul
)

echo Doi cac thiet bi ao san sang...
timeout /t 60 /nobreak >nul

echo Dang chay auto_youtube.py...
python auto_youtube.py

echo Cho 150s de dam bao video duoc upload...
timeout /t 150 /nobreak >nul

pause
endlocal
