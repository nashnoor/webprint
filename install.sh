#!/bin/bash 
sudo apt install libcups2-dev
python3 -m venv .
source ./bin/activate 
pip3 install -r requirements.txt
cd service 
sudo cp webprint.service /etc/systemd/system/webprint.service
echo "Your service file will be opened in 5 seconds. Please edit the field marked in the file"
sleep 5
sudo nano /etc/systemd/system/webprint.service
sudo systemctl daemon-reload
sudo systemctl enable webprint.service
sudo systemctl start webprint.service
sleep 3
echo "Done installing WebPrint Service on your system. Please visit :https://github.com/nashnoor/webprint/issues if there is any issues related with the installation. Printing service status..."
sudo systemctl status webprint.service
