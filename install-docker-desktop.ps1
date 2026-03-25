# Автоматическая установка Docker Desktop на Windows
# Требуется: права администратора

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "УСТАНОВКА DOCKER DESKTOP" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)

if (-not $isAdmin) {
    Write-Host "Требуется запуск от имени администратора" -ForegroundColor Yellow
    Write-Host "Щёлкните правой кнопкой на скрипте → Run with PowerShell (Admin)" -ForegroundColor Yellow
    exit 1
}

# Проверка версии Windows
Write-Host "[1/6] Проверка версии Windows..." -ForegroundColor Yellow
$osVersion = Get-CimInstance Win32_OperatingSystem
Write-Host "ОС: $($osVersion.Caption)" -ForegroundColor White
Write-Host "Издание: $($osVersion.BuildNumber)" -ForegroundColor White

# Проверка Windows Home
if ($osVersion.Caption -like "*Home*") {
    Write-Host "ОШИБКА: Windows Home не поддерживает Docker Desktop" -ForegroundColor Red
    Write-Host "Варианты:" -ForegroundColor Yellow
    Write-Host "  1. Обновиться до Windows Pro" -ForegroundColor Yellow
    Write-Host "  2. Использовать Docker Toolbox (устаревший)" -ForegroundColor Yellow
    Write-Host "  3. Использовать WSL 2 + Docker Engine внутри Linux" -ForegroundColor Yellow
    exit 1
}

# Проверка виртуализации
Write-Host ""
Write-Host "[2/6] Проверка виртуализации..." -ForegroundColor Yellow
$virtualization = (Get-CimInstance Win32_Processor).VirtualizationFirmwareEnabled
if ($virtualization -contains $true) {
    Write-Host "Виртуализация: Включена" -ForegroundColor Green
} else {
    Write-Host "ОШИБКА: Виртуализация отключена в BIOS/UEFI" -ForegroundColor Red
    Write-Host "Включите Intel VT-x или AMD-V в BIOS" -ForegroundColor Yellow
    exit 1
}

# Проверка WSL 2
Write-Host ""
Write-Host "[3/6] Проверка WSL 2..." -ForegroundColor Yellow
$wslVersion = wsl --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "WSL установлен: $wslVersion" -ForegroundColor Green
} else {
    Write-Host "WSL не найден. Установка..." -ForegroundColor Yellow
    
    # Включение WSL
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart
    
    # Включение Hyper-V
    Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart
    
    Write-Host "Требуется перезагрузка для включения WSL" -ForegroundColor Yellow
    $restart = Read-Host "Перезагрузить сейчас? (y/n)"
    if ($restart -eq "y") {
        Restart-Computer -Force
    }
    exit 0
}

# Скачивание Docker Desktop
Write-Host ""
Write-Host "[4/6] Загрузка Docker Desktop..." -ForegroundColor Yellow
$dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
$dockerInstaller = "$env:TEMP\DockerDesktopInstaller.exe"

try {
    Invoke-WebRequest -Uri $dockerUrl -OutFile $dockerInstaller
    Write-Host "Загружено: $dockerInstaller" -ForegroundColor Green
} catch {
    Write-Host "Ошибка загрузки: $_" -ForegroundColor Red
    exit 1
}

# Установка Docker Desktop
Write-Host ""
Write-Host "[5/6] Установка Docker Desktop..." -ForegroundColor Yellow
Write-Host "Это займёт 5-10 минут..." -ForegroundColor Yellow

$installProcess = Start-Process -FilePath $dockerInstaller `
    -ArgumentList "install", "--quiet", "--accept-license" `
    -Wait `
    -PassThru

if ($installProcess.ExitCode -eq 0) {
    Write-Host "Установка завершена успешно" -ForegroundColor Green
} else {
    Write-Host "Ошибка установки (код: $($installProcess.ExitCode))" -ForegroundColor Red
}

# Проверка установки
Write-Host ""
Write-Host "[6/6] Проверка установки..." -ForegroundColor Yellow
$dockerPath = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"

if (Test-Path $dockerPath) {
    $env:Path += ";C:\Program Files\Docker\Docker\resources\bin"
    [Environment]::SetEnvironmentVariable(
        "Path",
        $env:Path,
        [System.EnvironmentVariableTarget]::Machine
    )
    
    $dockerVersion = & $dockerPath --version
    Write-Host "Docker установлен: $dockerVersion" -ForegroundColor Green
} else {
    Write-Host "Docker не найден после установки" -ForegroundColor Red
}

# Итоги
Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "УСТАНОВКА ЗАВЕРШЕНА" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Следующие шаги:" -ForegroundColor Yellow
Write-Host "1. Запустите Docker Desktop из меню Пуск" -ForegroundColor White
Write-Host "2. Дождитесь зелёного индикатора" -ForegroundColor White
Write-Host "3. Проверьте: docker --version" -ForegroundColor White
Write-Host ""
Write-Host "Для продолжения установки прототипа выполните:" -ForegroundColor White
Write-Host "  cd D:\repos\disser" -ForegroundColor White
Write-Host "  .\test-locally.ps1" -ForegroundColor White
Write-Host ""
