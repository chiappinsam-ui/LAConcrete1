@echo off
echo Waking up the AI Server and opening the Ngrok tunnel...

:: 1. Start the Flask server in its own window
start "AI Server" cmd /k "call venv\Scripts\activate && python app.py"

:: Give the server 2 seconds to boot up before opening the tunnel
timeout /t 2 /nobreak >nul

:: 2. Start Ngrok in a second window (using .\ so Windows actually finds it)
start "Ngrok Tunnel" cmd /k ".\ngrok http 5000"

echo Done! Look for the Ngrok window to grab your live link.
pause