@echo off

:loop

@echo Processing file: %1
python.exe .\main.py %1
@echo "Done!"

shift
if not "%~1"=="" goto loop

@REM pause