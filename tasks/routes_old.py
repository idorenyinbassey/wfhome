from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from .forms import TaskForm
from models import Task, User
from . import tasks
from app import db
from datetime import datetime


@tasks.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """Simple dashboard for basic task management."""
    form = TaskForm()
    form.assignee.choices = [(user.id, user.username) for user in User.query.all()]
    
    if form.validate_on_submit():
        task = Task(
            title=form.task_title.data,
            description=form.task_description.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            task_type=form.task_type.data,
            user_id=current_user.id,
            assignee_id=form.assignee.data
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('tasks.dashboard'))
    
    # Get user tasks
    user_tasks = Task.query.filter(
        (Task.user_id == current_user.id) | (Task.assignee_id == current_user.id)
    ).order_by(Task.date_created.desc()).all()
    
    return render_template('dashboard.html',
                          form=form,
                          tasks=user_tasks,
                          user=current_user)


@tasks.route('/enhanced-dashboard', methods=['GET', 'POST'])
@login_required
def enhanced_dashboard():
    """Display the enhanced dashboard with all new features."""
    # Get user tasks
    user_tasks = Task.query.filter(
        (Task.user_id == current_user.id) | (Task.assignee_id == current_user.id)
    ).order_by(Task.date_created.desc()).all()
    
    # Calculate task statistics
    completed_tasks = sum(1 for task in user_tasks 
                         if task.start_time and task.end_time)
    pending_tasks = len(user_tasks) - completed_tasks
    
    # Get user files
    user_files = FileUpload.query.filter_by(user_id=current_user.id).all()
    
    # Get unread notifications
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(Notification.date_created.desc()).limit(10).all()
    
    # Get online users (simulate with recent activity)
    online_users = User.query.filter(
        User.id != current_user.id,
        User.status == UserStatus.ONLINE.value
    ).limit(10).all()
    
    # Get department users
    department_users = []
    if current_user.department:
        department_users = User.query.filter(
            User.department == current_user.department,
            User.id != current_user.id
        ).all()
    
    # Get user groups
    user_groups = UserGroup.query.filter(
        UserGroup.members.contains(current_user)).all()
    
    # Get broadcast messages (recent)
    broadcast_messages = Message.query.filter_by(
        message_type='broadcast'
    ).order_by(Message.date_created.desc()).limit(10).all()
    
    return render_template('dashboard_new.html',
                          user_tasks=user_tasks,
                          completed_tasks=completed_tasks,
                          pending_tasks=pending_tasks,
                          user_files=user_files,
                          unread_notifications=unread_notifications,
                          online_users=online_users,
                          department_users=department_users,
                          user_groups=user_groups,
                          broadcast_messages=broadcast_messages)


@tasks.route('/dashboard-selection')
@login_required
def dashboard_selection():
    """Allow users to choose between dashboard versions."""
    return render_template('dashboard_selection.html')

@tasks.route('/create-task', methods=['POST'])
@login_required
def create_task():
    """Create a new task from the dashboard modal."""
    title = request.form.get('title')
    description = request.form.get('description')
    priority = request.form.get('priority', 'medium')
    due_date = request.form.get('due_date')
    category = request.form.get('category', 'work')
    
    # Validation
    if not title:
        flash('Task title is required.', 'danger')
        return redirect(url_for('tasks.dashboard'))
    
    # Parse due date
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid due date format.', 'danger')
            return redirect(url_for('tasks.dashboard'))
    
    # Create task
    task = Task(
        title=title,
        description=description,
        priority=priority,
        due_date=parsed_due_date,
        task_type=category,
        user_id=current_user.id,
        assignee_id=current_user.id
    )
    
    db.session.add(task)
    db.session.commit()
    
    flash(f'Task "{title}" created successfully!', 'success')
    return redirect(url_for('tasks.dashboard'))

