@echo off
setlocal
set OLLAMA_DIR=%~dp0tools\ollama
set OLLAMA_EXE=%OLLAMA_DIR%\ollama.exe

if exist "%OLLAMA_EXE%" (
    echo Ollama already installed.
) else (
    if not exist "%OLLAMA_DIR%" mkdir "%OLLAMA_DIR%"
    echo Downloading Ollama...
    curl -L -o "%OLLAMA_DIR%\ollama.zip" https://ollama.com/download/OllamaWindows.zip
    powershell -ExecutionPolicy Bypass -Command "Expand-Archive -Path '%OLLAMA_DIR%\ollama.zip' -DestinationPath '%OLLAMA_DIR%' -Force"
    del "%OLLAMA_DIR%\ollama.zip"
)

"%OLLAMA_EXE%" pull llama3
endlocal
