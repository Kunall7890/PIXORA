@echo off
REM Pixora Quick Start Script for Windows

echo 🎨 Pixora Creative Engine - Quick Start
echo ========================================
echo.

REM Check Python version
python --version
echo ✓ Python found

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
) else (
    echo ✓ Virtual environment exists
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -q -r requirements.txt

REM Setup environment
if not exist ".env" (
    echo ⚙️  Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env and add your API keys:
    echo    - GROQ_API_KEY (required)
    echo    - REPLICATE_API_TOKEN (optional)
) else (
    echo ✓ .env file exists
)

REM Create required directories
echo 📁 Creating directories...
if not exist "outputs\images" mkdir outputs\images
if not exist "outputs\videos" mkdir outputs\videos
if not exist "logs" mkdir logs

echo.
echo ✅ Setup complete!
echo.
echo 🚀 Next steps:
echo.
echo 1. Edit .env and add your Groq API key:
echo    notepad .env
echo.
echo 2. Start the backend (Terminal 1):
echo    python -m api.main
echo.
echo 3. Start the frontend (Terminal 2):
echo    streamlit run frontend/app.py
echo.
echo 4. Open browser:
echo    http://localhost:8501
echo.
echo 📖 Documentation: README.md
pause
