# Music Streaming Service

A beautiful and simple music streaming platform built with Django.

## Setup Instructions

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database and update settings.py with your database credentials

4. Run migrations:

```bash
python manage.py migrate
```

5. Create a superuser:

```bash
python manage.py createsuperuser
```

6. Run the development server:

```bash
python manage.py runserver
```

## Features

- User authentication
- Music streaming
- Song ratings
- Play history tracking
- Beautiful and responsive UI
