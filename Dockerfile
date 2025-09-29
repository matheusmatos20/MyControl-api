FROM python:3.10-slim

ENV APP_HOME=/home/app/api
WORKDIR $APP_HOME
ENV PYTHONPATH="$APP_HOME:$APP_HOME/app"

COPY . $APP_HOME

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        gnupg \
        build-essential \
        unixodbc \
        unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl https://packages.microsoft.com/config/debian/12/prod.list \
        | tee /etc/apt/sources.list.d/microsoft-prod.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r app/requirements.txt

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
