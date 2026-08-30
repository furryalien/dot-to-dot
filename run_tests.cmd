@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE="
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"

if not defined PYTHON_EXE (
    python --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_EXE=python"
)

if not defined PYTHON_EXE (
    echo Python was not found. Installing Python 3.12...
    where winget >nul 2>&1 || (
        echo ERROR: Python is required and winget is unavailable.
        exit /b 1
    )
    winget install --id Python.Python.3.12 --exact --silent --accept-package-agreements --accept-source-agreements
    if errorlevel 1 exit /b %errorlevel%
    for /d %%D in ("%LocalAppData%\Programs\Python\Python312*") do set "PYTHON_EXE=%%~fD\python.exe"
)

if not defined PYTHON_EXE (
    echo ERROR: Python installation could not be located.
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    "%PYTHON_EXE%" -m venv .venv || exit /b 1
)

set "PYTHON_EXE=.venv\Scripts\python.exe"
echo Installing dependencies...
"%PYTHON_EXE%" -m pip install --disable-pip-version-check -r requirements.txt || exit /b 1

echo Running tests...
"%PYTHON_EXE%" -m unittest discover -s tests -v
exit /b %errorlevel%