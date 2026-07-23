@echo off
setlocal
cd /d "%~dp0"

echo Installing required Python packages...
python -m pip install --upgrade pip
if errorlevel 1 goto :error

python -m pip install -r requirements.txt
if errorlevel 1 goto :error

if not exist "Stereo_Analog_VU_Meter.ico" (
    echo.
    echo ERROR: Stereo_Analog_VU_Meter.ico is missing from this folder.
    goto :error
)

echo.
echo Building Stereo Analog VU Meter...
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --onefile ^
  --name "Stereo Analog VU Meter" ^
  --icon "Stereo_Analog_VU_Meter.ico" ^
  --add-data "Stereo_Analog_VU_Meter.ico;." ^
  --collect-all soundcard ^
  stereo_vu_meter.py

if errorlevel 1 goto :error

echo.
echo ========================================
echo BUILD COMPLETED SUCCESSFULLY
echo EXE: dist\Stereo Analog VU Meter.exe
echo ========================================
pause
exit /b 0

:error
echo.
echo ========================================
echo BUILD FAILED
echo Review the error shown above.
echo ========================================
pause
exit /b 1
