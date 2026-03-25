#!/bin/bash
# Скрипт запуска VNC + noVNC

# Запуск VNC сервера
vncserver :1 -geometry 1920x1080 -depth 24 &
sleep 2

# Запуск noVNC через websockify
websockify --web=/usr/share/novnc 6080 localhost:5900 &

# Держим контейнер запущенным
tail -f /dev/null
