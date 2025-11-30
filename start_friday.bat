@echo off
echo ========================================
echo Starting Friday Voice Assistant
echo ========================================
echo.
echo Starting Agent Worker...
echo.
start "Friday Agent" cmd /k "D:/Ashok/_AI/_AGENTS/JARVIS_MOBILE/venv/Scripts/python.exe agent.py start"
timeout /t 3 /nobreak > nul
echo.
echo Starting GUI Client...
echo.
start "Friday GUI" cmd /k "D:/Ashok/_AI/_AGENTS/JARVIS_MOBILE/venv/Scripts/python.exe voice_assistant_gui_auto.py"
echo.
echo ========================================
echo Both terminals opened!
echo ========================================
echo.
echo 1. Wait for agent to show "registered worker"
echo 2. Click "Start Call" in the GUI
echo 3. Just talk naturally - no buttons needed!
echo.
pause
