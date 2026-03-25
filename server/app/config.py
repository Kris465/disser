# Конфигурация сервера управления сессиями

# Docker Registry
REGISTRY_URL = "http://localhost:5000"
REGISTRY_HOST = "0.0.0.0"
REGISTRY_PORT = 5000

# FastAPI
API_HOST = "0.0.0.0"
API_PORT = 8000

# Образы
DESIGNER_IMAGE = "designer-base:latest"
DEVELOPER_IMAGE = "developer-base:latest"

# Логирование
LOG_LEVEL = "info"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
