@echo off
echo ========================================
echo RescuNav Quick Setup Script
echo ========================================
echo.

echo Checking Python version...
python --version
echo.

echo ========================================
echo SETUP OPTIONS:
echo ========================================
echo.
echo [1] MINIMAL - Core dependencies only (5 min)
echo     - Building navigation
echo     - Danger simulation
echo     - Basic rescue agents
echo.
echo [2] STANDARD - Web UI + Database (10 min)
echo     - Everything in Minimal
echo     - Web interface
echo     - Database support
echo     - Video processing
echo.
echo [3] FULL - All features (30+ min)
echo     - Everything in Standard
echo     - 3D visualization
echo     - AI2Thor simulation
echo     - Deep learning (5-10 GB!)
echo.
echo [4] TEST ONLY - Check what's installed
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" goto minimal
if "%choice%"=="2" goto standard
if "%choice%"=="3" goto full
if "%choice%"=="4" goto test
goto invalid

:minimal
echo.
echo ========================================
echo Installing MINIMAL dependencies...
echo ========================================
pip install networkx>=3.1
echo.
echo ✓ Minimal setup complete!
echo.
echo You can now run:
echo   python building_navigator.py
echo   python danger_simulator.py
echo   python test_rescue_system.py
goto end

:standard
echo.
echo ========================================
echo Installing STANDARD dependencies...
echo ========================================
pip install networkx>=3.1 pymongo>=4.6.0 flask>=2.3.0 opencv-python>=4.8.0 python-dotenv>=1.0.0 matplotlib>=3.7.0 scipy>=1.11.0 requests>=2.31.0
echo.
echo ✓ Standard setup complete!
echo.
echo Next steps:
echo 1. Configure API keys in .env file (optional)
echo 2. Run: python test_rescue_system.py
echo 3. Run: python web_app.py
goto end

:full
echo.
echo ========================================
echo Installing FULL dependencies...
echo WARNING: This will download 5-10 GB!
echo ========================================
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" goto end
pip install -r requirements_rescue.txt
echo.
echo ✓ Full setup complete!
echo.
echo Next steps:
echo 1. Configure API keys in .env file
echo 2. Run: python test_rescue_system.py
echo 3. Run: python rescue_simulation.py --scenario fire --iterations 5
goto end

:test
echo.
echo ========================================
echo Checking installed packages...
echo ========================================
python -c "try:
    import networkx; print('✓ networkx:', networkx.__version__)
except: print('✗ networkx NOT installed')
try:
    import numpy; print('✓ numpy:', numpy.__version__)
except: print('✗ numpy NOT installed')
try:
    import pymongo; print('✓ pymongo:', pymongo.__version__)
except: print('✗ pymongo NOT installed')
try:
    import flask; print('✓ flask:', flask.__version__)
except: print('✗ flask NOT installed')
try:
    import cv2; print('✓ opencv:', cv2.__version__)
except: print('✗ opencv NOT installed')
try:
    import matplotlib; print('✓ matplotlib:', matplotlib.__version__)
except: print('✗ matplotlib NOT installed')
try:
    import scipy; print('✓ scipy:', scipy.__version__)
except: print('✗ scipy NOT installed')
try:
    import requests; print('✓ requests:', requests.__version__)
except: print('✗ requests NOT installed')
try:
    from dotenv import load_dotenv; print('✓ python-dotenv installed')
except: print('✗ python-dotenv NOT installed')"
echo.
echo See SETUP_STATUS_REPORT.md for details
goto end

:invalid
echo.
echo Invalid choice. Please run again and select 1-4.
goto end

:end
echo.
echo ========================================
echo Setup script finished
echo ========================================
echo.
echo For detailed setup info, see:
echo   SETUP_STATUS_REPORT.md
echo.
pause
