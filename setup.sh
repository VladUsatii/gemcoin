#!/bin/bash

# installs all dependencies
pip install -r requirements.txt;

# remember to execute setup.sh if you change location of gemcoin
chosen_path="$PWD";
echo "alias gemcoin=\'python3 $chosen_path/peers/main.py\'" >> ~/.bash_profile;
