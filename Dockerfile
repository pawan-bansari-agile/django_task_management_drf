# 1. Use a Python base image
FROM python:3.10-slim

# 2. Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=task_management_system_drf.settings \
    PYTHONDONTWRITEBYTECODE=1

# 3. Set the working directory
WORKDIR /app

# 4. Install OS-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the project files
COPY . /app/

# 7. Expose the application port
EXPOSE 8000

# 8. Run the Django application
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "task_management_system_drf.wsgi:application"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

