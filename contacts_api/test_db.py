from database import engine

try:
    with engine.connect() as connection:
        print("Подключение успешно!")
except Exception as e:
    print(f"Ошибка: {e}")