FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--workers=3", "--bind=0.0.0.0:5000", "--timeout=120", "--access-logfile=-", "--error-logfile=-", "pialara:create_app()"]