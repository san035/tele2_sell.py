echo Start/Run/Запуск: Start_any_py_file.cmd py_file
set py_file=%1
set num_call=%2
@if _%num_call%==_ (set num_call=1)

echo Определяем путь к PayPro и IP серевера из реестра
For /F "Tokens=2*" %%I In ('Reg Query "HKCU\SkorPay" /V paypro_path') Do Set paypro_path=%%J
For /F "Tokens=2*" %%I In ('Reg Query "HKCU\SkorPay" /V ip_current_server') Do Set ip_current_server=http://%%J
@if _%ip_current_server%==_ (pause)&(exit)
@if _%paypro_path%==_ (pause)&(exit)
@if _%py_file%==_ (pause)&(exit)
@if NOT EXIST %py_file% (echo No file %py_file%)&(exit)
set Opera="C:\Program Files\Opera\launcher.exe"
if not exist %Opera% (set Opera="C:\Program Files (x86)\Opera\launcher.exe")
if not exist %Opera% (echo No Opera)&(exit)

rem close old win %py_file%
echo %paypro_path%san/nircmd.exe win close ititle %py_file%
TIMEOUT 1

cd /d %~dp0
title _%py_file% %date% %time% call %num_call%
python.exe %py_file%

TIMEOUT 90
rem activate windows with error
%paypro_path%san/nircmd.exe win max ititle _%py_file%

rem create screenshot
For /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set FILE_SCREENSHOT=img/shot-%date%_%mytime%.jpg
%paypro_path%san/nircmd.exe savescreenshot %FILE_SCREENSHOT%

%Opera% "https://api.telegram.org/bot910956210:AAGy4DTGALEwaSM959XwTp1MKrdgtWhPVhs/sendMessage?text=Error %py_file% %ip_current_server%/%FILE_SCREENSHOT%&chat_id=-261805546"

TIMEOUT 60
echo call self
set /a num_call =%num_call%+1
call %~n0 %py_file% %num_call%