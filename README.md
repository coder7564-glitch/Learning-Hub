# Learning Management System (LMS)

A comprehensive Learning Management System built with Django (Backend) and React (Frontend), featuring Google Drive integration for video content management.

## Features

### Student Dashboard
- 🎓 Browse and enroll in courses
- 📺 Watch video lessons (Google Drive integration)
- 📊 Track learning progress
- 📝 Take quizzes and assessments
- 🏆 Earn certificates upon completion
- 👤 Manage profile settings

### Admin Dashboard
- 📚 Create and manage courses
- 👥 Manage students and enrollments
- 📝 Create quizzes and assessments
- 📈 View reports and analytics
- 🔗 Google Drive integration for video management
- ✅ Mark course completions

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Frontend**: React 18, React Router
- **Database**: PostgreSQL
- **Cache**: Redis
- **Authentication**: Google OAuth2, JWT
- **Cloud Storage**: Google Drive API
- **Containerization**: Docker, Docker Compose

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Google Cloud Console account (for OAuth2 and Drive API)

### 1. Clone and Setup Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your settings
# - Add your Google OAuth2 credentials
# - Set a secure SECRET_KEY
# - Configure database credentials
```

### 2. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Drive API
4. Configure OAuth2 consent screen
5. Create OAuth2 credentials (Web application)
6. Add authorized redirect URIs:
   - `http://localhost:8000/auth/complete/google-oauth2/`
   - `http://localhost:3000`
7. Copy Client ID and Client Secret to `.env`

### 3. Run with Docker

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Initialize Database

```bash
# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Load sample data (optional)
docker-compose exec backend python manage.py loaddata sample_data
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api/docs

## Project Structure

```
├── backend/                 # Django backend
│   ├── accounts/           # User authentication & profiles
│   ├── courses/            # Course management
│   ├── quizzes/            # Quiz & assessment system
│   ├── progress/           # Progress tracking & certificates
│   ├── google_drive/       # Google Drive integration
│   └── lms_project/        # Django project settings
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── context/        # React context (Auth)
│   │   ├── pages/          # Page components
│   │   │   ├── admin/      # Admin pages
│   │   │   ├── auth/       # Authentication pages
│   │   │   └── student/    # Student pages
│   │   └── services/       # API services
│   └── public/
├── nginx/                  # Nginx configuration
├── docker-compose.yml      # Docker orchestration
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Login with email/password
- `POST /api/auth/google/` - Google OAuth2 login
- `POST /api/auth/register/` - Register new user
- `GET /api/auth/profile/` - Get user profile

### Courses
- `GET /api/courses/` - List courses
- `GET /api/courses/{slug}/` - Course details
- `POST /api/courses/{slug}/enroll/` - Enroll in course
- `GET /api/courses/my-courses/` - User's enrolled courses

### Progress
- `GET /api/progress/my-progress/` - User's progress
- `POST /api/progress/video/update/` - Update video progress
- `GET /api/progress/certificates/` - User's certificates

### Quizzes
- `GET /api/quizzes/` - List quizzes
- `POST /api/quizzes/start/` - Start quiz attempt
- `POST /api/quizzes/submit/` - Submit quiz answers

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Debug mode (True/False) |
| `POSTGRES_DB` | Database name |
| `POSTGRES_USER` | Database user |
| `POSTGRES_PASSWORD` | Database password |
| `GOOGLE_CLIENT_ID` | Google OAuth2 Client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth2 Client Secret |
| `REACT_APP_API_URL` | Backend API URL |

## License

MIT License
