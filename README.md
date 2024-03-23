# stocks

## Install
```
uv venv venv
. ./venv/bin/activate

uv pip install -r requirements.txt
```

## Run

```
export STOCK_FILE=./stock.json 
python3 src/main.py

or
STOCK_FILE=./stock.json python3 src/main.py

or
python3 src/main.py -f stock.json
```
