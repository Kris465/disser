# Скрипт настройки автозапуска лаунчера
# Требуется: права администратора

Write-Host "=== Настройка автозапуска лаунчера ===" -ForegroundColor Cyan

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)

if (-not $isAdmin) {
    Write-Host "Ошибка: Требуется запуск от имени администратора" -ForegroundColor Red
    exit 1
}

# Путь к лаунчеру
$launcherPath = "D:\repos\disser\station\launcher"
$pythonScript = Join-Path $launcherPath "main.py"
$pythonExe = "python"

# Проверка наличия Python
Write-Host "Проверка Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ошибка: Python не найден. Установите Python 3.8+" -ForegroundColor Red
    exit 1
}
Write-Host "Найдено: $pythonVersion" -ForegroundColor Green

# Установка зависимостей
Write-Host "Установка зависимостей (tkinter, requests)..." -ForegroundColor Yellow
pip install requests

# Создание ярлыка в автозагрузке
$startupPath = [Environment]::GetFolderPath("Startup")
$shortcutPath = Join-Path $startupPath "SessionLauncher.lnk"

Write-Host "Создание ярлыка в автозагрузке..." -ForegroundColor Yellow

$WScript = New-Object -ComObject WScript.Shell
$shortcut = $WScript.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $pythonExe
$shortcut.Arguments = $pythonScript
$shortcut.WorkingDirectory = $launcherPath
$shortcut.WindowStyle = 1  # Нормальное окно
$shortcut.Description = "Academy TOP Session Launcher"
$shortcut.Save()

Write-Host "Ярлык создан: $shortcutPath" -ForegroundColor Green

# Настройка задачи в планировщике (альтернатива автозагрузке)
Write-Host "Создание задачи в планировщике..." -ForegroundColor Yellow

$taskName = "SessionLauncher"
$taskAction = New-ScheduledTaskAction -Execute $pythonExe -Argument $pythonScript -WorkingDirectory $launcherPath
$taskTrigger = New-ScheduledTaskTrigger -AtLogOn
$taskPrincipal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $taskName -Action $taskAction -Trigger $taskTrigger -Principal $taskPrincipal -Settings $taskSettings -Force

Write-Host "Задача создана: $taskName" -ForegroundColor Green

# Скрипт cleanup при выключении
Write-Host "Настройка cleanup при выключении..." -ForegroundColor Yellow

$cleanupScript = Join-Path $PSScriptRoot "cleanup.ps1"
$shutdownTaskName = "SessionCleanup"
$shutdownAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$cleanupScript`""
$shutdownTrigger = New-ScheduledTaskTrigger -AtStartup
$shutdownPrincipal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType Service -RunLevel Highest

Register-ScheduledTask -TaskName $shutdownTaskName -Action $shutdownAction -Trigger $shutdownTrigger -Principal $shutdownPrincipal -Force

Write-Host "Задача cleanup создана: $shutdownTaskName" -ForegroundColor Green

Write-Host "=== Настройка завершена ===" -ForegroundColor Green
Write-Host "Лаунчер запустится при следующей загрузке" -ForegroundColor Yellow
