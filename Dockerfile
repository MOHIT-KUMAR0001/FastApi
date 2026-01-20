FROM python:3.11-alpine 

LABEL author="mohitdevx"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# system deps (safe baseline)
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["fastapi", "dev" ,"bin/app/main.py", "--host", "0.0.0.0", "--port", "8000"]

