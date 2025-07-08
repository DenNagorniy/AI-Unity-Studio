@echo off
setlocal
set MISTRAL_PATH=%~dp0external\ollama\mistral.q4_K_M.gguf
set SDXL_PATH=%~dp0external\models\sdxl\sd_xl_base_1.0.safetensors

if exist "%MISTRAL_PATH%" (
    echo Mistral model already present.
) else (
    if not exist "%~dp0external\ollama" mkdir "%~dp0external\ollama"
    echo Downloading Mistral model...
    curl -L -o "%MISTRAL_PATH%" https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to download Mistral model. Skipping.
    )
)

if exist "%SDXL_PATH%" (
    echo SDXL model already present.
) else (
    if not exist "%~dp0external\models\sdxl" mkdir "%~dp0external\models\sdxl"
    echo Downloading SDXL model...
    curl -L -o "%SDXL_PATH%" https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to download SDXL model. Skipping.
    )
)
endlocal
