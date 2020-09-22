cd /d "%~dp0"

python.exe tele2_sell.py
pause

rem добавление в автозагрузку
Rem copy Start_tele2_sell.cmd.lnk "%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\"
