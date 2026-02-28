@echo off
start cmd /k "venv\Scripts\activate && python app.py"
start cmd /k ".\cloudflared.exe tunnel --url http://127.0.0.1:5000"