# WFHome - Work From Home Management System

**WFHome** is a modern, streamlined work-from-home task management system built with Flask. Designed for simplicity and efficiency, this platform enables remote workers and teams to create, track, and manage tasks with a clean, professional interface.

## 🚀 Features

### Core Functionality
- **User Authentication** - Secure registration and login system
- **Task Management** - Create, edit, delete, and track task completion
- **Personal Dashboard** - Clean interface showing your tasks and progress
- **Profile Management** - Manage user information and preferences
- **Timer Integration** - Track task duration and completion times
- **Assignment System** - Assign tasks to team members
- **Professional UI** - Clean, modern blue-themed interface

### Technical Features
- **Responsive Design** - Works on desktop and mobile devices
- **Blueprint Architecture** - Modular Flask application structure
- **Database Migrations** - Alembic integration for schema management
- **Session Management** - Secure user sessions with Flask-Login
- **SQLite Database** - Lightweight database for easy deployment

## 🛠️ Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Migrations**: Flask-Migrate + Alembic
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Bootstrap 5 + Custom CSS
- **Version Control**: Git

## 📁 Project Structure

```plaintext
wfhome/
├── auth/                    # Authentication blueprint
│   ├── __init__.py
│   ├── forms.py            # Login/register forms
│   └── routes.py           # Auth routes
├── tasks/                   # Task management blueprint
│   ├── __init__.py
│   ├── forms.py            # Task forms
│   └── routes.py           # Task routes
├── static/                  # Static assets
│   ├── css/
│   │   └── styles.css      # Main stylesheet
│   ├── js/
│   │   └── script.js       # JavaScript functionality
│   ├── images/
│   └── uploads/            # User uploaded files
├── templates/               # Jinja2 templates
│   ├── base.html           # Base template
│   ├── dashboard.html      # Main dashboard
│   ├── index.html          # Landing page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── profile.html        # User profile
│   ├── edit_task.html      # Task editing
│   └── settings.html       # User settings
├── migrations/              # Database migrations
├── instance/               # Instance-specific files (gitignored)
├── app.py                  # Application factory
├── config.py               # Configuration settings
├── models.py               # Database models
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/idorenyinbassey/wfhome.git
   cd wfhome
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/macOS
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the application**
   - Open your browser to `http://127.0.0.1:5000`
   - Register a new account or login
   - Start managing your tasks!

## 🐳 Docker Deployment

### Build and Run with Docker

1. **Build the Docker image**
   ```bash
   docker build -t wfhome:latest .
   ```

2. **Run the container**
   ```bash
   docker run -d -p 5000:5000 --name wfhome-app wfhome:latest
   ```

### Using Docker Compose

1. **Start the application**
   ```bash
   docker-compose up -d
   ```

2. **Stop the application**
   ```bash
   docker-compose down
   ```

## 🌐 Production Deployment

### Heroku Deployment

1. **Install Heroku CLI and login**
   ```bash
   heroku login
   ```

2. **Create Heroku app**
   ```bash
   heroku create your-wfhome-app
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

### Render Deployment

1. Connect your GitHub repository to Render
2. Render will auto-detect the Flask app
3. Set environment variables as needed
4. Deploy with one click

### DigitalOcean App Platform

1. Create a new app on DigitalOcean
2. Connect your GitHub repository
3. Configure build and run commands
4. Deploy automatically on push

## 📖 Usage Guide

### Getting Started
1. **Register** - Create your account with email and password
2. **Login** - Access your personal dashboard
3. **Profile** - Complete your profile information
4. **Create Tasks** - Use the dashboard form to create new tasks
5. **Manage Tasks** - Edit, complete, or delete tasks as needed

### Task Management
- **Create**: Fill out the task creation form with title, description, priority, and due date
- **Assign**: Assign tasks to yourself or team members
- **Track**: Monitor task progress with start/end times
- **Complete**: Mark tasks as completed when finished

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/site.db
```

### Database Configuration
The application uses SQLite by default. For production, consider PostgreSQL:

```python
# config.py
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/site.db'
```

## 🧪 Testing

```bash
# Run tests (when implemented)
python -m pytest

# Run with coverage
python -m pytest --cov=app
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write clear, descriptive commit messages
- Add tests for new functionality
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask community for the excellent framework
- Bootstrap team for the UI components
- All contributors who help improve this project

---

**WFHome** © 2025 by **Predorio LTD**. All rights reserved.

*Built with ❤️ for remote teams and productivity enthusiasts.*
