@echo off
echo ========================================
echo Setting up Point and Figure Chart
echo ========================================
echo.

REM Create static folder if not exists
if not exist "static" (
    echo Creating static folder...
    mkdir static
    echo [OK] static folder created
) else (
    echo [OK] static folder already exists
)

REM Check if pnf_chart_frontend.html exists
if exist "pnf_chart_frontend.html" (
    echo Moving pnf_chart_frontend.html to static\index.html...
    move /Y pnf_chart_frontend.html static\index.html
    echo [OK] File moved successfully
) else (
    if not exist "static\index.html" (
        echo [ERROR] Neither pnf_chart_frontend.html nor static\index.html found!
        echo Please download pnf_chart_frontend.html first.
        pause
        exit /b 1
    ) else (
        echo [OK] static\index.html already exists
    )
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Your project structure:
tree /F /A
echo.
echo Now you can run: python main.py
echo.
pause
