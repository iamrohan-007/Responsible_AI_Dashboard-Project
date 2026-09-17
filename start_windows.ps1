$ErrorActionPreference = "Stop"
if (!(Test-Path ".venv")) { py -m venv .venv }
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
Write-Host ""
Write-Host "Starting Responsible AI Dashboard..."
Write-Host "Open http://127.0.0.1:5000"
& ".\.venv\Scripts\python.exe" run.py
