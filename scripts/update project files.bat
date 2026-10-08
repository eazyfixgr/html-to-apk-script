@echo off
cd /d "%~dp0"

:menu
cls
echo ========================================
echo    Capacitor Commands Menu
echo ========================================
echo Current directory: %CD%
echo.
echo 1. Sync + Copy + Open Android (Full build)
echo 2. Sync only
echo 3. Copy only
echo 4. Open Android
echo 5. Open iOS
echo 6. Sync + Copy only
echo 7. Build + Sync + Copy + Open Android
echo 8. Clean + Sync + Copy + Open Android
echo 9. Add Android platform
echo 10. Add iOS platform
echo 11. List installed platforms
echo 12. Update Capacitor
echo 0. Exit
echo.
set /p choice="Enter your choice (0-12): "

if "%choice%"=="1" goto full_android
if "%choice%"=="2" goto sync_only
if "%choice%"=="3" goto copy_only
if "%choice%"=="4" goto open_android
if "%choice%"=="5" goto open_ios
if "%choice%"=="6" goto sync_copy
if "%choice%"=="7" goto build_full_android
if "%choice%"=="8" goto clean_full_android
if "%choice%"=="9" goto add_android
if "%choice%"=="10" goto add_ios
if "%choice%"=="11" goto list_platforms
if "%choice%"=="12" goto update_cap
if "%choice%"=="0" goto exit
echo Invalid choice. Please try again.
pause
goto menu

:full_android
echo Running: Sync + Copy + Open Android...
npx cap sync
npx cap copy
npx cap open android
echo.
echo Completed!
pause
goto menu

:sync_only
echo Running: Sync only...
npx cap sync
echo.
echo Completed!
pause
goto menu

:copy_only
echo Running: Copy only...
npx cap copy
echo.
echo Completed!
pause
goto menu

:open_android
echo Running: Open Android...
npx cap open android
echo.
echo Completed!
pause
goto menu

:open_ios
echo Running: Open iOS...
npx cap open ios
echo.
echo Completed!
pause
goto menu

:sync_copy
echo Running: Sync + Copy...
npx cap sync
npx cap copy
echo.
echo Completed!
pause
goto menu

:build_full_android
echo Running: Build + Sync + Copy + Open Android...
npm run build
npx cap sync
npx cap copy
npx cap open android
echo.
echo Completed!
pause
goto menu

:clean_full_android
echo Running: Clean + Sync + Copy + Open Android...
npx cap sync --clean
npx cap copy
npx cap open android
echo.
echo Completed!
pause
goto menu

:add_android
echo Running: Add Android platform...
npx cap add android
echo.
echo Completed!
pause
goto menu

:add_ios
echo Running: Add iOS platform...
npx cap add ios
echo.
echo Completed!
pause
goto menu

:list_platforms
echo Listing installed platforms...
echo Current directory: %CD%
echo.
echo Running command: npx cap ls
echo.
call npx cap ls
echo.
echo Command finished with exit code: %ERRORLEVEL%
echo.
echo Press any key to return to menu...
pause
goto menu

:update_cap
echo Updating Capacitor...
npm install @capacitor/core@latest @capacitor/cli@latest
npx cap sync
echo.
echo Completed!
pause
goto menu

:exit
echo Goodbye!
exit /b