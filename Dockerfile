FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.lock ./requirements.lock
RUN pip install --no-cache-dir -r requirements.lock
COPY . .
RUN mkdir -p /data/uploads
ENV DATABASE_PATH=/data/itlive_bot.db UPLOAD_DIR=/data/uploads PORT=8000
EXPOSE 8000
CMD ["python", "run.py"]
