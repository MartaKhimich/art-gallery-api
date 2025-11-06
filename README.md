# 🎨 Art Gallery API 
FastAPI приложение для управления коллекцией картин с использованием PostgreSQL.

# 🛠️ Технологии

- **Backend**: FastAPI, Python 3.11

- **Database**: PostgreSQL, SQLAlchemy, Alembic

- **Testing**: pytest, TestClient

- **Containerization**: Docker, Docker Compose

- **Documentation**: Swagger, ReDoc

# 📋 Предварительные требования
- 🐍 Python 3.8+ 
- 🐳 Docker и Docker Compose
- 🔧 Git

# Создание виртуального окружения 
python3 -m venv venv

source venv/bin/activate  # Linux/Mac

cp .env.example .env

# Установка зависимостей
pip install -r requirements.txt

# 🗄️ Запуск базы данных
docker-compose up -d

# 🗄️ Миграции базы данных
alembic upgrade head

# 🌱 Наполнение базы данных
python seed_database.py

# 🗄️ База данных
В проекте используется PostgreSQL с тремя основными таблицами:

    🎨 artists - Художники

    🏛️ museums - Музеи

    🖼️ paintings - Картины (связи с artists и museums)

# 🚀 Запуск приложения
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 🧪 Тесты
pytest -v -s

# 🌐 Доступ к приложению
📚 Swagger документация: http://localhost:8000/docs

📖 ReDoc документация: http://localhost:8000/redoc

🏠 Главная страница: http://localhost:8000/

🎨 Все картины: http://localhost:8000/paintings 

🖼️ Получить картину по ID: http://localhost:8000//paintings/{id}


# ✅ Соответствие заданию

- [x] FastAPI с роутами, схемами и зависимостями

- [x] Подключение PostgreSQL через SQLAlchemy

- [x] Асинхронные эндпоинты (async/await)

- [x] Тестирование с pytest

- [x] Пагинация, фильтрация и сортировка данных

- [x] Миграции базы данных через Alembic

- [x] Документация API через Swagger/ReDoc