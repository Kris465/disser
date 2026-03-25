# Образ для дизайнеров
# Krita, Inkscape, GIMP, Darktable, Kdenlive, Blender

FROM base-session:latest

LABEL maintainer="Academy TOP IT Security"
LABEL description="Designer session image with open-source graphics tools"

# ============================================
# Графические приложения
# ============================================
RUN apt-get update && apt-get install -y \
    # Krita - растровая графика (аналог Photoshop)
    krita \
    \
    # GIMP - растровая графика (дополнительно к Krita)
    gimp \
    \
    # Inkscape - векторная графика (аналог Illustrator)
    inkscape \
    \
    # Darktable - обработка фото (аналог Lightroom)
    darktable \
    \
    # Kdenlive - видеомонтаж (аналог Premiere Pro)
    kdenlive \
    \
    # Blender - 3D графика
    blender \
    \
    # Firefox - браузер для доступа к порталу
    firefox \
    \
    # Дополнительные кодеки для видео
    ffmpeg \
    \
    # Чистка кэша
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ============================================
# Настройки рабочего стола XFCE
# ============================================
# Обои по умолчанию (серый цвет)
RUN mkdir -p /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/ && \
    echo '<?xml version="1.0" encoding="UTF-8"?>' > /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '<channel name="xfce4-desktop" version="1.0">' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '  <property name="backdrop" type="empty">' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '    <property name="screen0" type="empty">' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '      <property name="monitor0" type="empty">' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '        <property name="workspace0" type="empty">' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '          <property name="color-style" type="int" value="0"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '          <property name="single-color" type="string" value="#4a4a4a"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '        </property>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '      </property>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '    </property>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '  </property>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '</channel>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml

# ============================================
# Меню приложений (ярлыки на рабочем столе)
# ============================================
RUN mkdir -p /home/session/Desktop && \
    chown -R session:session /home/session

# ============================================
# Информация о системе
# ============================================
RUN echo "=== Designer Session ===" > /etc/session-info && \
    echo "Image: designer-base:latest" >> /etc/session-info && \
    echo "Applications: Krita, GIMP, Inkscape, Darktable, Kdenlive, Blender, Firefox" >> /etc/session-info

USER session
WORKDIR /home/session

# ============================================
# Порт для noVNC (наследуется от base)
# ============================================
EXPOSE 5900
