FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    fontconfig \
    build-essential \
    wget \
    pkg-config \
    python3-dev \
    default-libmysqlclient-dev \
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
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/share/fonts/truetype/myanmar/

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy entire project
COPY . .

# Copy Pyidaungsu font from static folder
COPY static/fonts/Pyidaungsu.ttf /usr/share/fonts/truetype/myanmar/Pyidaungsu.ttf
COPY static/fonts/Pyidaungsu-Regular.ttf /usr/share/fonts/truetype/myanmar/Pyidaungsu-Regular.ttf

RUN fc-cache -f -v

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
