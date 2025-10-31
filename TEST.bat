@echo off
setlocal enabledelayedexpansion

rem --- config ---
set "LOGFILE=%USERPROFILE%\Desktop\IMPORTANT\README.txt"
mkdir "%USERPROFILE%\Desktop\IMPORTANT" 2>nul
set /a max_chances=3
set /a countdown_seconds=3

rem --- header in log ---
echo ----- %date% %time% ----- >> "%LOGFILE%"

rem --- ask loop ---
set /a chances=%max_chances%
:askloop
if %chances% LEQ 0 goto out_of_chances

set /p UsrInput=ARE YOU SURE YOU WANT TO DO THIS, THIS COULD HARM YOUR COMPUTER! (Y/N): 
echo [%date% %time%] Response: %UsrInput% >> "%LOGFILE%"

if /I "%UsrInput%"=="Y" goto confirmed
if /I "%UsrInput%"=="Yes" goto confirmed
if /I "%UsrInput%"=="N" goto cancelled
if /I "%UsrInput%"=="No" goto cancelled

rem not recognized
set /a chances-=1
echo Input not recognized. You have %chances% chance(s) left.
goto askloop

:confirmed
echo You chose YES. Beginning countdown...
echo [%date% %time%] CONFIRMED >> "%LOGFILE%"

rem --- countdown ---
for /L %%C in (%countdown_seconds%,-1,1) do (
    echo %%C...
    timeout /t 1 /nobreak >nul
)

rem --- SAFE ACTION (change this) ---
echo Running safe action now.
start "" notepad.exe

goto finish

:cancelled
echo You chose NO. Exiting.
echo [%date% %time%] CANCELLED >> "%LOGFILE%"
goto finish

:out_of_chances
echo Out of chances. Exiting.
echo [%date% %time%] OUT OF CHANCES >> "%LOGFILE%"
goto finish

:finish
echo Done. Press any key to exit.
pause >nul
endlocal
exit /b
