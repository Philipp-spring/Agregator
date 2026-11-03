# Агрегатор событий (Events Aggregator)

# Агрегатор событий (Events Aggregator)

Backend-сервис на Python, который интегрируется с внешним Events Provider API, кэширует данные в локальной базе данных и предоставляет удобный REST API для работы с событиями и регистрацией на них.

## Технологический стек

*   **Язык:** Python 3.11
*   **Фреймворк:** FastAPI
*   **База данных:** PostgreSQL (асинхронный драйвер `asyncpg`)
*   **ORM:** SQLAlchemy 2.0 (с использованием паттерна Repository)
*   **Миграции:** Alembic
*   **HTTP-клиент:** httpx (для интеграции с внешним API)
*   **Управление зависимостями:** uv (локально), pip (в Docker)
*   **Линтер:** Ruff (с проверкой PEP8)
*   **Контейнеризация:** Docker, Docker Compose
*   **CI/CD:** GitHub Actions (линтер -> сборка -> деплой)

## Архитектура

Проект построен по слоистой архитектуре (Clean Architecture):
*   **Routers** (`app/routers/`) — принимают HTTP-запросы и валидируют их через Pydantic.
*   **Services** (`app/services/`) — содержат бизнес-логику.
*   **Repositories** (`app/repositories/`) — изолируют работу с базой данных (SQLAlchemy).
*   **Clients** (`app/clients/`) — отвечают за интеграцию с внешним API.

## Запуск проекта

### 1. Подготовка
Склонируйте репозиторий и создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env