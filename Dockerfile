FROM python:3.10-slim

ENV APP_HOME=/home/app/api
WORKDIR $APP_HOME

# Copy source first so we have requirements available
COPY . $APP_HOME

# System dependencies (SQL Server ODBC driver + build tools for pyodbc)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        apt-transport-https \
        ca-certificates \
        gnupg \
        build-essential \
        unixodbc \
        unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/config/debian/12/prod/ stable main" \
        > /etc/apt/sources.list.d/microsoft-prod.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r app/requirements.txt \
    && pip install --no-cache-dir -e .

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]\n