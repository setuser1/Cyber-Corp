@echo off
echo Opening Notepad 100 times...

for /l %%i in (1,1,100) do (
    start "" notepad.exe
)

echo Waiting a few seconds for instances to load...
timeout /t 5 /nobreak >nul

echo Closing all Notepad instances...
taskkill /f /im notepad.exe