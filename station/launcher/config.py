# Конфигурация лаунчера рабочей станции

# URL сервера управления сессиями
SESSION_SERVER = "http://192.168.1.100:8000"

# Локальные образы (резерв, если сервер недоступен)
DESIGNER_IMAGE = "designer-base:latest"
DEVELOPER_IMAGE = "developer-base:latest"

# Порт noVNC
NOVNC_PORT = 6080

# Порт VNC
VNC_PORT = 5900

# Браузер для noVNC (kiosk режим)
BROWSER_KIOSK = True
BROWSER_NAME = "chrome"  # или "firefox"
