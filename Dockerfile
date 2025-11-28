FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for WeasyPrint + fonts
RUN apt-get update && apt-get install -y \
    fontconfig \
    wget \
    build-essential \
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
    fonts-dejavu \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Create directory for Myanmar fonts
RUN mkdir -p /usr/share/fonts/truetype/myanmar/

# Copy the Pyidaungsu font correctly
COPY static/fonts/Pyidaungsu.ttf /usr/share/fonts/truetype/myanmar/Pyidaungsu.ttf

# Build the font cache
RUN fc-cache -f -v

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
