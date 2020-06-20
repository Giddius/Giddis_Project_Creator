@echo off
setlocal enableextensions enabledelayedexpansion

echo.
echo.
echo ----------------------------------------------------------------------------------------------------
rem Titel
echo ----------------------------------------------------------------------------------------------------
echo.
echo.





timeout /t 15


rem Timeout with interrupt:
rem CHOICE /C WN /D N /T 10 /M "press [W] in the next 10 seconds if you want to keep the window open"
rem IF %ERRORLEVEL% EQU 1 Pause
rem IF %ERRORLEVEL% EQU 2 Exit


rem get Clipboarddata: powershell -sta "add-type -as System.Windows.Forms; [windows.forms.clipboard]::GetText()"
