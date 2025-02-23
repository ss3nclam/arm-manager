#!/bin/bash

SOURCE_DIR="$(dirname "$(realpath "$0")")"
TARGET_DIR="/opt/arm-manager"
SERVICE_NAME="arm-cleaner.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"
ARMON_SCRIPT="/usr/local/bin/armon"

if [ -d "$TARGET_DIR" ]; then
  echo "Папка $TARGET_DIR уже существует. Удаляю и перезаписываю..."
  sudo rm -rf "$TARGET_DIR"
fi

echo "Копирую содержимое из $SOURCE_DIR в $TARGET_DIR..."
sudo mkdir -p "$TARGET_DIR"
sudo cp -r "$SOURCE_DIR"/* "$TARGET_DIR/"

CLEANER_SCRIPT="$TARGET_DIR/cleaner.py"
MONITOR_SCRIPT="$TARGET_DIR/monitor.py"

if [ -f "$CLEANER_SCRIPT" ]; then
  sudo chmod +x "$CLEANER_SCRIPT"
  echo "Скрипт $CLEANER_SCRIPT сделан исполняемым."
else
  echo "Ошибка: Скрипт $CLEANER_SCRIPT не найден!"
  exit 1
fi

if [ -f "$MONITOR_SCRIPT" ]; then
  sudo chmod +x "$MONITOR_SCRIPT"
  echo "Скрипт $MONITOR_SCRIPT сделан исполняемым."
else
  echo "Ошибка: Скрипт $MONITOR_SCRIPT не найден!"
  exit 1
fi

echo "Создание файла службы $SERVICE_FILE..."
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=ARM Cleaner Service
After=mplc4.service

[Service]
ExecStart=/usr/bin/python3 $TARGET_DIR/cleaner.py
WorkingDirectory=$TARGET_DIR
Restart=always
User=root
Group=root
Environment="PYTHONUNBUFFERED=1"

StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=arm-cleaner

[Install]
WantedBy=multi-user.target
EOF

if [ -f "$SERVICE_FILE" ]; then
  echo "Файл службы $SERVICE_FILE успешно создан."
else
  echo "Ошибка: Не удалось создать файл службы!"
  exit 1
fi

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

echo "Проверка статуса службы $SERVICE_NAME..."
sudo systemctl status "$SERVICE_NAME"

echo "Создание скрипта $ARMON_SCRIPT..."
sudo bash -c "cat > $ARMON_SCRIPT" <<EOF
#!/bin/bash
$TARGET_DIR/monitor.py "\$@"
EOF

sudo chmod +x "$ARMON_SCRIPT"

if [ -f "$ARMON_SCRIPT" ]; then
  echo "Скрипт $ARMON_SCRIPT успешно создан."
else
  echo "Ошибка: Не удалось создать скрипт $ARMON_SCRIPT!"
  exit 1
fi

echo "Готово!"
