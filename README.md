# MusicWave - Music Streaming Service

A modern web-based music streaming service built with Django that allows users to discover, stream, and share their favorite music.

## Features

- 🎵 Music Streaming: Stream high-quality music directly from the browser
- 👤 User Authentication: Secure login/registration system with Google OAuth support
- 📱 Responsive Design: Beautiful and modern UI that works on all devices
- 📑 Playlist Management: Create, edit, and share playlists
- 🎨 User Profiles: Customizable user profiles with profile pictures and bio
- 🔍 Search Functionality: Search for music by title, artist, or genre
- 📊 Music Rating System: Rate and review your favorite tracks
- 📈 Play History: Track your listening history
- 📝 Contact System: Built-in contact form for user feedback
- 👥 Admin Panel: Comprehensive admin interface for content management

## Technology Stack

- **Backend**: Django 5.2
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Authentication**: Django Authentication + Social Auth (Google OAuth2)
- **Frontend**: HTML, CSS, JavaScript
- **File Storage**: Local file system for media files
- **Security**: Django's built-in security features + Custom middleware for HTTPS

## Prerequisites

- Python 3.x
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd music_service
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up the database:

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

The application will be available at `http://localhost:8000`

## Environment Variables

Create a `.env` file in the root directory and add the following variables:

```
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Google OAuth2 credentials
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your_google_oauth2_key
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your_google_oauth2_secret

# Database configuration (for production)
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
```

## Project Structure

- `music_service/` - Main project directory
  - `settings.py` - Project settings
  - `urls.py` - Main URL configuration
- `core/` - Main application directory
  - `models.py` - Database models
  - `views.py` - View functions
  - `urls.py` - URL patterns
  - `admin.py` - Admin interface configuration
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS, images)
- `media/` - User-uploaded files
- `manage.py` - Django management script

## Usage

1. Access the admin interface at `http://localhost:8000/admin` to manage content
2. Register a new user account or log in with Google
3. Upload and manage music files
4. Create and manage playlists
5. Browse and stream music
6. Rate songs and maintain play history

## Development

- Follow PEP 8 style guide for Python code
- Use meaningful commit messages
- Write tests for new features
- Document code changes

## Production Deployment

Before deploying to production:

1. Set `DEBUG=False` in settings
2. Configure a production-grade database (PostgreSQL recommended)
3. Set up proper static and media file serving
4. Configure HTTPS
5. Set up proper email backend
6. Update `ALLOWED_HOSTS`
7. Configure proper logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please use the following channels:

- Create an issue in the repository
- Use the contact form in the application
- Email: support@musicwave.com (replace with actual support email)
