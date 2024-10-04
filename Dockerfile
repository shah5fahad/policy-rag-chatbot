FROM python:3.12

WORKDIR /app

RUN pip install poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock /app/

RUN poetry install --only main --no-root

RUN useradd -m -u 1000 user

RUN chown -R user /app

USER user

COPY --chown=user alembic.ini /app/

COPY --chown=user migrations /app/migrations

COPY --chown=user src /app/src

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["poetry", "run", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
