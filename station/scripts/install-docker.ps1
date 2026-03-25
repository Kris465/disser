# Скрипт установки Docker Desktop на рабочую станцию
# Требуется: Windows 10/11 Pro, права администратора

Write-Host "=== Установка Docker Desktop ===" -ForegroundColor Cyan

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)

if (-not $isAdmin) {
    Write-Host "Ошибка: Требуется запуск от имени администратора" -ForegroundColor Red
    exit 1
}

# Проверка версии Windows
$version = [Environment]::OSVersion.Version
if ($version.Major -lt 10) {
    Write-Host "Ошибка: Требуется Windows 10 или выше" -ForegroundColor Red
    exit 1
}

Write-Host "Версия Windows: $version" -ForegroundColor Green

# Включение функции контейнеров Windows (если требуется)
Write-Host "Включение функции контейнеров..." -ForegroundColor Yellow
Enable-WindowsOptionalFeature -Online -FeatureName Containers -All -NoRestart

# Включение Hyper-V (требуется для Docker Desktop)
Write-Host "Включение Hyper-V..." -ForegroundColor Yellow
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All -NoRestart

# Скачивание Docker Desktop
$dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
$dockerInstaller = "$env:TEMP\DockerInstaller.exe"

Write-Host "Загрузка Docker Desktop..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $dockerUrl -OutFile $dockerInstaller

# Установка Docker Desktop (тихий режим)
Write-Host "Установка Docker Desktop..." -ForegroundColor Yellow
Start-Process -FilePath $dockerInstaller -ArgumentList "install", "--quiet" -Wait

# Проверка установки
$dockerPath = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"
if (Test-Path $dockerPath) {
    Write-Host "Docker Desktop успешно установлен" -ForegroundColor Green
    
    # Добавление в PATH
    $env:Path += ";C:\Program Files\Docker\Docker\resources\bin"
    [Environment]::SetEnvironmentVariable(
        "Path",
        $env:Path,
        [System.EnvironmentVariableTarget]::Machine
    )
    
    Write-Host "Docker добавлен в PATH" -ForegroundColor Green
} else {
    Write-Host "Ошибка: Docker не найден после установки" -ForegroundColor Red
    exit 1
}

# Перезапуск проводника для применения PATH
Write-Host "Перезапуск проводника..." -ForegroundColor Yellow
Stop-Process -Name explorer -Force

Write-Host "=== Установка завершена ===" -ForegroundColor Green
Write-Host "Требуется перезагрузка компьютера" -ForegroundColor Yellow
Write-Host "После перезагрузки запустите Docker Desktop для инициализации" -ForegroundColor Yellow
