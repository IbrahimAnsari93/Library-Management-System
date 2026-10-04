# Library Management System

A college-level Library Management System built with:
- Python
- Django
- SQL database (SQLite by default; MySQL supported)
- HTML/CSS

## Features
1. Dashboard
2. Add/search/delete books
3. Add students
4. Issue books
5. Return books
6. Automatic availability update
7. Automatic fine calculation (₹5 per late day)
8. Django Admin panel

## Run the project

### 1. Create virtual environment
Windows:
    python -m venv venv
    venv\Scripts\activate

Linux/macOS:
    python3 -m venv venv
    source venv/bin/activate

### 2. Install dependencies
    pip install -r requirements.txt

### 3. Create database tables
    python manage.py makemigrations
    python manage.py migrate

### 4. Create admin user
    python manage.py createsuperuser

### 5. Run server
    python manage.py runserver

Open:
    http://127.0.0.1:8000/

Admin:
    http://127.0.0.1:8000/admin/

## MySQL
Create a database named `library_db`, then uncomment the MySQL DATABASES section in:
    library_project/settings.py

Install MySQL connector:
    pip install mysqlclient

Then run:
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
