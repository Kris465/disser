# Базовый образ для сессий
# Ubuntu 22.04 + XFCE + noVNC + общие зависимости

FROM ubuntu:22.04

# Подавляем интерактивные подсказки
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Moscow

# ============================================
# Базовые зависимости
# ============================================
RUN apt-get update && apt-get install -y \
    # XFCE рабочий стол
    xfce4 \
    xfce4-goodies \
    \
    # noVNC и VNC сервер
    novnc \
    websockify \
    tigervnc-standalone-server \
    \
    # Виртуальный дисплей
    xvfb \
    \
    # Утилиты
    supervisor \
    wget \
    curl \
    git \
    ca-certificates \
    locales \
    tzdata \
    \
    # Чистка кэша
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ============================================
# Локаль и часовой пояс
# ============================================
RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# ============================================
# Пользователь (не root для безопасности)
# ============================================
RUN useradd -m -s /bin/bash -G sudo session \
    && echo "session ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# ============================================
# Настройка VNC и noVNC
# ============================================
COPY scripts/vnc_startup.sh /usr/local/bin/vnc_startup.sh
RUN chmod +x /usr/local/bin/vnc_startup.sh

COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Создание директорий для логов supervisor
RUN mkdir -p /var/log/supervisor /var/run

# ============================================
# Порты: VNC (5900) и noVNC (6080)
# ============================================
EXPOSE 5900 6080

# ============================================
# Запуск через supervisor
# ============================================
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
