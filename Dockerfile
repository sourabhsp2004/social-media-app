FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default command (can be overridden)
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
