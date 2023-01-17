FROM python:3.11.0-alpine

RUN apk add --update --no-cache gcc libc-dev libffi-dev

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir --upgrade poetry

RUN poetry config virtualenvs.create false && poetry install && mkdir log

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "logging.yaml"]


