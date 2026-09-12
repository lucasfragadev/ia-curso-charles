@echo off
echo.
echo =====================================================
echo   AuditoriaSUS - Gerador de Executavel (.exe)
echo   Instituto do Cerebro
echo =====================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERRO] Ambiente virtual .venv nao encontrado!
    echo        Execute este script dentro da pasta procedimentos-sus.
    pause
    exit /b 1
)

echo [1/4] Verificando PyInstaller...
.venv\Scripts\pip.exe install pyinstaller --quiet --upgrade
if errorlevel 1 (
    echo [ERRO] Falha ao instalar PyInstaller.
    pause
    exit /b 1
)
echo       OK.
echo.

echo [2/4] Limpando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "AuditoriaSUS.spec" del /q "AuditoriaSUS.spec"
echo       OK.
echo.

echo [3/4] Gerando AuditoriaSUS.exe (aguarde alguns minutos)...
.venv\Scripts\pyinstaller.exe --onefile --windowed --name AuditoriaSUS --add-data "templates;templates" --hidden-import "src.auditoria_modelo01" --hidden-import "src.auditoria_modelo02" --hidden-import "src.config" --collect-submodules src --collect-all openpyxl --collect-all et_xmlfile app.py

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao gerar o executavel. Verifique as mensagens acima.
    pause
    exit /b 1
)

echo.
echo [4/4] Copiando base de dados SIGTAP para dist\...
if exist "data" (
    xcopy /E /I /Y /Q "data" "dist\data"
    echo       Pasta data\ copiada com sucesso.
) else (
    echo [AVISO] Pasta data\ nao encontrada. Copie manualmente para dist\.
)

if exist "build" rmdir /s /q "build"
if exist "AuditoriaSUS.spec" del /q "AuditoriaSUS.spec"

echo.
echo =====================================================
echo   PRONTO!
echo   Executavel gerado em: dist\AuditoriaSUS.exe
echo   Base de dados em    : dist\data\
echo.
echo   Para distribuir, copie a pasta dist\ inteira.
echo =====================================================
echo.
pause
