# Инструкция по развёртыванию системы изолированных сессий

**Версия:** 1.0.0  
**Дата:** Март 2026  
**Для кого:** Системные администраторы ООО «Академия ТОП»

---

## Содержание

1. [Требования к инфраструктуре](#1-требования-к-инфраструктуре)
2. [Развёртывание сервера управления](#2-развёртывание-сервера-управления)
3. [Настройка рабочих станций](#3-настройка-рабочих-станций)
4. [Создание образов](#4-создание-образов)
5. [Проверка работоспособности](#5-проверка-работоспособности)
6. [Устранение неисправностей](#6-устранение-неисправностей)

---

## 1. Требования к инфраструктуре

### 1.1. Сервер управления

| Компонент | Минимум | Рекомендуется |
|-----------|---------|---------------|
| ОС | Windows 10/11 или Linux | Linux (Ubuntu 22.04) |
| CPU | 4 ядра | 8 ядер |
| RAM | 8 ГБ | 16 ГБ |
| Disk | 50 ГБ SSD | 200 ГБ SSD |
| Сеть | 1 Gbps | 1 Gbps |
| Docker | Docker Engine 20+ | Docker Engine 24+ |

**Статический IP:** Назначьте серверу статический IP в локальной сети филиала (например, `192.168.1.100`).

### 1.2. Рабочая станция

| Компонент | Требование |
|-----------|------------|
| ОС | Windows 10/11 (64-bit) |
| CPU | 4 ядра |
| RAM | 8+ ГБ (рекомендуется 16 ГБ) |
| Disk | 50 ГБ свободно |
| Сеть | Доступ к серверу по локальной сети |
| Python | 3.8+ |
| Docker | Docker Desktop |

---

## 2. Развёртывание сервера управления

### Шаг 2.1. Установка Docker (Linux)

```bash
# Установка Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Проверка
docker --version
```

### Шаг 2.2. Клонирование репозитория

```bash
# На сервере
cd /opt
git clone <url-репозитория> session-system
cd session-system
```

### Шаг 2.3. Настройка сервера

При развёртывании на сервере с другим IP отредактируйте `server/docker-compose.yml`:

```yaml
environment:
  - REGISTRY_URL=http://192.168.1.100:5000  # IP вашего сервера
  - REGISTRY_INTERNAL=http://registry:5000
  - DESIGNER_IMAGE=designer-base:latest
  - DEVELOPER_IMAGE=developer-base:latest
```

> **Примечание:** По умолчанию `REGISTRY_URL=http://localhost:5000` — для локального тестирования. Для продакшена замените на IP сервера.

### Шаг 2.4. Запуск сервера

```bash
cd /opt/session-system/server

# Сборка и запуск
docker-compose up -d --build

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f api
```

Сервер должен быть доступен:
- API: `http://192.168.1.100:8000`
- Registry: `http://192.168.1.100:5000`

### Шаг 2.5. Проверка API

```bash
# Проверка health endpoint
curl http://192.168.1.100:8000/health

# Ожидаемый ответ:
# {"status":"ok","registry_url":"http://192.168.1.100:5000","images":{"designer":"designer-base:latest","developer":"developer-base:latest"}}
```

---

## 3. Настройка рабочих станций

### Шаг 3.1. Установка Docker Desktop

**Вариант A: Автоматическая установка (рекомендуется)**

Запустите от имени администратора:

```powershell
# Перейти в папку скриптов
cd D:\repos\disser\station\scripts

# Запустить установку
.\install-docker.ps1
```

После установки **перезагрузите компьютер**.

**Вариант B: Ручная установка**

1. Скачайте Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Запустите установщик
3. Следуйте инструкциям мастера
4. Перезагрузите компьютер

### Шаг 3.2. Установка Python

1. Скачайте Python 3.8+: https://www.python.org/downloads/
2. При установке отметьте **"Add Python to PATH"**
3. Установите

### Шаг 3.3. Настройка автозапуска лаунчера

Запустите от имени администратора:

```powershell
# Перейти в папку скриптов
cd D:\repos\disser\station\scripts

# Запустить настройку
.\setup-autostart.ps1
```

Скрипт:
- Установит зависимости (`requests`)
- Создаст ярлык в автозагрузке
- Создаст задачу в планировщике
- Настроит cleanup при выключении

### Шаг 3.4. Настройка сервера для станции

Откройте файл `station\launcher\config.py` и укажите IP сервера:

```python
SESSION_SERVER = "http://192.168.1.100:8000"  # IP вашего сервера
```

---

## 4. Создание образов

### Шаг 4.1. Сборка базового образа

```bash
# На сервере
cd /opt/session-system/images/base-session

docker build -t base-session:latest .
```

### Шаг 4.2. Сборка образа дизайнера

```bash
cd /opt/session-system/images/designer-base

docker build -t designer-base:latest .
```

### Шаг 4.3. Сборка образа разработчика

```bash
cd /opt/session-system/images/developer-base

docker build -t developer-base:latest .
```

### Шаг 4.4. Загрузка образов в Registry

**На сервере (продакшен):**

```bash
# Тегирование образов с IP сервера
docker tag designer-base:latest 192.168.1.100:5000/designer-base:latest
docker tag developer-base:latest 192.168.1.100:5000/developer-base:latest

# Загрузка
docker push 192.168.1.100:5000/designer-base:latest
docker push 192.168.1.100:5000/developer-base:latest
```

**Локальное тестирование (один компьютер):**

```bash
# Тегирование с localhost
docker tag designer-base:latest localhost:5000/designer-base:latest
docker tag developer-base:latest localhost:5000/developer-base:latest

# Загрузка
docker push localhost:5000/designer-base:latest
docker push localhost:5000/developer-base:latest
```

### Шаг 4.5. Проверка Registry

```bash
# Список образов в registry
curl http://192.168.1.100:5000/v2/_catalog

# Ожидаемый ответ:
# {"repositories":["designer-base","developer-base"]}
```

---

## 5. Проверка работоспособности

### Шаг 5.1. Проверка сервера

```bash
# Проверка API
curl http://192.168.1.100:8000/health
curl http://192.168.1.100:8000/image/designer
curl http://192.168.1.100:8000/image/developer
```

### Шаг 5.2. Проверка рабочей станции

1. **Перезагрузите рабочую станцию**
2. Лаунчер должен запуститься автоматически
3. Выберите тип сессии (Дизайнер/Разработчик)
4. Должен открыться браузер с noVNC

### Шаг 5.3. Проверка контейнера

```powershell
# Проверка запущенных контейнеров
docker ps

# Просмотр логов
docker logs session_designer_<id>

# Остановка сессии
docker stop session_<type>_<id>
```

---

## 6. Устранение неисправностей

### 6.1. Лаунчер не запускается

**Проблема:** Лаунчер не появляется после загрузки

**Решение:**
```powershell
# Проверка автозагрузки
shell:startup

# Проверка наличия ярлыка SessionLauncher.lnk

# Запуск вручную
python D:\repos\disser\station\launcher\main.py
```

### 6.2. Ошибка "Сервер недоступен"

**Проблема:** Лаунчер показывает "Сервер недоступен"

**Решение:**
1. Проверьте подключение к сети
2. Проверьте доступность сервера:
   ```powershell
   ping 192.168.1.100
   curl http://192.168.1.100:8000/health
   ```
3. Убедитесь, что firewall не блокирует порт 8000

### 6.3. Контейнер не запускается

**Проблема:** Ошибка при запуске контейнера

**Решение:**
```powershell
# Проверка Docker
docker --version

# Проверка доступности Docker Desktop
docker ps

# Если Docker не отвечает - перезапустите Docker Desktop

# Проверка наличия образа
docker images | findstr designer-base
docker images | findstr developer-base

# Если образа нет - загрузите вручную
docker pull 192.168.1.100:5000/designer-base:latest
```

### 6.4. noVNC не открывается

**Проблема:** Браузер не открывает noVNC

**Решение:**
1. Проверьте, что порт 6080 не занят:
   ```powershell
   netstat -ano | findstr :6080
   ```
2. Попробуйте открыть вручную: `http://localhost:6080/vnc.html`
3. Проверьте логи контейнера:
   ```powershell
   docker logs session_<type>_<id>
   ```

### 6.5. Медленная загрузка образа

**Проблема:** Долгая загрузка при первом запуске

**Решение:**
- Нормальное время загрузки: 2-5 минут на образ (3-4 ГБ)
- Убедитесь, что сеть 1 Gbps
- Последующие запуски используют кэш (быстро)

---

## Приложения

### A. Команды Docker для администрирования

**Linux / macOS:**

```bash
# Список всех контейнеров сессий
docker ps -a --filter name=session_

# Остановка всех сессий
docker stop $(docker ps -q --filter name=session_)

# Удаление всех сессий
docker rm $(docker ps -aq --filter name=session_)

# Просмотр логов
docker logs session_designer_<id>

# Мониторинг ресурсов
docker stats
```

**Windows (PowerShell):**

```powershell
# Список всех контейнеров сессий
docker ps -a --filter name=session_

# Остановка всех сессий
docker stop $(docker ps -q --filter name=session_)

# Удаление всех сессий
docker rm -f $(docker ps -aq --filter name=session_)

# Просмотр логов
docker logs session_designer_<id>

# Мониторинг ресурсов
docker stats
```

### B. Контакты поддержки

По вопросам развёртывания обращайтесь к разработчикам системы.

---

**Конец инструкции**
