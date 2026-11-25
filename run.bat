@echo off
cd /d "%~dp0"
echo Starting BIGPDF 11zon Localhost Server on http://127.0.0.1:8000 ...
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
