#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo "Starting BIGPDF 11zon Localhost Server on http://127.0.0.1:8000 ..."
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
