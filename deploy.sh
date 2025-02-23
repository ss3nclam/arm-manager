echo $'\n# For mplc4-cleaner\nroot ALL=(ALL) ALL\nuser ALL=(ALL) NOPASSWD: /bin/systemctl daemon-reload\nuser ALL=(ALL) NOPASSWD: /bin/systemctl * mplc4\nuser ALL=(ALL) NOPASSWD: /bin/systemctl * mplc4-cleaner\n' | sudo tee -a /etc/sudoers
sudo chmod +x /opt/mplc4-cleaner/cleaner.py
echo $'[Unit]\nDescription=mplc4-cleaner\n\n[Service]\nExecStart=/opt/mplc4-cleaner/cleaner.py\n\n[Install]\nWantedBy=multi-user.target\n' | sudo tee -a /lib/systemd/system/mplc4-cleaner.service

sudo systemctl daemon-reload
sudo systemctl enable mplc4-cleaner.service
sudo systemctl start mplc4-cleaner.service
