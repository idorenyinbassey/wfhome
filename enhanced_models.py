from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
import uuid

db = SQLAlchemy()


class UserRole(Enum):
    USER = 'user'
    MANAGER = 'manager'
    ADMIN = 'admin'


class UserStatus(Enum):
    ACTIVE = 'active'
    AWAY = 'away'
    BUSY = 'busy'
    OFFLINE = 'offline'


class TaskStatus(Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class TaskPriority(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'


class TaskType(Enum):
    INDIVIDUAL = 'individual'
    GROUP = 'group'
    PROJECT = 'project'


# Association table for team members
team_members = db.Table('team_members',
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Enhanced profile fields
    first_name = db.Column(db.String(100), nullable=True)
    middle_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True, default='Unknown')
    job_title = db.Column(db.String(150), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    
    # System fields
    role = db.Column(db.String(20), nullable=False, default=UserRole.USER.value)
    is_admin = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), nullable=False, default=UserStatus.ACTIVE.value)
    profile_picture = db.Column(db.String(250), nullable=True)
    
    # Timestamps
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Settings
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    profile_visibility = db.Column(db.String(20), default='public')
    timezone = db.Column(db.String(50), default='UTC')
    
    # Relationships
    tasks_created = db.relationship('Task', foreign_keys='Task.creator_id', backref='creator', lazy=True)
    tasks_assigned = db.relationship('Task', foreign_keys='Task.assignee_id', backref='assignee', lazy=True)
    teams_managed = db.relationship('Team', backref='manager', lazy=True)
    time_logs = db.relationship('TimeLog', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        names = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(filter(None, names))
    
    def is_manager(self):
        return self.role in [UserRole.MANAGER.value, UserRole.ADMIN.value]
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Team(db.Model):
    __tablename__ = 'team'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Many-to-many relationship with users
    members = db.relationship('User', secondary=team_members, lazy='subquery',
                             backref=db.backref('teams', lazy=True))
    
    # One-to-many with tasks
    tasks = db.relationship('Task', backref='team', lazy=True)


class Project(db.Model):
    __tablename__ = 'project'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    budget = db.Column(db.Decimal(10, 2), nullable=True)
    status = db.Column(db.String(20), default='planning')
    priority = db.Column(db.String(20), default='medium')
    
    # Relationships
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    tasks = db.relationship('Task', backref='project', lazy=True)
    
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


class Task(db.Model):
    __tablename__ = 'task'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Status and priority
    status = db.Column(db.String(20), nullable=False, default=TaskStatus.PENDING.value)
    priority = db.Column(db.String(20), nullable=False, default=TaskPriority.LOW.value)
    task_type = db.Column(db.String(20), nullable=False, default=TaskType.INDIVIDUAL.value)
    
    # Time management
    estimated_hours = db.Column(db.Integer, nullable=True)
    actual_hours = db.Column(db.Integer, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    parent_task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    
    # Self-referential relationship for subtasks
    subtasks = db.relationship('Task', backref=db.backref('parent_task', remote_side=[id]), lazy=True)
    
    # File attachments
    attachments = db.relationship('TaskAttachment', backref='task', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('TaskComment', backref='task', lazy=True, cascade='all, delete-orphan')
    time_logs = db.relationship('TimeLog', backref='task', lazy=True)
    
    # Audit fields
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def duration(self):
        """Calculate the duration of the task."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    def get_progress_percentage(self):
        """Calculate task progress based on subtasks completion."""
        if not self.subtasks:
            return 100 if self.status == TaskStatus.COMPLETED.value else 0
        
        completed_subtasks = sum(1 for subtask in self.subtasks 
                               if subtask.status == TaskStatus.COMPLETED.value)
        return (completed_subtasks / len(self.subtasks)) * 100
    
    def is_overdue(self):
        """Check if task is overdue."""
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date and self.status != TaskStatus.COMPLETED.value


class TaskAttachment(db.Model):
    __tablename__ = 'task_attachment'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    content_type = db.Column(db.String(100), nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class TaskComment(db.Model):
    __tablename__ = 'task_comment'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    author = db.relationship('User', backref='task_comments')


class TimeLog(db.Model):
    __tablename__ = 'time_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class Notification(db.Model):
    __tablename__ = 'notification'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # task_assigned, deadline_approaching, etc.
    
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Optional reference to related objects
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
