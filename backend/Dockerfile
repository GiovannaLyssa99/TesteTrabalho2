FROM python:3.13-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.13-slim

WORKDIR /app

ARG APP_USER=appuser
ENV APP_USER=${APP_USER}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

RUN useradd -m ${APP_USER}

COPY --from=builder /root/.local /home/${APP_USER}/.local

ENV PATH=/home/${APP_USER}/.local/bin:$PATH


COPY . .

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh


RUN mkdir -p /app/data && chown -R ${APP_USER}:${APP_USER} /app


USER ${APP_USER}

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]