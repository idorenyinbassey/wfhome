from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, request, flash

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Enum for user status
class UserStatus(Enum):
    ONLINE = 'online'
    AWAY = 'away'
    BUSY = 'busy'
    OFFLINE = 'offline'

# Enum for task type
class TaskType(Enum):
    INDIVIDUAL = 'individual'
    GROUP = 'group'

# Enum for message type
class MessageType(Enum):
    BROADCAST = 'broadcast'
    PRIVATE = 'private'
    GROUP = 'group'

# Enum for notification type
class NotificationType(Enum):
    MESSAGE = 'message'
    TASK = 'task'
    FILE = 'file'
    SYSTEM = 'system'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(db.Boolean, default = False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    
    first_name = db.Column(db.String(150), nullable=True)
    middle_name = db.Column(db.String(150), nullable=True)
    last_name = db.Column(db.String(150), nullable=True)
    department = db.Column(db.String(150), nullable=True, default='Unknown')
    phone_number = db.Column(db.String(15), nullable=True)
    address = db.Column(db.String(250), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default=UserStatus.ONLINE.value)

    # New field for profile picture
    profile_picture = db.Column(db.String(250), nullable=True)  # Path to the profile picture

    tasks = db.relationship('Task', foreign_keys='Task.user_id', backref='creator', lazy=True)
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assignee_id', backref='assignee', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return (f"User('{self.username}', '{self.email}', '{self.first_name}', '{self.last_name}', "
                f"'{self.department}', '{self.phone_number}', '{self.address}', '{self.date_created}', "
                f"'Profile Picture: {self.profile_picture}')")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), nullable=False, default='low')
    due_date = db.Column(db.DateTime, nullable=True)
    task_type = db.Column(db.String(20), nullable=False, default=TaskType.INDIVIDUAL.value)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Creator of the task
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Assigned user (optional)

    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # New fields for timer
    start_time = db.Column(db.DateTime, nullable=True)  # Task start time
    end_time = db.Column(db.DateTime, nullable=True)    # Task end time

    @property
    def duration(self):
        """Calculate the duration of the task."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None  # Return None if duration cannot be calculated

    def __repr__(self):
        return (f"Task('{self.title}', 'Assigned to user_id: {self.assignee_id if self.assignee_id else self.user_id}', "
                f"'Priority: {self.priority}', 'Due Date: {self.due_date}', 'Duration: {self.duration}')")
                
# Custom ModelView for User model
class UserModelView(ModelView):
    # Control which columns are displayed in the list view
    column_list = ('id', 'username', 'email', 'first_name', 'last_name', 'department', 'status', 'date_created')

    # Specify which columns can be searched
    column_searchable_list = ('username', 'email', 'first_name', 'last_name')

    # Specify which columns can be filtered
    column_filters = ('status', 'department')

    # Make specific columns editable from the list view
    column_editable_list = ('status', 'department')

    # Set form fields for creating or editing users (excluding sensitive data like password_hash)
    form_columns = ('username', 'email', 'first_name', 'middle_name', 'last_name', 'department', 
                    'phone_number', 'address', 'status', 'profile_picture')

    # Override is_accessible to restrict access to certain roles
    def is_accessible(self):
        # Replace with your condition to check admin rights (e.g., a role-based system)
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    # Redirect users who do not have access
    def inaccessible_callback(self, name, **kwargs):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('auth.login', next=request.url))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), nullable=False, default=MessageType.BROADCAST.value)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # For private messages
    department = db.Column(db.String(150), nullable=True)  # For department messages
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    
    def __repr__(self):
        return f"Message('{self.content[:50]}...', '{self.message_type}', sender_id={self.sender_id})"


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(20), nullable=False, 
                                 default=NotificationType.SYSTEM.value)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    related_id = db.Column(db.Integer, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='notifications')
    sender = db.relationship('User', foreign_keys=[sender_id])
    
    def __repr__(self):
        return (f"Notification('{self.title}', '{self.notification_type}', "
                f"user_id={self.user_id})")


class FileUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False, default='other')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    download_count = db.Column(db.Integer, default=0, nullable=False)
    is_private = db.Column(db.Boolean, default=False, nullable=False)
    
    user = db.relationship('User', backref='uploaded_files')
    
    def __repr__(self):
        return f"FileUpload('{self.original_filename}', user_id={self.user_id})"


class UserGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    creator = db.relationship('User', backref='created_groups')
    members = db.relationship('User', secondary='group_members', backref='groups')


# Association table for many-to-many relationship between users and groups
group_members = db.Table('group_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('user_group.id'), primary_key=True)
)

# Custom ModelView for Task model
class TaskModelView(ModelView):
    column_list = ('id', 'title', 'description', 'priority', 'due_date', 'task_type', 'creator', 'assignee', 'date_created', 'start_time', 'end_time')
    column_searchable_list = ('title', 'description')
    column_filters = ('priority', 'task_type', 'creator')
    form_columns = ('title', 'description', 'priority', 'due_date', 'task_type', 'user_id', 'assignee_id', 'start_time', 'end_time')

    def is_accessible(self):
        # Replace with your condition to check admin rights (e.g., a role-based system)
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('auth.login', next=request.url))