@echo off
echo Starting Smart Tourist Safety & Incident Response System...
echo.

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting the server...
echo The API will be available at: http://localhost:8000
echo Swagger documentation: http://localhost:8000/docs
echo.

python main.py