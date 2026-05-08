# Локальное тестирование прототипа

Запуск полной симуляции на одном компьютере (Windows 10/11).

---

## Требования

- Docker Desktop установлен и запущен
- Python 3.8+ установлен
- Свободно ~10 ГБ на диске (для образов)
- Время: ~30-60 минут (первая сборка)

---

## Шаг 1. Сборка сервера

```bash
cd D:\repos\disser\server

# Сборка и запуск сервера (Registry + API)
docker-compose up -d --build

# Проверка
docker-compose ps

# Должно быть:
# - session-registry (порт 5000)
# - session-api (порт 8000)
# - При запуске сессии лаунчер пробрасывает порты 5900 (VNC) и 6080 (noVNC)
```

Проверка API в браузере или через curl:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/image/designer
curl http://localhost:8000/image/developer
```

---

## Шаг 2. Сборка образов

### 2.1. Базовый образ (XFCE + noVNC)

```bash
cd D:\repos\disser\images\base-session

docker build -t base-session:latest .
```

**Время сборки:** ~5-10 минут  
**Размер:** ~1 ГБ

### 2.2. Образ дизайнера

```bash
cd D:\repos\disser\images\designer-base

docker build -t designer-base:latest .
```

**Время сборки:** ~15-20 минут  
**Размер:** ~3.5 ГБ

### 2.3. Образ разработчика

```bash
cd D:\repos\disser\images\developer-base

docker build -t developer-base:latest .
```

**Время сборки:** ~20-30 минут  
**Размер:** ~3 ГБ

---

## Шаг 3. Загрузка образов в локальный Registry

```bash
# Тегирование для локального registry
docker tag designer-base:latest localhost:5000/designer-base:latest
docker tag developer-base:latest localhost:5000/developer-base:latest

# Загрузка
docker push localhost:5000/designer-base:latest
docker push localhost:5000/developer-base:latest
```

Проверка:
```bash
curl http://localhost:5000/v2/_catalog
# Ожидаемый ответ: {"repositories":["designer-base","developer-base"]}
```

---

## Шаг 4. Запуск лаунчера

### 4.1. Установка зависимостей

```bash
cd D:\repos\disser\station\launcher

pip install requests
```

### 4.2. Настройка конфигурации

Откройте `config.py` и убедитесь, что сервер указан правильно:

```python
SESSION_SERVER = "http://localhost:8000"
```

### 4.3. Запуск лаунчера

```bash
python main.py
```

Должно открыться окно с выбором сессии.

---

## Шаг 5. Тестирование сессии

### 5.1. Запуск сессии

1. В окне лаунчера выберите тип сессии (Дизайнер или Разработчик)
2. Лаунчер загрузит образ (если нет локально)
3. Запустится контейнер
4. Лаунчер подождёт готовности noVNC (до 15 секунд)
5. Откроется браузер с noVNC в режиме киоска

### 5.2. Проверка работы

В noVNC вы должны увидеть:
- Рабочий стол XFCE
- Панель приложений
- Возможность открывать программы

**Для дизайнера:**
- Откройте Krita: `Applications → Graphics → Krita`
- Откройте GIMP: `Applications → Graphics → GIMP`
- Откройте Firefox: `Applications → Internet → Firefox`

**Для разработчика:**
- Откройте VS Code: `Applications → Programming → VS Code`
- Откройте Terminal: `Applications → System Tools → Terminal`
- Проверьте PHP: `php --version`
- Проверьте Python: `python3 --version`

### 5.3. Проверка изоляции

Попробуйте в терминале контейнера:

```bash
# Попытка записи в защищённую директорию
echo test > /etc/test
# Ошибка: Read-only file system

# Попытка запуска docker (побега)
docker ps
# Ошибка: docker command not found

# Проверка пользователя
whoami
# Должно быть: session (не root)
```

### 5.4. Завершение сессии

Закройте браузер noVNC и проверьте:

**Linux / macOS:**
```bash
docker ps -a --filter name=session_
```

**Windows (PowerShell):**
```powershell
docker ps -a --filter name=session_
```

Контейнер должен быть удалён автоматически (`--rm`).

---

## Шаг 6. Тесты

### 6.1. Тест нагрузки

```bash
cd D:\repos\disser\tests

pip install aiohttp

python load_test.py
```

Ожидаемые результаты:
- 100 одновременных запросов
- Среднее время < 100 мс
- Пропускная способность > 1000 RPS

### 6.2. Тест безопасности

```bash
cd D:\repos\disser\tests

python security_test.py
```

Проверяет:
- Побег из контейнера
- Повышение привилегий
- Персистентность данных

---

## Устранение проблем

### Проблема: Docker не отвечает

**Решение:**
```bash
# Перезапустите Docker Desktop
# В трее: Docker Desktop → Quit Docker
# Запустите снова
```

### Проблема: Ошибка сборки образов

**Решение:**
```bash
# Очистка кэша Docker
docker system prune -a

# Повторная сборка
docker build --no-cache -t base-session:latest .
```

### Проблема: Лаунчер не подключается к серверу

**Решение:**
```bash
# Проверка сервера
curl http://localhost:8000/health

# Проверка доступности
netstat -ano | findstr :8000
```

### Проблема: noVNC не открывается

**Решение:**
1. Проверьте, что Chrome установлен
2. Откройте вручную: `http://localhost:6080/vnc.html`
3. Проверьте логи контейнера:
   ```bash
   docker ps -a | findstr session_
   docker logs <container_id>
   ```

### Проблема: Медленная сборка

**Решение:**
- Нормальное время: 30-60 минут (первый запуск)
- Убедитесь, что Docker выделено достаточно RAM (4+ ГБ)
- Проверьте скорость интернета (загрузка пакетов)

---

## Очистка после тестирования

> ⚠️ **Внимание:** Команды ниже удалят все образы и данные. Выполняйте только если хотите полностью очистить систему.

```bash
# Остановка сервера
cd D:\repos\disser\server
docker-compose down

# Удаление образов
docker rmi base-session:latest designer-base:latest developer-base:latest

# Очистка registry (имя зависит от настроек docker-compose)
docker volume rm server_registry-data

# Полная очистка (удаляет ВСЕ неиспользуемые образы и контейнеры)
docker system prune -a
```

---

## Ожидаемые результаты

✅ Сервер работает (порт 8000, 5000)  
✅ Образы собраны и загружены в registry  
✅ Лаунчер открывается с выбором сессии  
✅ noVNC показывает рабочий стол XFCE  
✅ Приложения запускаются  
✅ Контейнер удаляется после закрытия  
✅ Тесты проходят без ошибок

---

**Время полного тестирования:** 1-2 часа (включая сборку образов)
