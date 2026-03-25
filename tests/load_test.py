"""
Тест нагрузки сервера управления
Проверка обработки 100+ одновременных запросов
"""

import asyncio
import aiohttp
import time
from typing import List

# Конфигурация
SERVER_URL = "http://localhost:8000"
CONCURRENT_REQUESTS = 100
IMAGE_TYPES = ["designer", "developer"]


async def fetch_image_metadata(session: aiohttp.ClientSession, image_type: str) -> dict:
    """Запрос metadata образа"""
    start_time = time.time()
    
    try:
        async with session.get(f"{SERVER_URL}/image/{image_type}") as response:
            elapsed = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                return {
                    "status": "success",
                    "time": elapsed,
                    "data": data
                }
            else:
                return {
                    "status": "error",
                    "time": elapsed,
                    "error": f"HTTP {response.status}"
                }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "status": "error",
            "time": elapsed,
            "error": str(e)
        }


async def fetch_health(session: aiohttp.ClientSession) -> dict:
    """Запрос health check"""
    start_time = time.time()
    
    try:
        async with session.get(f"{SERVER_URL}/health") as response:
            elapsed = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                return {
                    "status": "success",
                    "time": elapsed,
                    "data": data
                }
            else:
                return {
                    "status": "error",
                    "time": elapsed,
                    "error": f"HTTP {response.status}"
                }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "status": "error",
            "time": elapsed,
            "error": str(e)
        }


async def load_test_image_metadata():
    """Тест нагрузки на endpoint /image/{type}"""
    print(f"=== Тест нагрузки: {CONCURRENT_REQUESTS} одновременных запросов ===\n")
    
    async with aiohttp.ClientSession() as session:
        # Создание задач
        tasks = []
        for i in range(CONCURRENT_REQUESTS):
            image_type = IMAGE_TYPES[i % len(IMAGE_TYPES)]
            tasks.append(fetch_image_metadata(session, image_type))
        
        # Запуск всех запросов одновременно
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Анализ результатов
        success_count = sum(1 for r in results if r["status"] == "success")
        error_count = sum(1 for r in results if r["status"] == "error")
        
        times = [r["time"] for r in results if r["status"] == "success"]
        avg_time = sum(times) / len(times) if times else 0
        min_time = min(times) if times else 0
        max_time = max(times) if times else 0
        
        # Вывод результатов
        print(f"Общее время: {total_time:.2f} сек")
        print(f"Успешных запросов: {success_count}/{CONCURRENT_REQUESTS}")
        print(f"Ошибок: {error_count}/{CONCURRENT_REQUESTS}")
        print(f"\nВремя ответа:")
        print(f"  Среднее: {avg_time*1000:.2f} мс")
        print(f"  Минимальное: {min_time*1000:.2f} мс")
        print(f"  Максимальное: {max_time*1000:.2f} мс")
        print(f"\nПропускная способность: {CONCURRENT_REQUESTS/total_time:.2f} запросов/сек")
        
        # Проверка соответствия требованиям
        print(f"\n=== Проверка требований ===")
        if avg_time < 0.1:  # 100 мс
            print("✓ Среднее время ответа < 100 мс")
        else:
            print(f"✗ Среднее время ответа > 100 мс ({avg_time*1000:.2f} мс)")
        
        if success_count == CONCURRENT_REQUESTS:
            print("✓ Все запросы успешны")
        else:
            print(f"✗ Есть ошибки ({error_count})")
        
        rps = CONCURRENT_REQUESTS / total_time
        if rps >= 1000:
            print(f"✓ Пропускная способность >= 1000 RPS ({rps:.2f})")
        else:
            print(f"✗ Пропускная способность < 1000 RPS ({rps:.2f})")


async def load_test_health():
    """Тест нагрузки на endpoint /health"""
    print(f"\n=== Тест нагрузки: /health ===\n")
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_health(session) for _ in range(CONCURRENT_REQUESTS)]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        success_count = sum(1 for r in results if r["status"] == "success")
        times = [r["time"] for r in results if r["status"] == "success"]
        avg_time = sum(times) / len(times) if times else 0
        
        print(f"Общее время: {total_time:.2f} сек")
        print(f"Успешных запросов: {success_count}/{CONCURRENT_REQUESTS}")
        print(f"Среднее время: {avg_time*1000:.2f} мс")
        print(f"Пропускная способность: {CONCURRENT_REQUESTS/total_time:.2f} RPS")


async def main():
    """Запуск всех тестов"""
    print("=" * 60)
    print("ТЕСТ НАГРУЗКИ СЕРВЕРА УПРАВЛЕНИЯ СЕССИЯМИ")
    print("=" * 60)
    print(f"\nСервер: {SERVER_URL}")
    print(f"Количество одновременных запросов: {CONCURRENT_REQUESTS}")
    print()
    
    # Проверка доступности сервера
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/health") as response:
                if response.status != 200:
                    print(f"Ошибка: Сервер недоступен (HTTP {response.status})")
                    return
    except Exception as e:
        print(f"Ошибка: Не удалось подключиться к серверу\n{e}")
        return
    
    print("Сервер доступен, запуск тестов...\n")
    
    # Тест /image/{type}
    await load_test_image_metadata()
    
    # Тест /health
    await load_test_health()
    
    print("\n" + "=" * 60)
    print("ТЕСТЫ ЗАВЕРШЕНЫ")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
