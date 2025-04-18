@echo off
title MBomb - SMS/Call/WhatsApp Bomber
color 0a

:start
cls
echo.
echo  [1] SMS Bomber
echo  [2] Call Bomber
echo  [3] WhatsApp Bomber
echo  [4] Exit
echo  [5] Update
echo  [6] About
echo  [7] Rate Us
echo  [8] More
echo.

set /p choice="Enter your choice: "

if "%choice%"=="1" (
    python bomber.py --sms
    if errorlevel 1 (
        echo Error running SMS Bomber
        echo Check mbomb.log for details
        pause
    )
    goto start
)
if "%choice%"=="2" (
    python bomber.py --call
    if errorlevel 1 (
        echo Error running Call Bomber
        echo Check mbomb.log for details
        pause
    )
    goto start
)
if "%choice%"=="3" (
    python bomber.py --whatsapp
    if errorlevel 1 (
        echo Error running WhatsApp Bomber
        echo Check mbomb.log for details
        pause
    )
    goto start
)
if "%choice%"=="4" (
    exit
)
if "%choice%"=="5" (
    echo Updating...
    git pull
    if errorlevel 1 (
        echo Error updating
        echo Please check your internet connection
        pause
    )
    goto start
)
if "%choice%"=="6" (
    cls
    echo MBomb - SMS/Call/WhatsApp Bomber
    echo Version: 2.2b
    echo.
    echo Contributors:
    echo - TezX
    echo - Mansh Kumar
    echo - mintu Virus
    echo - WH No- +91-8809377701
    echo.
    pause
    goto start
)
if "%choice%"=="7" (
    start https://github.com/TezX/MBomb
    goto start
)
if "%choice%"=="8" (
    start https://github.com/TezX/MBomb#readme
    goto start
)

echo Invalid choice!
timeout /t 2
goto start 