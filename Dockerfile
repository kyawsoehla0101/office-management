FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# --- Install system dependencies ---
RUN apt-get update && apt-get install -y \
    fontconfig \
    wget \
    build-essential \
    pkg-config \
    python3-dev \
    default-libmysqlclient-dev \
    # --- WeasyPrint deps ---
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    libxml2 \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    fonts-dejavu \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install Pyidaungsu font
RUN mkdir -p /usr/share/fonts/truetype/myanmar

RUN wget -O /usr/share/fonts/truetype/myanmar/Pyidaungsu.ttf \
    https://github.com/nginxinc/docker-nginx/blob/master/stable/stretch/font/Pyidaungsu.ttf?raw=true

RUN fc-cache -f -v
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
