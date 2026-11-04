FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    postgresql \
    postgresql-contrib \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN echo '#!/bin/bash\n\
pg_ctlcluster 15 main start\n\
sleep 10\n\
pg_ctlcluster 15 main restart || true\n\
sleep 3\n\
su - postgres -c "psql -c \"ALTER USER postgres WITH PASSWORD '\''postgres'\'';\""\n\
su - postgres -c "psql -c \"CREATE DATABASE aggregator_db;\"" || true\n\
alembic upgrade head\n\
echo "Миграции Alembic успешно применены!"\n\
uvicorn app.main:app --host 0.0.0.0 --port 8000' > /start.sh && chmod +x /start.sh

CMD ["/start.sh"]
