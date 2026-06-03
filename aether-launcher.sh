#!/bin/bash  # this is cursed but
echo ":)   :)   :)   :)   :)   :)   :)   :)   :)   :)"
echo         Aether Setup & Launcher
echo ":)   :)   :)   :)   :)   :)   :)   :)   :)   :)"
echo.

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3.9+ required"
    exit 1
fi

if [ ! -d "aether" ]; then
    git clone https://github.com/mh3nj/aether.git
    cd aether
else
    cd aether
    git pull
fi

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt


# create .env if missing
if [ ! -f ".env" ]; then
    echo "OPENAI_API_KEY=your_key_here" > .env
    echo "Please edit .env with your keys"
    nano .env
fi


python main.py