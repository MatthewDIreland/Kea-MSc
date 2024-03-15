@echo off
setlocal

cd/d "%1"
python "%~dp0AssignSessions.py" "ImageData.csv" "AlignmentResults.csv" "ImageDataCorrectedDateTimes.csv" "AssignedSessions.csv"
if errorlevel 1 goto error_1
exit/b 0

:error_1 
echo Script terminated. An error occured while assigning sessions
exit/b 1
