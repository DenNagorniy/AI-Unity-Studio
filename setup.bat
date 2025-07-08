@echo off
setlocal

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    powershell -ExecutionPolicy Bypass -File install_python.ps1
)

python -c "import sys; exit(0) if sys.version_info >= (3,10) else exit(1)"
if %ERRORLEVEL% NEQ 0 (
    echo Python 3.10 or higher is required.
    exit /b 1
)

python env_setup.py
python -m pip install -r requirements-full.txt

set SCRIPT_DIR=%~dp0
powershell -ExecutionPolicy Bypass -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\AI Unity Studio.lnk');$s.TargetPath='python';$s.Arguments='\"%SCRIPT_DIR%ai_unity_studio_launcher.py\"';$s.WorkingDirectory='%SCRIPT_DIR%';$s.Save()"

python ai_unity_studio_launcher.py
endlocal
