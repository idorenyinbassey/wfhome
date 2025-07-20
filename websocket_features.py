from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
from functools import wraps
from models import User, Task, Notification, db
from datetime import datetime

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*")

# Store active users and their rooms
active_users = {}

def authenticated_only(f):
    """Decorator to ensure user is authenticated for socket events."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        return f(*args, **kwargs)
    return wrapped

# Connection handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    if current_user.is_authenticated:
        # Join user's personal room
        join_room(f"user_{current_user.id}")
        
        # Update user status
        active_users[current_user.id] = {
            'username': current_user.username,
            'status': 'online',
            'room': f"user_{current_user.id}"
        }
        
        # Broadcast user online status to team members
        broadcast_user_status(current_user.id, 'online')
        
        emit('connected', {
            'message': 'Connected successfully',
            'user_id': current_user.id
        })
        
        # Send unread notifications
        send_unread_notifications(current_user.id)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    if current_user.is_authenticated:
        # Remove from active users
        if current_user.id in active_users:
            del active_users[current_user.id]
        
        # Leave user's room
        leave_room(f"user_{current_user.id}")
        
        # Broadcast user offline status
        broadcast_user_status(current_user.id, 'offline')

# Task-related events
@socketio.on('join_task_room')
@authenticated_only
def handle_join_task_room(data):
    """Join a task-specific room for real-time updates."""
    task_id = data.get('task_id')
    if not task_id:
        emit('error', {'message': 'Task ID required'})
        return
    
    task = Task.query.get(task_id)
    if not task:
        emit('error', {'message': 'Task not found'})
        return
    
    # Check if user has access to this task
    if (task.creator_id != current_user.id and 
        task.assignee_id != current_user.id and 
        not current_user.is_manager()):
        emit('error', {'message': 'Access denied'})
        return
    
    room = f"task_{task_id}"
    join_room(room)
    emit('joined_task_room', {'task_id': task_id, 'room': room})

@socketio.on('leave_task_room')
@authenticated_only
def handle_leave_task_room(data):
    """Leave a task-specific room."""
    task_id = data.get('task_id')
    if task_id:
        room = f"task_{task_id}"
        leave_room(room)
        emit('left_task_room', {'task_id': task_id})

@socketio.on('task_status_update')
@authenticated_only
def handle_task_status_update(data):
    """Handle real-time task status updates."""
    task_id = data.get('task_id')
    new_status = data.get('status')
    
    if not task_id or not new_status:
        emit('error', {'message': 'Task ID and status required'})
        return
    
    task = Task.query.get(task_id)
    if not task:
        emit('error', {'message': 'Task not found'})
        return
    
    # Check permissions
    if (task.creator_id != current_user.id and 
        task.assignee_id != current_user.id and 
        not current_user.is_manager()):
        emit('error', {'message': 'Access denied'})
        return
    
    # Update task status
    old_status = task.status
    task.status = new_status
    task.updated_at = datetime.utcnow()
    
    if new_status == 'completed':
        task.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    # Broadcast update to task room
    socketio.emit('task_updated', {
        'task_id': task_id,
        'old_status': old_status,
        'new_status': new_status,
        'updated_by': current_user.username,
        'updated_at': task.updated_at.isoformat()
    }, room=f"task_{task_id}")
    
    # Send notifications to relevant users
    send_task_notification(task, 'status_changed', {
        'old_status': old_status,
        'new_status': new_status,
        'updated_by': current_user.username
    })

@socketio.on('start_timer')
@authenticated_only
def handle_start_timer(data):
    """Handle task timer start."""
    task_id = data.get('task_id')
    
    task = Task.query.get(task_id)
    if not task:
        emit('error', {'message': 'Task not found'})
        return
    
    if (task.assignee_id != current_user.id and 
        task.creator_id != current_user.id):
        emit('error', {'message': 'Access denied'})
        return
    
    if task.start_time:
        emit('error', {'message': 'Timer already started'})
        return
    
    task.start_time = datetime.utcnow()
    task.status = 'in_progress'
    db.session.commit()
    
    # Broadcast timer start
    socketio.emit('timer_started', {
        'task_id': task_id,
        'start_time': task.start_time.isoformat(),
        'started_by': current_user.username
    }, room=f"task_{task_id}")

@socketio.on('stop_timer')
@authenticated_only
def handle_stop_timer(data):
    """Handle task timer stop."""
    task_id = data.get('task_id')
    
    task = Task.query.get(task_id)
    if not task:
        emit('error', {'message': 'Task not found'})
        return
    
    if (task.assignee_id != current_user.id and 
        task.creator_id != current_user.id):
        emit('error', {'message': 'Access denied'})
        return
    
    if not task.start_time:
        emit('error', {'message': 'Timer not started'})
        return
    
    task.end_time = datetime.utcnow()
    if task.status == 'in_progress':
        task.status = 'completed'
        task.completed_at = datetime.utcnow()
    
    # Calculate actual hours
    duration = task.end_time - task.start_time
    task.actual_hours = int(duration.total_seconds() / 3600)
    
    db.session.commit()
    
    # Broadcast timer stop
    socketio.emit('timer_stopped', {
        'task_id': task_id,
        'end_time': task.end_time.isoformat(),
        'duration': str(duration),
        'actual_hours': task.actual_hours,
        'stopped_by': current_user.username
    }, room=f"task_{task_id}")

# Notification events
@socketio.on('mark_notification_read')
@authenticated_only
def handle_mark_notification_read(data):
    """Mark notification as read."""
    notification_id = data.get('notification_id')
    
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first()
    
    if not notification:
        emit('error', {'message': 'Notification not found'})
        return
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.session.commit()
    
    emit('notification_marked_read', {'notification_id': notification_id})

@socketio.on('get_active_users')
@authenticated_only
def handle_get_active_users():
    """Get list of currently active users."""
    emit('active_users', {'users': list(active_users.values())})

# Helper functions
def broadcast_user_status(user_id, status):
    """Broadcast user status change to team members."""
    user = User.query.get(user_id)
    if not user:
        return
    
    # Get user's team members
    team_members = []
    for team in user.teams:
        for member in team.members:
            if member.id != user_id:
                team_members.append(member.id)
    
    # Broadcast to team members
    for member_id in set(team_members):
        socketio.emit('user_status_changed', {
            'user_id': user_id,
            'username': user.username,
            'status': status
        }, room=f"user_{member_id}")

def send_unread_notifications(user_id):
    """Send unread notifications to user."""
    notifications = Notification.query.filter_by(
        user_id=user_id,
        is_read=False
    ).limit(10).all()
    
    for notification in notifications:
        socketio.emit('new_notification', {
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.type,
            'created_at': notification.created_at.isoformat(),
            'task_id': notification.task_id,
            'project_id': notification.project_id
        }, room=f"user_{user_id}")

def send_task_notification(task, notification_type, additional_data=None):
    """Send task-related notifications."""
    users_to_notify = []
    
    # Add creator and assignee
    if task.creator_id:
        users_to_notify.append(task.creator_id)
    if task.assignee_id and task.assignee_id != task.creator_id:
        users_to_notify.append(task.assignee_id)
    
    # Add team members if it's a team task
    if task.team:
        for member in task.team.members:
            if member.id not in users_to_notify:
                users_to_notify.append(member.id)
    
    # Create and send notifications
    for user_id in users_to_notify:
        if user_id == current_user.id:
            continue  # Don't notify the person who made the change
        
        notification = Notification(
            user_id=user_id,
            title=f"Task Update: {task.title}",
            message=f"Task '{task.title}' has been updated",
            type=notification_type,
            task_id=task.id
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # Send real-time notification
        notification_data = {
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.type,
            'created_at': notification.created_at.isoformat(),
            'task_id': task.id
        }
        
        if additional_data:
            notification_data.update(additional_data)
        
        socketio.emit('new_notification', notification_data, room=f"user_{user_id}")

def create_task_comment_notification(task_id, comment):
    """Create notification for task comment."""
    task = Task.query.get(task_id)
    if not task:
        return
    
    users_to_notify = []
    if task.creator_id != current_user.id:
        users_to_notify.append(task.creator_id)
    if task.assignee_id and task.assignee_id != current_user.id:
        users_to_notify.append(task.assignee_id)
    
    for user_id in set(users_to_notify):
        notification = Notification(
            user_id=user_id,
            title=f"New comment on: {task.title}",
            message=f"{current_user.username} commented on task '{task.title}'",
            type='task_comment',
            task_id=task.id
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # Send real-time notification
        socketio.emit('new_notification', {
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.type,
            'created_at': notification.created_at.isoformat(),
            'task_id': task.id,
            'comment': comment
        }, room=f"user_{user_id}")
