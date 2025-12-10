FROM python:3.10-slim

WORKDIR /app

RUN pip install poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock /app/

RUN poetry install --only main --no-root

RUN useradd -m -u 1000 user

RUN chown -R user /app

USER user

COPY --chown=user alembic.ini /app/

COPY --chown=user src /app/src

EXPOSE 7860

ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "src.app:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:7860", "--timeout", "600", "--keep-alive", "120"]
