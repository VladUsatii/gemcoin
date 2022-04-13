#!/bin/bash

# installs all dependencies
pip install -r requirements.txt;

# dir gets absolute path of main.py
chmod +x dir.py
chmod +x findmaindir.py

chmod +x peers/main.py
start_path="$(./dir.py)"
main_path="$(./findmaindir.py)"

>> ~/gemshortcut.sh

echo "chmod +x ${start_path}; ./${start_path}" > ~/gemshortcut.sh
echo "./${main_path}" > peers/exec_main.sh;

echo "alias gemcoin='(cd ~ ; ./gemshortcut.sh )'" >> ~/.bash_profile;
echo "All done. Type 'gemcoin' into Terminal to start the peer."
