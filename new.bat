@echo off
rem ------------------------------
rem CONFIG - change these values
set "PROCESS_NAME=C:\Program Files (x86)\LanSchool\student.exe"
set "INTERFACE_NAME=Wi-Fi 2"
set "POLL_SECONDS=5"
rem ------------------------------

set "MARKER=%TEMP%\wifi_disabled_by_script.marker"

echo Watching for process "%PROCESS_NAME%" and toggling interface "%INTERFACE_NAME%".
echo Run this script as Administrator. Press Ctrl+C to stop.

:loop
tasklist /FI "IMAGENAME eq %PROCESS_NAME%" 2>nul | find /I "%PROCESS_NAME%" >nul
if %ERRORLEVEL%==0 (
    if not exist "%MARKER%" (
        echo Process detected — disabling "%INTERFACE_NAME%"...
        netsh interface set interface name="%INTERFACE_NAME%" admin=DISABLED
        if %ERRORLEVEL%==0 (
            echo disabled > "%MARKER%"
            echo Wi-Fi disabled at %DATE% %TIME%.
        ) else (
            echo Failed to disable interface. Make sure you run as Administrator and the interface name is exactly correct.
        )
    )
) else (
    if exist "%MARKER%" (
        echo Process stopped — re-enabling "%INTERFACE_NAME%"...
        netsh interface set interface name="%INTERFACE_NAME%" admin=ENABLED
        if %ERRORLEVEL%==0 (
            del "%MARKER%" >nul 2>&1
            echo Wi-Fi re-enabled at %DATE% %TIME%.
        ) else (
            echo Failed to enable interface. Manual intervention may be required.
        )
    )
)

timeout /t %POLL_SECONDS% /nobreak >nul
goto loop
