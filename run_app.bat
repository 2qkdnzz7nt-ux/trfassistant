@echo off
if not exist "venv" (
    echo Creating virtual environment...
    py -m venv venv
    call venv\Scripts\activate
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

echo Starting Streamlit App...
streamlit run app.py
pause
