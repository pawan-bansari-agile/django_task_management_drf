# Task Management System - Local Setup Guide

This document provides step-by-step instructions to run the Task Management System project locally.

## Prerequisites

Ensure the following tools are installed on your system:

1. Python 3.10 or higher
2. PostgreSQL (configured and running)
3. Virtualenv (Python Virtual Environment)
4. Git

## Steps to Set Up the Project Locally

### 1. Clone the Repository
```bash
$ git clone <repository_url>
$ cd <repository_name>
```

### 2. Create a Virtual Environment
```bash
$ python3 -m venv venv
$ source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
$ pip install --upgrade pip
$ pip install -r requirements.txt
```

### 4. Set Up the Database

#### 4.1. Create a PostgreSQL Database
Login to your PostgreSQL server and create a new database:

```sql
CREATE DATABASE <your_database_name>;
CREATE USER <your_database_user> WITH PASSWORD '<your_database_password>';
GRANT ALL PRIVILEGES ON DATABASE <your_database_name> TO <your_database_user>;
```

#### 4.2. Change the values in settings.py and Apply Migrations
```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

### 5. Run the Server
Start the Django development server:

```bash
$ python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`.

### 8. Access the Application
Open a browser and navigate to:
- **Admin Dashboard**: `http://127.0.0.1:8000/admin/`
- **Task Management System**: `http://127.0.0.1:8000/`

## Project Features

### Admin Features:
- Manage staff users (add, edit, block/unblock, delete).
- Assign tasks to staff users.
- Update task details and statuses.
- Archive tasks.

### Staff Features:
- View assigned tasks.
- Update task status (from ongoing to completed or vice versa).
- View task statistics (draft, ongoing, completed).

