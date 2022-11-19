#! /bin/bash

sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.8-venv
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
