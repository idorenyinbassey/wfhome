from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from models import User, db  # Import your models and db instance

# Initialize extensions
login_manager = LoginManager()
migrate = Migrate()

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Load user by ID

def create_app():
    """Application factory function to create the Flask app."""
    app = Flask(__name__)
    
    print("Registered routes:", app.url_map)

    # Load configuration from config.py
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Login manager settings
    login_manager.login_view = 'auth.login'  # Default login route

    # Register Blueprints
    from auth import auth as auth_blueprint
    from tasks import tasks as tasks_blueprint
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(tasks_blueprint)
    
    
    return app