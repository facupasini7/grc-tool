@echo off
echo Instalando PyInstaller...
pip install pyinstaller

echo Generando ejecutable...
pyinstaller --onefile --noconsole --name "NormaLab" ^
  --add-data "static;static" ^
  --add-data "src/data;data" ^
  --hidden-import=sqlite3 ^
  run.py

echo.
echo Ejecutable generado en: dist\NormaLab.exe
pause
