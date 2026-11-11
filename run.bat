@echo off
chcp 65001 >nul
title WebClone v2.0 - Başlatılıyor...
cd /d "%~dp0"

echo ============================================================
echo   WebClone v2.0 Pro - Web Sitesi Kopyalama ve İstihbarat
echo ============================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo [HATA] Python bulunamadı!
        echo Lütfen https://www.python.org adresinden Python 3 yükleyin
        echo ve "Add Python to PATH" seçeneğini işaretleyin.
        echo.
        pause
        exit /b 1
    ) else (
        set PY_CMD=py
    )
) else (
    set PY_CMD=python
)

echo Python bulundu: %PY_CMD%
echo Gerekli kütüphaneler kontrol ediliyor...
%PY_CMD% -m pip install -r requirements.txt --quiet --disable-pip-version-check

echo WebClone Başlatılıyor...
start "" %PY_CMD% gui.py
exit /b 0
