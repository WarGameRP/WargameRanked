@echo off
cd /d "%~dp0.."
python scripts\python\replace_imgur_links.py
pause
