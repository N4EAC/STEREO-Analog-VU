@echo off
setlocal
cd /d "%~dp0"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --onefile ^
  --name "Stereo Analog VU Meter" ^
  stereo_vu_meter.py

echo.
echo Build complete. Check the dist folder.
pause
