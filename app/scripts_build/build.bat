@echo off
echo.
echo =====================================================
echo   AuditoriaSUS - Gerador de Executavel (.exe)
echo   Instituto do Cerebro
echo =====================================================
echo.

echo [1/3] Verificando PyInstaller...
..\..\Aula02\documentos\procedimentos-sus\.venv\Scripts\pip.exe install pyinstaller --quiet --upgrade

echo [2/3] Limpando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "AuditoriaSUS.spec" del /q "AuditoriaSUS.spec"

echo [3/3] Gerando AuditoriaSUS.exe (aguarde)...
..\..\Aula02\documentos\procedimentos-sus\.venv\Scripts\pyinstaller.exe --onefile --windowed --name AuditoriaSUS --paths ".." --add-data "..\web\templates;web\templates" --add-data "..\data;data" --hidden-import "core.auditoria_escala" --hidden-import "sigtap.config" --collect-submodules core --collect-all openpyxl --collect-all et_xmlfile ..\web\server.py

echo.
echo [OK] Executavel gerado com sucesso!
pause