@tasks.route('/upload-file', methods=['POST'])
@login_required
def upload_file():
    """Handle file upload from dashboard."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file selected'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    # Get form data
    file_name = request.form.get('file_name') or file.filename
    description = request.form.get('description', '')
    category = request.form.get('category', 'other')
    is_private = 'is_private' in request.form
    
    # Secure filename
    filename = secure_filename(file.filename)
    
    # Check file size (16MB limit)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > 16 * 1024 * 1024:  # 16MB
        return jsonify({'success': False, 'error': 'File size exceeds 16MB limit'})
    
    # Save file
    upload_folder = os.path.join('static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    # Create database record
    file_upload = FileUpload(
        filename=file_name,
        original_filename=filename,
        file_path=f'uploads/{filename}',
        file_size=file_size,
        category=category,
        description=description,
        is_private=is_private,
        user_id=current_user.id
    )
    
    db.session.add(file_upload)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'File uploaded successfully'})

@tasks.route('/send-broadcast', methods=['POST'])
@login_required
def send_broadcast():
    """Send broadcast message."""
    content = request.form.get('content')
    priority = request.form.get('priority', 'normal')
    recipient_type = request.form.get('recipient_type', 'all')
    group_id = request.form.get('group_id')
    
    if not content:
        flash('Message content is required.', 'danger')
        return redirect(url_for('tasks.dashboard'))
    
    # Create broadcast message
    message = Message(
        content=content,
        message_type='broadcast',
        sender_id=current_user.id
    )
    
    db.session.add(message)
    db.session.commit()
    
    # Create notifications based on recipient type
    recipients = []
    if recipient_type == 'all':
        recipients = User.query.filter(User.id != current_user.id).all()
    elif recipient_type == 'department' and current_user.department:
        recipients = User.query.filter(
            User.department == current_user.department,
            User.id != current_user.id
        ).all()
    elif recipient_type == 'group' and group_id:
        group = UserGroup.query.get(group_id)
        if group and current_user in group.members:
            recipients = [user for user in group.members if user.id != current_user.id]
    
    # Create notifications
    for recipient in recipients:
        notification = Notification(
            title='New Broadcast Message',
            content=f'{current_user.username}: {content[:50]}...',
            notification_type='message',
            user_id=recipient.id,
            sender_id=current_user.id
        )
        db.session.add(notification)
    
    db.session.commit()
    
    flash('Broadcast message sent successfully!', 'success')
    return redirect(url_for('tasks.dashboard'))

@tasks.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first()
    
    if notification:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False}), 404

@tasks.route('/dashboard/refresh-users')
@login_required
def refresh_users():
    """API endpoint to refresh online users."""
    online_users = User.query.filter(
        User.id != current_user.id,
        User.status == UserStatus.ONLINE
    ).all()
    
    users_data = [{
        'id': user.id,
        'username': user.username,
        'department': user.department,
        'profile_picture': user.profile_picture
    } for user in online_users]
    
    return jsonify({'online_users': users_data})

@tasks.route('/all-notifications')
@login_required
def all_notifications():
    """View all notifications."""
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.date_created.desc()).all()
    
    return render_template('all_notifications.html', notifications=notifications)


@tasks.route('/all-tasks')
@login_required
def all_tasks():
    """View all tasks for the current user."""
    user_tasks = Task.query.filter(
        (Task.user_id == current_user.id) | (Task.assignee_id == current_user.id)
    ).order_by(Task.date_created.desc()).all()
    
    return render_template('all_tasks.html', tasks=user_tasks)

@tasks.route('/task/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Edit an existing task."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id and task.assignee_id != current_user.id:
        abort(403)  # Forbidden if the user is not the creator or assignee

    form = TaskForm(obj=task)
    form.assignee.choices = [(user.id, user.username) for user in User.query.all()]

    if form.validate_on_submit():
        task.title = form.task_title.data
        task.description = form.task_description.data
        task.priority = form.priority.data
        task.due_date = form.due_date.data
        task.start_time = form.start_time.data
        task.end_time = form.end_time.data
        task.task_type = form.task_type.data
        task.assignee_id = form.assignee.data
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks.dashboard'))

    return render_template('edit_task.html', form=form, task=task)

@tasks.route('/task/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete an existing task."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id and task.assignee_id != current_user.id:
        abort(403)  # Forbidden if the user is not the creator or assignee

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('tasks.dashboard'))

@tasks.route('/task/start/<int:task_id>', methods=['POST'])
@login_required
def start_task(task_id):
    """Start a task and record the start time."""
    task = Task.query.get_or_404(task_id)
    # Ensure only the assigned user or creator can start the task
    if task.assignee_id != current_user.id and task.user_id != current_user.id:
        flash('You do not have permission to start this task.', 'danger')
        return redirect(url_for('tasks.dashboard'))

    if not task.start_time:
        task.start_time = datetime.utcnow()  # Set the start time
        db.session.commit()
        flash('Task started.', 'success')
    else:
        flash('Task has already been started.', 'warning')
    return redirect(url_for('tasks.dashboard'))

@tasks.route('/task/complete/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    """Complete a task and record the end time."""
    task = Task.query.get_or_404(task_id)
    # Ensure only the assigned user or creator can complete the task
    if task.assignee_id != current_user.id and task.user_id != current_user.id:
        flash('You do not have permission to complete this task.', 'danger')
        return redirect(url_for('tasks.dashboard'))

    if not task.end_time:
        task.end_time = datetime.utcnow()  # Set the end time
        if hasattr(task, 'calculate_duration'):  # Ensure the method exists
            task.duration = task.calculate_duration()  # Calculate the duration
        db.session.commit()
        flash('Task completed.', 'success')
    else:
        flash('Task has already been completed.', 'warning')
    return redirect(url_for('tasks.dashboard'))

@tasks.route('/end_task/<int:task_id>', methods=['POST'])
@login_required
def end_task(task_id):
    """Mark a task as completed and set the end time."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id and task.assignee_id != current_user.id:
        abort(403)  # Forbidden if not the owner or assignee of the task

    if not task.end_time:
        task.end_time = datetime.utcnow()  # Set the end time to the current UTC time
        db.session.commit()
        flash('Task marked as completed!', 'success')
    else:
        flash('Task has already been completed.', 'warning')

    return redirect(url_for('tasks.dashboard'))