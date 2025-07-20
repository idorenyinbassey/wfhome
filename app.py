from flask import Flask, redirect, url_for, request, flash
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from config import Config
from models import User, Task, db  # Import your models and db instance
from datetime import datetime

# Initialize extensions
login_manager = LoginManager()
migrate = Migrate()

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Load user by ID

# Custom ModelView for User
class UserModelView(ModelView):
    column_list = ('id', 'username', 'email', 'first_name', 'last_name', 'department', 'status', 'date_created')
    column_searchable_list = ('username', 'email', 'first_name', 'last_name')
    column_filters = ('status', 'department')
    column_editable_list = ('status', 'department')
    form_columns = ('username', 'email', 'password_hash', 'first_name', 'middle_name', 'last_name', 'department',
                    'phone_number', 'address', 'status', 'profile_picture')

    def is_accessible(self):
        # Customize access control (e.g., only admin can access)
        return current_user.is_authenticated and current_user.username == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('auth.login', next=request.url))

# Custom ModelView for Task
class TaskModelView(ModelView):
    column_list = ('id', 'title', 'description', 'priority', 'due_date', 'task_type', 'user_id', 'assignee_id', 'date_created', 'start_time', 'end_time')
    column_searchable_list = ('title', 'description')
    column_filters = ('priority', 'task_type', 'user_id')  # Ensure these attributes exist in the model
    form_columns = ('title', 'description', 'priority', 'due_date', 'task_type', 'user_id', 'assignee_id', 'start_time', 'end_time')

    def is_accessible(self):
        # Customize access control (e.g., only admin can access)
        return current_user.is_authenticated and current_user.username == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('auth.login', next=request.url))

def create_app(config_class=Config):
    """Application factory function to create the Flask app."""
    app = Flask(__name__)

    # Load configuration dynamically
    app.config.from_object(config_class)

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Login manager settings
    login_manager.login_view = 'auth.login'  # Default login route

    # Register Blueprints
    from auth import auth as auth_blueprint
    from tasks import tasks as tasks_blueprint
    from api_endpoints import api_bp as api_blueprint
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(tasks_blueprint)
    app.register_blueprint(api_blueprint)

    # Custom Jinja2 filter for formatting datetime
    @app.template_filter('datetimeformat')
    def datetimeformat(value, format='%Y-%m-%dT%H:%M'):
        if value:
            return value.strftime(format)
        return ''

    # Initialize Flask-Admin (temporarily disabled for simplification)
    # admin = Admin(app, name='Admin Dashboard', template_mode='bootstrap4')
    
    # Add custom model views to the admin
    # admin.add_view(UserModelView(User, db.session))
    # admin.add_view(TaskModelView(Task, db.session))

    return app