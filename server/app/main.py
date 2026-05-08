from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib
import os

app = FastAPI(title="Session Orchestrator API")

# CORS для доступа с рабочих станций
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Конфигурация
# REGISTRY_URL — адрес, доступный с хоста (для docker pull)
# Внутри docker-compose контейнеры обращаются друг к другу по имени сервиса,
# но лаунчер на хосте должен использовать localhost
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://localhost:5000")
# Внутренний адрес registry для межконтейнерного общения
REGISTRY_INTERNAL = os.getenv("REGISTRY_INTERNAL", "http://registry:5000")
DESIGNER_IMAGE = os.getenv("DESIGNER_IMAGE", "designer-base:latest")
DEVELOPER_IMAGE = os.getenv("DEVELOPER_IMAGE", "developer-base:latest")


class ImageMetadata(BaseModel):
    image_name: str
    version: str
    hash: str
    registry_url: str
    size_bytes: int
    full_name: str


class HealthStatus(BaseModel):
    status: str
    registry_url: str
    images: dict


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Проверка доступности сервера"""
    return HealthStatus(
        status="ok",
        registry_url=REGISTRY_URL,
        images={
            "designer": DESIGNER_IMAGE,
            "developer": DEVELOPER_IMAGE
        }
    )


@app.get("/image/{image_type}", response_model=ImageMetadata)
async def get_image_metadata(image_type: str):
    """
    Получение metadata образа по типу

    image_type: 'designer' или 'developer'
    """
    if image_type == "designer":
        image_name = DESIGNER_IMAGE
        size_bytes = 3_500_000_000  # ~3.5 ГБ
    elif image_type == "developer":
        image_name = DEVELOPER_IMAGE
        size_bytes = 3_000_000_000  # ~3 ГБ
    else:
        raise HTTPException(status_code=404, detail="Unknown image type")

    # Генерируем hash из имени образа (в реальности - hash реального образа)
    image_hash = hashlib.sha256(image_name.encode()).hexdigest()

    # Версия из имени образа (например, designer-base:latest → latest)
    version = image_name.split(":")[-1] if ":" in image_name else "latest"

    return ImageMetadata(
        image_name=image_name.split(":")[0],
        version=version,
        hash=image_hash,
        registry_url=REGISTRY_URL,
        size_bytes=size_bytes,
        full_name=f"localhost:5000/{image_name}"
    )


@app.get("/")
async def root():
    """Информация об API"""
    return {
        "service": "Session Orchestrator API",
        "version": "1.0.0",
        "endpoints": [
            "GET /health",
            "GET /image/{type}"
        ]
    }
