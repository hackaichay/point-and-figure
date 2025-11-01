@echo off
chcp 65001 > nul
cls
echo ╔════════════════════════════════════════════════════════╗
echo ║                                                        ║
echo ║     Point and Figure Chart - Auto Setup Script        ║
echo ║                                                        ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Get current directory
set "PROJECT_DIR=%cd%"
echo 📂 Project Directory: %PROJECT_DIR%
echo.

REM Step 1: Check Python
echo ═══════════════════════════════════════════════════════
echo Step 1/5: Checking Python...
echo ═══════════════════════════════════════════════════════
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo    Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)
python --version
echo ✅ Python OK
echo.

REM Step 2: Create static folder
echo ═══════════════════════════════════════════════════════
echo Step 2/5: Creating static folder...
echo ═══════════════════════════════════════════════════════
if not exist "static" (
    mkdir static
    echo ✅ Created static folder
) else (
    echo ✅ static folder already exists
)
echo.

REM Step 3: Setup index.html
echo ═══════════════════════════════════════════════════════
echo Step 3/5: Setting up index.html...
echo ═══════════════════════════════════════════════════════
if exist "pnf_chart_frontend.html" (
    echo 📄 Found pnf_chart_frontend.html
    echo    Moving to static\index.html...
    move /Y pnf_chart_frontend.html static\index.html >nul
    echo ✅ Moved successfully
) else if exist "static\index.html" (
    echo ✅ static\index.html already exists
) else (
    echo ⚠️  Warning: Neither pnf_chart_frontend.html nor static\index.html found
    echo    The web interface may not work until you add index.html
)
echo.

REM Step 4: Install dependencies
echo ═══════════════════════════════════════════════════════
echo Step 4/5: Installing dependencies...
echo ═══════════════════════════════════════════════════════
if exist "requirements.txt" (
    echo 📦 Installing packages from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ⚠️  Some packages failed to install
        echo    You may need to install manually
    ) else (
        echo ✅ All packages installed
    )
) else (
    echo ⚠️  requirements.txt not found
    echo    Skipping package installation
)
echo.

REM Step 5: Verify setup
echo ═══════════════════════════════════════════════════════
echo Step 5/5: Verifying setup...
echo ═══════════════════════════════════════════════════════
set "ERRORS=0"

if not exist "main.py" (
    echo ❌ main.py not found
    set "ERRORS=1"
) else (
    echo ✅ main.py found
)

if not exist "mt5_connector.py" (
    echo ❌ mt5_connector.py not found
    set "ERRORS=1"
) else (
    echo ✅ mt5_connector.py found
)

if not exist "pnf_calculator.py" (
    echo ❌ pnf_calculator.py not found
    set "ERRORS=1"
) else (
    echo ✅ pnf_calculator.py found
)

if not exist "config.json" (
    echo ⚠️  config.json not found (you'll need to create it)
) else (
    echo ✅ config.json found
)

if not exist "static\index.html" (
    echo ❌ static\index.html not found
    set "ERRORS=1"
) else (
    echo ✅ static\index.html found
)

echo.

if "%ERRORS%"=="1" (
    echo ═══════════════════════════════════════════════════════
    echo ❌ Setup incomplete - Some files are missing
    echo ═══════════════════════════════════════════════════════
    echo Please download missing files and run setup again
    echo.
    pause
    exit /b 1
)

echo ═══════════════════════════════════════════════════════
echo ✅ Setup Complete!
echo ═══════════════════════════════════════════════════════
echo.
echo 📁 Project Structure:
echo.
tree /F /A
echo.
echo ═══════════════════════════════════════════════════════
echo 📝 Next Steps:
echo ═══════════════════════════════════════════════════════
echo.
echo 1. Edit config.json:
echo    - Set your MT5 login
echo    - Set your MT5 password
echo    - Set your MT5 server
echo.
echo 2. Make sure MetaTrader 5 is installed and running
echo.
echo 3. Start the application:
echo    ^> python main.py
echo.
echo 4. Open browser:
echo    http://localhost:8000
echo.
echo ═══════════════════════════════════════════════════════
echo.
choice /C YN /M "Do you want to start the application now"
if errorlevel 2 goto :end
if errorlevel 1 goto :start

:start
echo.
echo Starting application...
echo.
python main.py
goto :end

:end
echo.
echo Thank you! 🎉
echo.
pause
