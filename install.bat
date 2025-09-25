@echo off
echo ========================================
echo    GlobeSpeak Installation Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.12+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo Please reinstall Python with pip
    pause
    exit /b 1
)

echo ✅ pip found

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment created

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing...
)

REM Install requirements
echo.
echo Installing Python packages...
echo This may take several minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo ✅ All packages installed successfully

REM Create .env file if it doesn't exist
if not exist .env (
    echo.
    echo Creating .env file...
    copy env_template.txt .env
    echo ✅ .env file created
    echo ⚠️  Please edit .env file and add your API keys
)

REM Run migrations
echo.
echo Setting up database...
python manage.py makemigrations
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Failed to setup database
    pause
    exit /b 1
)

echo ✅ Database setup complete

REM Collect static files
echo.
echo Collecting static files...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo WARNING: Failed to collect static files
)

echo ✅ Static files collected

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your API keys
echo 2. Run: python manage.py runserver
echo 3. Visit: http://localhost:8000
echo.
echo Note: Make sure FFmpeg and Tesseract are installed
echo See SETUP_GUIDE.md for detailed instructions
echo.
pause
