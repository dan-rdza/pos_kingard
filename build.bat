@echo off
title Compilación POS Kingard
color 0A

echo ==========================================
echo   🚀 Compilando ejecutable POS Kingard
echo ==========================================
echo.

cd /d "%~dp0"

:: 1️⃣ Buscar entorno virtual automáticamente
set "VENV_DIR="

for /d %%i in (venv .venv env .env) do (
    if exist "%%i\Scripts\activate.bat" (
        set "VENV_DIR=%%i"
        goto :foundVenv
    )
)
goto :noVenv

:foundVenv
echo 🟢 Entorno virtual encontrado: %VENV_DIR%
call "%VENV_DIR%\Scripts\activate.bat"
goto :continue

:noVenv
echo ⚠️ No se encontró entorno virtual, se usará Python global.
echo.

:continue
:: 2️⃣ Verificar que PyInstaller esté disponible
where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ PyInstaller no está instalado. Instalando...
    pip install pyinstaller
)

:: 3️⃣ Limpiar builds anteriores
echo 🧹 Limpiando compilaciones previas...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del "POS Kingard.spec" 2>nul
echo Hecho.
echo.

:: 4️⃣ Empaquetar con PyInstaller
echo ⚙️ Ejecutando PyInstaller...
pyinstaller main.py ^
 --onefile ^
 --noconsole ^
 --icon=assets\images\logo.ico ^
 --add-data "assets\images;assets\images" ^
 --add-data "database\schema.sql;database" ^
 --add-data "assets\images\logo.ico;assets" ^
 --name "POS Kingard"

if %ERRORLEVEL% neq 0 (
    color 0C
    echo ❌ Error durante la compilación.
    pause
    exit /b 1
)

echo.
echo ✅ Compilación completada exitosamente.
echo ------------------------------------------
echo El archivo final se encuentra en:
echo   dist\POS Kingard.exe
echo ------------------------------------------
echo.

pause
