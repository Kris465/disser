# Образ для разработчиков
# VS Code, PHP, Chrome, Apache, Nginx, C++, Notepad++, Vim

FROM base-session:latest

LABEL maintainer="Academy TOP IT Security"
LABEL description="Developer session image with programming tools"

# ============================================
# Базовые зависимости для разработки
# ============================================
RUN apt-get update && apt-get install -y \
    # Компиляторы и инструменты сборки
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    \
    # Языки программирования
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    php \
    php-cli \
    php-mysql \
    php-curl \
    php-gd \
    php-mbstring \
    php-xml \
    php-zip \
    \
    # Веб-серверы
    apache2 \
    nginx \
    \
    # Базы данных (клиенты)
    mysql-client \
    postgresql-client \
    sqlite3 \
    \
    # Инструменты разработки
    git \
    vim \
    nano \
    curl \
    wget \
    \
    # Чистка кэша
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ============================================
# VS Code (через snap альтернатива - code-server)
# ============================================
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    wget \
    gnupg \
    && wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg \
    && install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg \
    && sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list' \
    && rm -f packages.microsoft.gpg \
    && apt-get update \
    && apt-get install -y code \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# Chrome браузер
# ============================================
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# Notepad++ (аналог через wine или текстовые редакторы)
# Используем mousepad + gedit как альтернативу
# ============================================
RUN apt-get update && apt-get install -y \
    mousepad \
    gedit \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# Настройка веб-серверов (не запускать в фоне)
# ============================================
# Apache - конфигурация
RUN mkdir -p /var/run/apache2 \
    && chown www-data:www-data /var/run/apache2

# Nginx - конфигурация
RUN mkdir -p /var/run/nginx \
    && chown www-data:www-data /var/run/nginx

# ============================================
# Настройки рабочего стола XFCE
# ============================================
RUN mkdir -p /home/session/Desktop && \
    chown -R session:session /home/session

# ============================================
# Информация о системе
# ============================================
RUN echo "=== Developer Session ===" > /etc/session-info && \
    echo "Image: developer-base:latest" >> /etc/session-info && \
    echo "Tools: VS Code, Chrome, PHP, Apache, Nginx, C++, Python, Node.js, Vim" >> /etc/session-info

# ============================================
# Пользователь и рабочая директория
# ============================================
USER session
WORKDIR /home/session

# ============================================
# Порт для noVNC (наследуется от base)
# ============================================
EXPOSE 5900
