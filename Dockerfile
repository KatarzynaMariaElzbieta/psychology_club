FROM python:3.12-slim

WORKDIR /app

# Zainstaluj Poetry
RUN pip install --no-cache-dir poetry

# 🔑 Najważniejsze: wyłącz tworzenie .venv i instaluj zależności globalnie
RUN poetry config virtualenvs.create false

# Skopiuj pliki projektu
COPY pyproject.toml poetry.lock* ./

# Zainstaluj zależności bez budowania projektu
RUN poetry install --no-root --no-interaction --no-ansi

# Skopiuj cały kod źródłowy
COPY . .

# Ustawienie zmiennych środowiskowych
ENV PYTHONUNBUFFERED=1

# Domyślny CMD
CMD ["flask", "run", "--host=0.0.0.0"]
