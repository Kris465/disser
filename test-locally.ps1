# Автоматический скрипт локального тестирования
# Запуск полной симуляции на одном компьютере

$ErrorActionPreference = "Stop"

# Функция для проверки командлетов
function Test-Command($cmd) {
    return [bool](Get-Command $cmd -ErrorAction SilentlyContinue)
}

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "ЛОКАЛЬНОЕ ТЕСТИРОВАНИЕ ПРОТОТИПА" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# Проверка Docker
Write-Host "[1/8] Проверка Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Docker вернул ошибку" }
    Write-Host "  Найдено: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  Ошибка: Docker не найден. Установите Docker Desktop." -ForegroundColor Red
    exit 1
}

# Проверка Python
Write-Host ""
Write-Host "[2/8] Проверка Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Python вернул ошибку" }
    Write-Host "  Найдено: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  Ошибка: Python не найден. Установите Python 3.8+." -ForegroundColor Red
    exit 1
}

# Запуск сервера
Write-Host ""
Write-Host "[3/8] Запуск сервера (Registry + API)..." -ForegroundColor Yellow
Push-Location "D:\repos\disser\server"

try {
    $serverRunning = docker-compose ps -q 2>&1
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($serverRunning)) {
        Write-Host "  Запуск docker-compose..." -ForegroundColor Yellow
        docker-compose up -d --build
        if ($LASTEXITCODE -ne 0) { throw "docker-compose up завершился с ошибкой" }
        
        # Ожидание запуска
        Write-Host "  Ожидание запуска сервисов (30 сек)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
    } else {
        Write-Host "  Сервер уже запущен" -ForegroundColor Green
    }
} catch {
    Write-Host "  Ошибка запуска сервера: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# Проверка API
Write-Host ""
Write-Host "[4/8] Проверка API..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "  API доступно: $($response.Content)" -ForegroundColor Green
    } else {
        throw "API вернул статус $($response.StatusCode)"
    }
} catch {
    Write-Host "  Ошибка: API недоступно. Проверьте логи: docker-compose logs api" -ForegroundColor Red
    Write-Host "  Детали: $_" -ForegroundColor Red
    exit 1
}

# Сборка базового образа
Write-Host ""
Write-Host "[5/8] Сборка базового образа..." -ForegroundColor Yellow
Push-Location "D:\repos\disser\images\base-session"

try {
    $baseImageExists = docker images -q base-session:latest 2>&1
    if ([string]::IsNullOrWhiteSpace($baseImageExists)) {
        Write-Host "  Сборка base-session:latest (10-15 мин)..." -ForegroundColor Yellow
        docker build -t base-session:latest .
        if ($LASTEXITCODE -ne 0) { throw "Сборка base-session завершилась с ошибкой" }
        Write-Host "  base-session собран успешно" -ForegroundColor Green
    } else {
        Write-Host "  Образ уже существует" -ForegroundColor Green
    }
} catch {
    Write-Host "  Ошибка сборки base-session: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# Сборка образа дизайнера
Write-Host ""
Write-Host "[6/8] Сборка образа дизайнера..." -ForegroundColor Yellow
Push-Location "D:\repos\disser\images\designer-base"

try {
    $designerImageExists = docker images -q designer-base:latest 2>&1
    if ([string]::IsNullOrWhiteSpace($designerImageExists)) {
        Write-Host "  Сборка designer-base:latest (20-30 мин)..." -ForegroundColor Yellow
        docker build -t designer-base:latest .
        if ($LASTEXITCODE -ne 0) { throw "Сборка designer-base завершилась с ошибкой" }
        Write-Host "  designer-base собран успешно" -ForegroundColor Green
    } else {
        Write-Host "  Образ уже существует" -ForegroundColor Green
    }
} catch {
    Write-Host "  Ошибка сборки designer-base: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# Сборка образа разработчика
Write-Host ""
Write-Host "[7/8] Сборка образа разработчика..." -ForegroundColor Yellow
Push-Location "D:\repos\disser\images\developer-base"

try {
    $developerImageExists = docker images -q developer-base:latest 2>&1
    if ([string]::IsNullOrWhiteSpace($developerImageExists)) {
        Write-Host "  Сборка developer-base:latest (20-30 мин)..." -ForegroundColor Yellow
        docker build -t developer-base:latest .
        if ($LASTEXITCODE -ne 0) { throw "Сборка developer-base завершилась с ошибкой" }
        Write-Host "  developer-base собран успешно" -ForegroundColor Green
    } else {
        Write-Host "  Образ уже существует" -ForegroundColor Green
    }
} catch {
    Write-Host "  Ошибка сборки developer-base: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# Загрузка в Registry
Write-Host ""
Write-Host "[8/8] Загрузка образов в Registry..." -ForegroundColor Yellow

try {
    docker tag designer-base:latest localhost:5000/designer-base:latest
    if ($LASTEXITCODE -ne 0) { throw "Ошибка тегирования designer-base" }
    
    docker tag developer-base:latest localhost:5000/developer-base:latest
    if ($LASTEXITCODE -ne 0) { throw "Ошибка тегирования developer-base" }

    Write-Host "  Загрузка designer-base..." -ForegroundColor Yellow
    docker push localhost:5000/designer-base:latest
    if ($LASTEXITCODE -ne 0) { throw "Ошибка загрузки designer-base в registry" }

    Write-Host "  Загрузка developer-base..." -ForegroundColor Yellow
    docker push localhost:5000/developer-base:latest
    if ($LASTEXITCODE -ne 0) { throw "Ошибка загрузки developer-base в registry" }
    
    Write-Host "  Образы загружены в Registry" -ForegroundColor Green
} catch {
    Write-Host "  Ошибка загрузки в Registry: $_" -ForegroundColor Red
    exit 1
}

# Проверка Registry
Write-Host ""
Write-Host "Проверка Registry..." -ForegroundColor Yellow
try {
    $catalog = Invoke-WebRequest -Uri "http://localhost:5000/v2/_catalog" -TimeoutSec 5 -UseBasicParsing
    Write-Host "  Registry: $($catalog.Content)" -ForegroundColor Green
} catch {
    Write-Host "  Ошибка доступа к Registry: $_" -ForegroundColor Red
}

# Итоги
Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "СБОРКА ЗАВЕРШЕНА" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Список образов:" -ForegroundColor Yellow
docker images | Select-String "base-session|designer-base|developer-base"

Write-Host ""
Write-Host "Для запуска лаунчера выполните:" -ForegroundColor Yellow
Write-Host "  cd D:\repos\disser\station\launcher" -ForegroundColor White
Write-Host "  pip install requests" -ForegroundColor White
Write-Host "  python main.py" -ForegroundColor White
Write-Host ""
Write-Host "Сервер работает на: http://localhost:8000" -ForegroundColor White
Write-Host "Registry на: http://localhost:5000" -ForegroundColor White
Write-Host ""
