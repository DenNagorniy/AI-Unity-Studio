@echo off
setlocal
set INVOKE_DIR=%~dp0tools\invokeai
set INVOKE_EXE=%INVOKE_DIR%\Scripts\invokeai.exe

if exist "%INVOKE_EXE%" (
    echo InvokeAI already installed.
    exit /b 0
)

if not exist "%INVOKE_DIR%" mkdir "%INVOKE_DIR%"

echo Cloning InvokeAI...
git clone --depth 1 https://github.com/invoke-ai/InvokeAI.git "%INVOKE_DIR%"

pushd "%INVOKE_DIR%"
python -m pip install -r requirements.txt
python scripts/preload_models.py --yes
popd

echo InvokeAI installed.
endlocal
