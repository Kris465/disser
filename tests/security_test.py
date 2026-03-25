"""
Тест безопасности контейнера
Проверка изоляции и ограничений
"""

import subprocess
import json
import sys


class ContainerSecurityTest:
    def __init__(self, container_name="test-security-container"):
        self.container_name = container_name
        self.test_image = "developer-base:latest"
    
    def run_command_in_container(self, command: str) -> dict:
        """Выполнение команды в контейнере"""
        try:
            result = subprocess.run(
                ["docker", "exec", self.container_name] + command.split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timeout",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def start_test_container(self):
        """Запуск тестового контейнера с ограничениями безопасности"""
        print("Запуск тестового контейнера...")
        
        cmd = [
            "docker", "run", "-d",
            "--name", self.container_name,
            "--cap-drop=ALL",
            "--read-only",
            "--tmpfs", "/tmp",
            "--tmpfs", "/run",
            "--tmpfs", "/home/session/.cache",
            "--security-opt", "no-new-privileges",
            self.test_image
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Ошибка запуска контейнера: {result.stderr}")
            return False
        
        # Ждём запуска
        subprocess.run(["sleep", "2"], shell=True)
        print("Контейнер запущен\n")
        return True
    
    def stop_test_container(self):
        """Остановка и удаление контейнера"""
        print(f"\nОстановка контейнера {self.container_name}...")
        
        subprocess.run(["docker", "stop", self.container_name], capture_output=True)
        subprocess.run(["docker", "rm", "-f", self.container_name], capture_output=True)
        
        print("Контейнер удалён")
    
    def test_escape_attempt(self):
        """Попытка выхода из контейнера"""
        print("=== Тест: Попытка выхода из контейнера ===")
        
        # Попытка доступа к хосту через /proc
        result = self.run_command_in_container("cat /proc/1/cgroup")
        print(f"Доступ к /proc/1/cgroup: {'Блокировано' if not result['success'] else 'Разрешено'}")
        
        # Попытка монтирования
        result = self.run_command_in_container("mount -t tmpfs none /mnt")
        print(f"Монтирование ФС: {'Блокировано' if not result['success'] else 'Разрешено (ОПАСНО!)'}")
        
        # Попытка доступа к сокету Docker
        result = self.run_command_in_container("ls -la /var/run/docker.sock")
        print(f"Доступ к docker.sock: {'Блокировано' if result['returncode'] != 0 else 'Разрешено (ОПАСНО!)'}")
        
        # Попытка запуска нового контейнера
        result = self.run_command_in_container("docker ps")
        print(f"Запуск docker ps: {'Блокировано' if result['returncode'] != 0 else 'Разрешено (ОПАСНО!)'}")
        
        print()
    
    def test_privilege_escalation(self):
        """Попытка повышения привилегий"""
        print("=== Тест: Повышение привилегий ===")
        
        # Проверка root доступа
        result = self.run_command_in_container("whoami")
        print(f"Текущий пользователь: {result['stdout']}")
        
        # Попытка выполнения команды от root
        result = self.run_command_in_container("sudo whoami")
        print(f"sudo whoami: {result['stdout'] if result['success'] else 'Недоступно'}")
        
        # Попытка записи в защищённую директорию
        result = self.run_command_in_container("touch /etc/test")
        print(f"Запись в /etc: {'Блокировано' if not result['success'] else 'Разрешено (ОПАСНО!)'}")
        
        # Попытка изменения прав
        result = self.run_command_in_container("chmod 777 /home/session")
        print(f"chmod в домашней директории: {'Блокировано' if not result['success'] else 'Разрешено'}")
        
        print()
    
    def test_persistence(self):
        """Попытка сохранения данных"""
        print("=== Тест: Сохранение данных (персистентность) ===")
        
        # Создание файла
        result = self.run_command_in_container("echo 'test' > /home/session/test.txt")
        print(f"Создание файла в /home/session: {'Успешно' if result['success'] else 'Неудачно'}")
        
        # Проверка записи в /tmp (должно работать из-за tmpfs)
        result = self.run_command_in_container("echo 'test' > /tmp/test.txt")
        print(f"Запись в /tmp (tmpfs): {'Успешно' if result['success'] else 'Неудачно'}")
        
        # Попытка записи в корень (должно быть заблокировано)
        result = self.run_command_in_container("echo 'test' > /test.txt")
        print(f"Запись в /: {'Блокировано' if not result['success'] else 'Разрешено (нежелательно)'}")
        
        print()
    
    def test_network_isolation(self):
        """Проверка сетевой изоляции"""
        print("=== Тест: Сетевая изоляция ===")
        
        # Проверка доступности хоста
        result = self.run_command_in_container("ping -c 1 172.17.0.1")
        print(f"Ping хоста: {'Блокировано' if result['returncode'] != 0 else 'Разрешено'}")
        
        # Проверка доступности внешних ресурсов
        result = self.run_command_in_container("curl -s --connect-timeout 2 http://8.8.8.8")
        print(f"Доступ в интернет: {'Есть' if result['success'] else 'Нет'}")
        
        # Проверка открытых портов
        result = self.run_command_in_container("netstat -tlnp 2>/dev/null || ss -tlnp")
        if result['success']:
            print(f"Открытые порты:\n{result['stdout']}")
        else:
            print("Не удалось проверить порты")
        
        print()
    
    def test_resource_limits(self):
        """Проверка ограничений ресурсов"""
        print("=== Тест: Ограничения ресурсов ===")
        
        # Проверка видимости памяти хоста
        result = self.run_command_in_container("free -h")
        if result['success']:
            print(f"Видимая память:\n{result['stdout']}")
        
        # Проверка видимости CPU
        result = self.run_command_in_container("nproc")
        if result['success']:
            print(f"Доступно CPU ядер: {result['stdout']}")
        
        # Попытка потребления всей памяти (должно быть ограничено)
        print("Попытка выделения 10 ГБ памяти (ожидание ограничения)...")
        result = self.run_command_in_container("python3 -c \"b = b'x' * (10 * 1024**3)\"")
        print(f"Выделение 10 ГБ: {'Успешно (ОПАСНО!)' if result['success'] else 'Блокировано (cgroups)'}")
        
        print()
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("=" * 60)
        print("ТЕСТ БЕЗОПАСНОСТИ КОНТЕЙНЕРА")
        print("=" * 60)
        print(f"Образ: {self.test_image}")
        print(f"Контейнер: {self.container_name}\n")
        
        if not self.start_test_container():
            print("Не удалось запустить контейнер для тестирования")
            return
        
        try:
            self.test_escape_attempt()
            self.test_privilege_escalation()
            self.test_persistence()
            self.test_network_isolation()
            self.test_resource_limits()
            
            print("=" * 60)
            print("РЕЗЮМЕ")
            print("=" * 60)
            print("Если все тесты показали 'Блокировано' - изоляция работает корректно")
            print("Если есть 'Разрешено (ОПАСНО!)' - требуется дополнительная настройка")
            
        finally:
            self.stop_test_container()


if __name__ == "__main__":
    # Проверка доступности Docker
    result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Ошибка: Docker не найден")
        sys.exit(1)
    
    print(f"Docker: {result.stdout.strip()}\n")
    
    test = ContainerSecurityTest()
    test.run_all_tests()
