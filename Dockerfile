FROM python:3.12
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY **.py .
COPY poetry.lock .
COPY pyproject.toml .
COPY .env .env
COPY migrations migrations
COPY templates templates
COPY static static
COPY alembic.ini alembic.ini
COPY data.json data.json
RUN apt-get update && apt-get install -y nano
RUN python -m pip install --break-system-packages pipx
RUN pipx ensurepath --global --prepend
RUN pipx install --global poetry
RUN poetry config virtualenvs.create false
RUN poetry install --without dev --no-interaction --no-ansi --no-root