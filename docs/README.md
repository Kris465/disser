# Система изолированных сессий рабочих станций

**Прототип модели Zero Trust для образовательных организаций**  
**ООО «Академия ТОП»**

---

## Описание

Система обеспечивает изолированные эфемерные рабочие сессии для компьютерных классов. Пользователь получает чистую среду при каждом входе — все изменения уничтожаются при выходе.

**Назначение:** Защита от внутренних угроз (НСВД) в образовательных организациях с массовым доступом к рабочим станциям.

---

## Документация

| Документ | Описание |
|----------|----------|
| [architecture.md](architecture.md) | Архитектура и технические решения |
| [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) | План интеграции в инфраструктуру |
| [admin-guide.md](admin-guide.md) | Инструкция сисадмина |
| [local-testing.md](local-testing.md) | Локальное тестирование |
| [CHANGELOG.md](CHANGELOG.md) | Журнал изменений |

---

## Быстрый старт

### 1. Развёртывание сервера

```bash
cd server
docker-compose up -d --build
curl http://localhost:8000/health
```

### 2. Сборка образов

```bash
cd images/base-session && docker build -t base-session:latest .
cd ../designer-base && docker build -t designer-base:latest .
cd ../developer-base && docker build -t developer-base:latest .

docker tag designer-base:latest localhost:5000/designer-base:latest
docker push localhost:5000/designer-base:latest
```

### 3. Настройка станции (Windows)

```powershell
.\station\scripts\install-docker.ps1
.\station\scripts\setup-autostart.ps1
```

---

## Структура проекта

```
D:\repos\disser\
├── docs/                       # Документация
│   ├── README.md               # Этот файл
│   ├── architecture.md         # Архитектура
│   ├── INTEGRATION_PLAN.md     # План интеграции
│   ├── admin-guide.md          # Инструкция сисадмина
│   ├── local-testing.md        # Локальное тестирование
│   └── dissertation/           # Научная работа
├── server/                     # Сервер управления
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── app/
│       ├── main.py
│       └── config.py
├── images/                     # Docker образы
│   ├── base-session/
│   ├── designer-base/
│   └── developer-base/
├── station/                    # Рабочая станция
│   ├── launcher/
│   │   ├── main.py
│   │   └── config.py
│   └── scripts/
│       ├── install-docker.ps1
│       ├── setup-autostart.ps1
│       └── cleanup.ps1
└── tests/
    ├── load_test.py
    └── security_test.py
```

---

## Требования

| Компонент | Минимум | Рекомендуется |
|-----------|---------|---------------|
| **Сервер** | | |
| CPU | 4 ядра | 8 ядер |
| RAM | 8 ГБ | 16 ГБ |
| Disk | 50 ГБ SSD | 200 ГБ SSD |
| **Станция** | | |
| ОС | Windows 10/11 (64-bit) | Windows 11 |
| RAM | 8 ГБ | 16 ГБ |
| CPU | 4 ядра | 6 ядер |

---

## Статус

**MVP: В разработке**

- [x] Архитектура системы
- [x] Сервер управления (FastAPI + Registry)
- [x] Dockerfile образов
- [x] Лаунчер (Tkinter)
- [ ] Сборка образов
- [ ] Тестирование

---

## Лицензия

Внутренняя разработка ООО «Академия ТОП»
