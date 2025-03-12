FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy dependency definitions and install dependencies.
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY . .

EXPOSE 5000

# Run the app using Gunicorn.
CMD ["gunicorn", "-c", "gunicorn_config.py", "app:app"]
