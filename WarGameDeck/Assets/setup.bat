@echo off
echo Verification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python n'est pas installe.
    echo.
    echo Installation de Python via winget...
    winget install Python.Python.3.12
    if %errorlevel% neq 0 (
        echo.
        echo Erreur lors de l'installation automatique.
        echo Veuillez installer Python manuellement depuis: https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    )
    echo Python installe avec succes!
) else (
    echo Python est deja installe.
    python --version
)

echo.
echo Installation des dependances Python...
pip install requests
if %errorlevel% neq 0 (
    echo Erreur lors de l'installation des dependances.
    pause
    exit /b 1
)

echo.
echo Configuration terminee!
pause
