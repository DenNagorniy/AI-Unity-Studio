@echo off
setlocal
set SCRIPT_DIR=%~dp0

REM Ensure Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%install_python.ps1"
)

python -c "import sys; exit(0) if sys.version_info >= (3,10) else exit(1)"
if %ERRORLEVEL% NEQ 0 (
    echo Python 3.10 or higher is required.
    exit /b 1
)

python -m pip install -r "%SCRIPT_DIR%requirements-full.txt"

python "%SCRIPT_DIR%env_setup.py"

call "%SCRIPT_DIR%install_blender.bat"
call "%SCRIPT_DIR%install_invokeai.bat"
call "%SCRIPT_DIR%install_local_llm.bat"

python "%SCRIPT_DIR%ai_unity_studio_launcher.py"
endlocal
