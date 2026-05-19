@echo off
schtasks /Create /TN "KufarFreeBot" /TR "\"%LOCALAPPDATA%\Programs\Python\Python312\python.exe\" \"C:\gamess\kursachrpg\botkufar\bot.py\"" /SC MINUTE /MO 5 /F
echo.
if %ERRORLEVEL%==0 (
    echo Task created! Bot will run every 5 minutes.
) else (
    echo Failed. Try running this file as Administrator.
)
pause
