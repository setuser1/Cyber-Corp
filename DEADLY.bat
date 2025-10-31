@echo off
setlocal enabledelayedexpansion


set "LOGFILE=%USERPROFILE%\Desktop\IMPORTANT\README.txt"
mkdir "%USERPROFILE%\Desktop\IMPORTANT" 2>nul
set /a max_chances=3
set /a countdown_seconds=3

echo ----- %date% %time% ----- >> "%LOGFILE%"

set /a chances=%max_chances%
:askloop
if %chances% LEQ 0 goto out_of_chances

set /p UsrInput=ARE YOU SURE YOU WANT TO DO THIS, THIS COULD HARM YOUR COMPUTER! (Y/N): 
echo [%date% %time%] Response: %UsrInput% >> "%LOGFILE%"

if /I "%UsrInput%"=="Y" goto confirmed
if /I "%UsrInput%"=="Yes" goto confirmed
if /I "%UsrInput%"=="N" goto cancelled
if /I "%UsrInput%"=="No" goto cancelled


set /a chances-=1
echo Input not recognized. You have %chances% chance(s) left.
goto askloop

:confirmed
echo You chose YES. Beginning countdown...
echo [%date% %time%] CONFIRMED >> "%LOGFILE%"
for /L %%C in (%countdown_seconds%,-1,1) do (
    echo COUNTDOWN: %%C...
    timeout /t 1 /nobreak >nul
)
goto infloop
:infloop
start C:\Windows\explorer.exe
start %LocalAppData%\Microsoft\WindowsApps\wt.exe
start C:\Windows\notepad.exe
call %LocalAppData%\Microsoft\WindowsApps\mspaint.exe
call "R A M  D E A T H" wt.exe "C:\Users\bh37150_sersd\Desktop\infloop.bat"
call "O V E R  H E A T" wt.exe "C:\Users\bh37150_sersd\Desktop\infloop.bat"
goto infloop

:cancelled
echo You chose NO. Exiting.
echo [%date% %time%] CANCELLED >> "%LOGFILE%"
timeout /t 1 /nobreak >nul
goto finish

:out_of_chances
echo Out of chances. Exiting.
echo [%date% %time%] OUT OF CHANCES >> "%LOGFILE%"
timeout /t 1 /nobreak >nul
goto finish

:finish
endlocal
exit /b

