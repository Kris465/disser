# Скрипт очистки сессий при выключении/загрузке
# Останавливает все активные контейнеры сессий

Write-Host "=== Очистка сессий ===" -ForegroundColor Cyan

# Проверка доступности Docker
$dockerAvailable = Get-Command docker -ErrorAction SilentlyContinue

if (-not $dockerAvailable) {
    Write-Host "Docker не найден, пропуск очистки" -ForegroundColor Yellow
    exit 0
}

# Поиск контейнеров сессий
Write-Host "Поиск контейнеров сессий..." -ForegroundColor Yellow

$sessionContainers = docker ps -a --filter "name=session_*" --format "{{.ID}}"

if ([string]::IsNullOrWhiteSpace($sessionContainers)) {
    Write-Host "Активных сессий не найдено" -ForegroundColor Green
    exit 0
}

# Остановка и удаление контейнеров
foreach ($containerId in $sessionContainers) {
    Write-Host "Остановка контейнера: $containerId" -ForegroundColor Yellow
    
    # Graceful stop (10 секунд)
    docker stop $containerId --time 10
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Принудительная остановка: $containerId" -ForegroundColor Red
        docker kill $containerId
    }
    
    # Удаление (если не удалён автоматически через --rm)
    docker rm $containerId -Force
}

Write-Host "Очистка завершена" -ForegroundColor Green
