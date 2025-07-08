@echo off
setlocal
set INVOKE_DIR=%~dp0external\invokeai
set REQ_FILE=%INVOKE_DIR%\requirements.txt

if exist "%REQ_FILE%" (
    echo InvokeAI already installed.
    exit /b 0
)

if not exist "%INVOKE_DIR%" mkdir "%INVOKE_DIR%"

echo Cloning InvokeAI...
git clone --depth 1 https://github.com/invoke-ai/InvokeAI.git "%INVOKE_DIR%"
if %ERRORLEVEL% NEQ 0 (
    echo Failed to clone InvokeAI. Skipping.
    exit /b 0
)

pushd "%INVOKE_DIR%"
python -m pip install -r requirements.txt
if exist scripts\preload_models.py (
    python scripts\preload_models.py --yes
)
popd

echo InvokeAI installed.
endlocal
