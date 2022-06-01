@echo off

REM Allows to keep the console window open after an error

setlocal ENABLEDELAYEDEXPANSION

set filename=%~n0
set blank=
set filename=%filename:.debug=!blank!%
set python_file=%filename%.py

python "%~dp0%python_file%" %*

IF %ERRORLEVEL% NEQ 0 PAUSE