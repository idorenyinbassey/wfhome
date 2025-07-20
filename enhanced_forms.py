from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (StringField, PasswordField, SubmitField, SelectField, 
                     TextAreaField, DateField, DateTimeLocalField, IntegerField,
                     BooleanField, DecimalField, HiddenField)
from wtforms.validators import (DataRequired, Length, Email, EqualTo, Optional,
                               NumberRange, ValidationError, Regexp)
from datetime import datetime, date
import re


class EnhancedRegistrationForm(FlaskForm):
    """Enhanced registration form with better validation."""
    
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20),
        Regexp(r'^[A-Za-z][A-Za-z0-9_]*$', 
               message="Username must start with a letter and contain only letters, numbers, and underscores")
    ])
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Invalid email address"),
        Length(max=120)
    ])
    
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=50),
        Regexp(r'^[A-Za-z\s]+$', message="Name can only contain letters and spaces")
    ])
    
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(min=2, max=50),
        Regexp(r'^[A-Za-z\s]+$', message="Name can only contain letters and spaces")
    ])
    
    department = SelectField('Department', choices=[
        ('', 'Select Department'),
        ('HR', 'Human Resources'),
        ('IT', 'Information Technology'),
        ('Finance', 'Finance'),
        ('Marketing', 'Marketing'),
        ('Operations', 'Operations'),
        ('Legal', 'Legal'),
        ('Sales', 'Sales'),
        ('Support', 'Customer Support')
    ], validators=[DataRequired()])
    
    job_title = StringField('Job Title', validators=[
        Optional(),
        Length(max=100)
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ])
    
    submit = SubmitField('Register')
    
    def validate_password(self, field):
        """Custom password validation."""
        password = field.data
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r'[0-9]', password):
            raise ValidationError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain at least one special character")


class EnhancedTaskForm(FlaskForm):
    """Enhanced task creation/editing form."""
    
    title = StringField('Task Title', validators=[
        DataRequired(),
        Length(min=3, max=200)
    ])
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=2000)
    ])
    
    task_type = SelectField('Task Type', choices=[
        ('individual', 'Individual Task'),
        ('group', 'Group Task'),
        ('project', 'Project Task')
    ], validators=[DataRequired()])
    
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], validators=[DataRequired()])
    
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    
    estimated_hours = IntegerField('Estimated Hours', validators=[
        Optional(),
        NumberRange(min=1, max=1000, message="Hours must be between 1 and 1000")
    ])
    
    due_date = DateTimeLocalField('Due Date', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    start_date = DateTimeLocalField('Start Date', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    
    assignee_id = SelectField('Assignee', coerce=int, validators=[Optional()])
    project_id = SelectField('Project', coerce=int, validators=[Optional()])
    team_id = SelectField('Team', coerce=int, validators=[Optional()])
    parent_task_id = HiddenField()
    
    # File attachments
    attachments = FileField('Attachments', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt', 'zip'],
                   'Invalid file type!')
    ])
    
    submit = SubmitField('Save Task')
    
    def validate_due_date(self, field):
        """Validate due date is in the future."""
        if field.data and field.data < datetime.now():
            raise ValidationError('Due date must be in the future')
    
    def validate_start_date(self, field):
        """Validate start date logic."""
        if field.data and self.due_date.data:
            if field.data > self.due_date.data:
                raise ValidationError('Start date cannot be after due date')


class ProjectForm(FlaskForm):
    """Project creation and editing form."""
    
    name = StringField('Project Name', validators=[
        DataRequired(),
        Length(min=3, max=200)
    ])
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=2000)
    ])
    
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])
    
    budget = DecimalField('Budget', validators=[
        Optional(),
        NumberRange(min=0, message="Budget cannot be negative")
    ])
    
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], validators=[DataRequired()])
    
    status = SelectField('Status', choices=[
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    
    manager_id = SelectField('Project Manager', coerce=int, validators=[DataRequired()])
    team_id = SelectField('Team', coerce=int, validators=[Optional()])
    
    submit = SubmitField('Save Project')
    
    def validate_end_date(self, field):
        """Validate end date is after start date."""
        if field.data and self.start_date.data:
            if field.data < self.start_date.data:
                raise ValidationError('End date must be after start date')


class TeamForm(FlaskForm):
    """Team creation and editing form."""
    
    name = StringField('Team Name', validators=[
        DataRequired(),
        Length(min=2, max=150)
    ])
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=1000)
    ])
    
    manager_id = SelectField('Team Manager', coerce=int, validators=[DataRequired()])
    
    submit = SubmitField('Save Team')


class TimeLogForm(FlaskForm):
    """Time logging form."""
    
    task_id = SelectField('Task', coerce=int, validators=[DataRequired()])
    start_time = DateTimeLocalField('Start Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_time = DateTimeLocalField('End Time', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    
    submit = SubmitField('Log Time')
    
    def validate_end_time(self, field):
        """Validate end time is after start time."""
        if field.data and self.start_time.data:
            if field.data <= self.start_time.data:
                raise ValidationError('End time must be after start time')


class CommentForm(FlaskForm):
    """Task comment form."""
    
    comment = TextAreaField('Comment', validators=[
        DataRequired(),
        Length(min=1, max=1000)
    ])
    
    submit = SubmitField('Add Comment')


class SearchForm(FlaskForm):
    """Advanced search form."""
    
    query = StringField('Search', validators=[Optional(), Length(max=200)])
    search_type = SelectField('Search In', choices=[
        ('all', 'All'),
        ('tasks', 'Tasks'),
        ('projects', 'Projects'),
        ('users', 'Users')
    ], default='all')
    
    status = SelectField('Status', choices=[
        ('', 'Any Status'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ])
    
    priority = SelectField('Priority', choices=[
        ('', 'Any Priority'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ])
    
    assignee_id = SelectField('Assignee', coerce=int, validators=[Optional()])
    date_from = DateField('From Date', validators=[Optional()])
    date_to = DateField('To Date', validators=[Optional()])
    
    submit = SubmitField('Search')


class UserSettingsForm(FlaskForm):
    """Enhanced user settings form."""
    
    # Notification preferences
    email_notifications = BooleanField('Email Notifications')
    sms_notifications = BooleanField('SMS Notifications')
    desktop_notifications = BooleanField('Desktop Notifications')
    
    # Privacy settings
    profile_visibility = SelectField('Profile Visibility', choices=[
        ('public', 'Public'),
        ('team_only', 'Team Only'),
        ('private', 'Private')
    ])
    
    # Display preferences
    timezone = SelectField('Timezone', choices=[
        ('UTC', 'UTC'),
        ('America/New_York', 'Eastern Time'),
        ('America/Chicago', 'Central Time'),
        ('America/Denver', 'Mountain Time'),
        ('America/Los_Angeles', 'Pacific Time'),
        ('Europe/London', 'GMT'),
        ('Europe/Paris', 'Central European Time'),
        ('Asia/Tokyo', 'Japan Time'),
        ('Asia/Shanghai', 'China Time'),
        ('Australia/Sydney', 'Australian Eastern Time')
    ])
    
    theme = SelectField('Theme', choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto')
    ])
    
    submit = SubmitField('Save Settings')


class PasswordChangeForm(FlaskForm):
    """Password change form with enhanced security."""
    
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message="Passwords must match")
    ])
    
    submit = SubmitField('Change Password')
    
    def validate_new_password(self, field):
        """Custom password validation."""
        password = field.data
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r'[0-9]', password):
            raise ValidationError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain at least one special character")
