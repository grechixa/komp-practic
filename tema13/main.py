from fastapi import FastAPI, HTTPException
import asyncio
import time  # Для симуляции медленной операции

app = FastAPI()

# Не лучшая практика - глобальная переменная для подключения, но для демо сойдет
connection_pool = None


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/slow_endpoint")
async def slow_endpoint():
    # Имитация тяжелой CPU-задачи или сложного вычисления
    time.sleep(0.1)  # Опасность! time.sleep блокирует весь event loop.
    return {"message": "This was a slow request"}


@app.get("/high_cpu_endpoint")
async def high_cpu_endpoint():
    # Функция, которая нагружает ЦПУ
    def cpu_intensive_task():
        total = 0
        for i in range(10_000_000):
            total += i
        return total

    result = cpu_intensive_task()
    return {"message": f"CPU task completed with result: {result}"}