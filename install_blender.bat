@echo off
setlocal
set BLENDER_DIR=%~dp0external\blender
set BLENDER_EXE=%BLENDER_DIR%\blender.exe

if exist "%BLENDER_EXE%" (
    echo Blender already installed.
    exit /b 0
)

if not exist "%BLENDER_DIR%" mkdir "%BLENDER_DIR%"

echo Downloading Blender portable...
curl -L -o "%BLENDER_DIR%\blender.zip" https://download.blender.org/release/Blender3.6/blender-3.6.0-windows-x64.zip
if %ERRORLEVEL% NEQ 0 (
    echo Failed to download Blender. Skipping.
    exit /b 0
)
powershell -ExecutionPolicy Bypass -Command "Expand-Archive -Path '%BLENDER_DIR%\blender.zip' -DestinationPath '%BLENDER_DIR%' -Force"
del "%BLENDER_DIR%\blender.zip"

if exist "%BLENDER_EXE%" (
    echo Blender installed to %BLENDER_DIR%.
) else (
    echo Failed to install Blender.
)
endlocal
