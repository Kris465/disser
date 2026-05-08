"""
Лаунчер изолированных сессий
Рабочая станция: выбор типа сессии и запуск контейнера
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import subprocess
import os
import sys

# Конфигурация
SERVER_URL = os.getenv("SESSION_SERVER", "http://192.168.1.100:8000")
DESIGNER_IMAGE = "designer-base:latest"
DEVELOPER_IMAGE = "developer-base:latest"


class SessionLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Academy TOP - Session Launcher")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Центрирование окна
        self.center_window()

        # Текущий статус
        self.session_active = False
        self.container_name = None

        self.create_widgets()
        self.check_server_health()

    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = 800
        height = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Заголовок
        title_frame = ttk.Frame(self.root, padding="20")
        title_frame.pack(fill=tk.X)

        title_label = ttk.Label(
            title_frame,
            text="Выберите тип сессии",
            font=("Arial", 24, "bold")
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="Academy TOP - Изолированная рабочая среда",
            font=("Arial", 12),
            foreground="gray"
        )
        subtitle_label.pack()

        # Основной контент
        content_frame = ttk.Frame(self.root, padding="40")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Кнопка Дизайнер
        designer_btn = ttk.Button(
            content_frame,
            text="Дизайнер",
            command=lambda: self.start_session("designer"),
            width=30,
            padding=20
        )
        designer_btn.pack(pady=20, fill=tk.X)

        designer_desc = ttk.Label(
            content_frame,
            text="Krita, GIMP, Inkscape, Blender, Darktable, Kdenlive",
            font=("Arial", 10),
            foreground="gray"
        )
        designer_desc.pack()

        # Кнопка Разработчик
        developer_btn = ttk.Button(
            content_frame,
            text="💻 Разработчик",
            command=lambda: self.start_session("developer"),
            width=30,
            padding=20
        )
        developer_btn.pack(pady=20, fill=tk.X)

        developer_desc = ttk.Label(
            content_frame,
            text="VS Code, PHP, Python, Node.js, C++, Apache, Nginx, Chrome",
            font=("Arial", 10),
            foreground="gray"
        )
        developer_desc.pack()

        # Статус бар
        self.status_label = ttk.Label(
            self.root,
            text="Ожидание выбора...",
            font=("Arial", 10),
            foreground="blue",
            padding=10
        )
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

    def check_server_health(self):
        """Проверка доступности сервера"""
        try:
            response = requests.get(f"{SERVER_URL}/health", timeout=5)
            if response.status_code == 200:
                self.status_label.config(
                    text="Сервер доступен",
                    foreground="green"
                )
            else:
                self.status_label.config(
                    text="Сервер недоступен, работа с локальным кэшем",
                    foreground="orange"
                )
        except requests.exceptions.RequestException:
            self.status_label.config(
                text="Сервер недоступен, работа с локальным кэшем",
                foreground="orange"
            )

    def start_session(self, session_type):
        """Запуск сессии выбранного типа"""
        if self.session_active:
            messagebox.showwarning(
                "Сессия активна",
                "Сессия уже запущена. Закройте текущую сессию перед запуском новой."
            )
            return

        self.status_label.config(
            text="Запуск сессии...",
            foreground="blue"
        )

        try:
            # Получение metadata образа с сервера
            image_metadata = self.get_image_metadata(session_type)

            # Проверка локального кэша и запуск
            self.launch_container(session_type, image_metadata)

        except requests.exceptions.RequestException as e:
            # Сервер недоступен, пробуем локальный образ
            self.status_label.config(
                text="Сервер недоступен, запуск локального образа...",
                foreground="orange"
            )
            self.launch_container_local(session_type)

        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"Не удалось запустить сессию:\n{str(e)}\n\nОбратитесь к администратору."
            )
            self.status_label.config(
                text="Ошибка запуска",
                foreground="red"
            )

    def get_image_metadata(self, session_type):
        """Получение metadata образа с сервера"""
        response = requests.get(
            f"{SERVER_URL}/image/{session_type}",
            timeout=10
        )

        if response.status_code != 200:
            raise Exception(f"Сервер вернул ошибку: {response.status_code}")

        return response.json()

    def launch_container(self, session_type, metadata):
        """Запуск контейнера с загрузкой образа при необходимости"""
        image_name = metadata["full_name"]

        # Проверка наличия образа локально
        if not self.is_image_local(image_name):
            self.status_label.config(
                text="Загрузка образа...",
                foreground="blue"
            )
            self.pull_image(image_name)

        # Запуск контейнера
        self.status_label.config(
            text="Запуск контейнера...",
            foreground="blue"
        )

        container_name = f"session_{session_type}_{os.getpid()}"
        self.container_name = container_name

        # Docker run команда
        docker_cmd = [
            "docker", "run", "-d",
            "--rm",
            "--name", container_name,
            "--cap-drop=ALL",
            "--read-only",
            "--tmpfs", "/tmp",
            "--tmpfs", "/run",
            "--tmpfs", "/home/session/.cache",
            "-p", "5900:5900",
            "-p", "6080:6080",
            image_name
        ]

        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Ошибка запуска контейнера:\n{result.stderr}")

        self.session_active = True

        # Ожидание готовности noVNC (до 15 секунд)
        self.status_label.config(
            text="Ожидание готовности сервера...",
            foreground="blue"
        )
        self.root.update()

        import time
        for i in range(15):
            time.sleep(1)
            try:
                check = requests.get("http://localhost:6080/vnc.html", timeout=2)
                if check.status_code == 200:
                    break
            except Exception:
                pass

        # Открытие noVNC в браузере
        self.open_novnc()

        self.status_label.config(
            text="Сессия запущена",
            foreground="green"
        )

        # Закрытие лаунчера
        self.root.after(3000, self.root.quit)

    def launch_container_local(self, session_type):
        """Запуск локального образа (без сервера)"""
        if session_type == "designer":
            image_name = DESIGNER_IMAGE
        else:
            image_name = DEVELOPER_IMAGE

        # Проверка наличия образа
        if not self.is_image_local(image_name):
            raise Exception(
                "Локальный образ не найден.\n"
                "Сервер недоступен и кэш отсутствует.\n"
                "Обратитесь к администратору."
            )

        self.launch_container(session_type, {
            "full_name": image_name
        })

    def is_image_local(self, image_name):
        """Проверка наличия образа в локальном кэше Docker"""
        result = subprocess.run(
            ["docker", "images", "-q", image_name],
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())

    def pull_image(self, image_name):
        """Загрузка образа из registry"""
        result = subprocess.run(
            ["docker", "pull", image_name],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Ошибка загрузки образа:\n{result.stderr}")

    def open_novnc(self):
        """Открытие noVNC в браузере (полноэкранный режим)"""
        novnc_url = "http://localhost:6080/vnc.html?autoconnect=true"

        # Запуск браузера в режиме киоска
        if sys.platform == "win32":
            # Windows — используем start для запуска браузера по умолчанию
            # или chrome из стандартных путей
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
            chrome_exe = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_exe = path
                    break

            if chrome_exe:
                subprocess.Popen([
                    chrome_exe,
                    "--kiosk",
                    "--app=" + novnc_url
                ])
            else:
                # Fallback: открываем браузер по умолчанию через start
                os.system(f'start "" "{novnc_url}"')
        else:
            # Linux
            subprocess.Popen([
                "google-chrome",
                "--kiosk",
                "--app=" + novnc_url
            ])


def main():
    root = tk.Tk()
    app = SessionLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
