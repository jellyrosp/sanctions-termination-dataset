#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m ipykernel install --user --name=sanctions-venv --display-name "sanctions-venv"

echo -e "\nSetup complete."