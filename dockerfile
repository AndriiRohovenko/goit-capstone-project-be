FROM python:3.11-slim

WORKDIR /app

# Install Poetry + PostgreSQL dev dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && pip install poetry \
    && rm -rf /var/lib/apt/lists/*

# Copy app code
COPY . .

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi


# Expose port 5000
EXPOSE 5000

# Start the API
CMD ["start-prod"]