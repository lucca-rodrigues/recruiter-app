### Commands
```sh
## Create virtual environment
python3 -m venv venv

## Activate virtual environment
source venv/bin/activate

## Install dependencies
pip install -r requirements.txt

## Run the server
python server.py
## or
uvicorn server:app --host 0.0.0.0 --port 5001 --reload
```