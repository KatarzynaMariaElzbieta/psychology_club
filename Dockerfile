FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false

# Copy dependency files first
COPY pyproject.toml poetry.lock* ./

# Install deps
RUN poetry install --no-root --no-interaction --no-ansi

# Copy source code
COPY . .

# Railway uses port 8080
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Start production server
CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "wsgi:app"]
