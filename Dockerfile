FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN echo '#!/bin/bash\n\
if [ -n "$POSTGRES_USERNAME" ]; then\n\
  export DATABASE_URL="postgresql+asyncpg://${POSTGRES_USERNAME}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DATABASE_NAME}"\n\
  echo "Сгенерирован DATABASE_URL для FastAPI"\n\
fi\n\
\n\
alembic upgrade head\n\
uvicorn app.main:app --host 0.0.0.0 --port 8000' > /start.sh && chmod +x /start.sh

CMD ["/start.sh"]

