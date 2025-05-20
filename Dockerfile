FROM python:3.13-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

# Copy application code
COPY . .

# Set environment variables
ENV PORT=8080

# Expose port for Cloud Run
EXPOSE 8080

# Run the application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app.main:app
