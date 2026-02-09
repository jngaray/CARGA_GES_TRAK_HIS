@echo off
call "%~dp0config.bat"
echo PYTHON_EXE=%PYTHON_EXE%
if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" --version
) else (
    echo ERROR: El ejecutable %PYTHON_EXE% no existe.
)
pause
