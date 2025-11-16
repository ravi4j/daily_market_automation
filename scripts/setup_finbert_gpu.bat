@echo off
REM Setup FinBERT with GPU Support (Windows with NVIDIA GPU)
REM This script installs PyTorch with CUDA support for faster sentiment analysis

echo ========================================
echo   FinBERT GPU Setup (Windows)
echo ========================================
echo.

REM Check if running from project root
if not exist "venv" (
    echo [X] Virtual environment not found!
    echo     Run this from the project root after running setup_local.bat
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/5] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check CUDA availability (informational)
echo.
echo [2/5] Checking for NVIDIA GPU...
python -c "import torch; print(f'Current PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')" 2>nul
if errorlevel 1 (
    echo     PyTorch not installed yet - will install with GPU support
)

echo.
echo [3/5] Which CUDA version does your GPU support?
echo.
echo     1. CUDA 11.8 (Recommended for most GPUs)
echo     2. CUDA 12.1 (For newer GPUs - RTX 40 series)
echo     3. Skip GPU setup (use CPU only)
echo.
set /p CUDA_CHOICE="Enter choice (1-3): "

if "%CUDA_CHOICE%"=="3" (
    echo.
    echo Skipping GPU setup - will use CPU
    goto CPU_ONLY
)

if "%CUDA_CHOICE%"=="2" (
    set TORCH_INDEX=https://download.pytorch.org/whl/cu121
    set CUDA_VER=12.1
) else (
    set TORCH_INDEX=https://download.pytorch.org/whl/cu118
    set CUDA_VER=11.8
)

echo.
echo [4/5] Installing PyTorch with CUDA %CUDA_VER% support...
echo     This may take 2-5 minutes (downloading ~2GB)...
echo.

REM Uninstall existing torch if present
pip uninstall -y torch torchvision 2>nul

REM Install PyTorch with CUDA
pip install torch torchvision --index-url %TORCH_INDEX%
if errorlevel 1 (
    echo.
    echo [X] Failed to install PyTorch with GPU support
    echo     Falling back to CPU version...
    goto CPU_ONLY
)

goto INSTALL_TRANSFORMERS

:CPU_ONLY
echo.
echo [4/5] Installing PyTorch (CPU version)...
pip install torch>=2.1.0

:INSTALL_TRANSFORMERS
echo.
echo [5/5] Installing Transformers library...
pip install transformers>=4.35.0

echo.
echo ========================================
echo   Testing Installation
echo ========================================
echo.

REM Test GPU availability
python -c "import torch; cuda_available = torch.cuda.is_available(); print(f'CUDA Available: {cuda_available}'); print(f'Device: {torch.cuda.get_device_name(0) if cuda_available else \"CPU\"}'); print(f'PyTorch version: {torch.__version__}')"

if errorlevel 1 (
    echo [X] Installation test failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Test FinBERT: python src\finbert_sentiment.py
echo   2. Run news scanner: python scripts\send_news_opportunities.py
echo.
echo Performance:
echo   - With GPU: ~10-50x faster than CPU
echo   - Model loads in 2-3 seconds
echo   - Each sentiment analysis: ~0.01-0.05 seconds
echo.
pause

