from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_login import login_required, current_user
from functools import wraps
from models import User, Task, db
import jwt
from datetime import datetime, timedelta
import os

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(api_bp)

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key')
JWT_EXPIRATION_HOURS = 24

def token_required(f):
    """Decorator for API routes that require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return {'message': 'Token is missing'}, 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]  # Remove 'Bearer ' prefix
            
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user_id = data['user_id']
            user = User.query.get(current_user_id)
            
            if not user:
                return {'message': 'Invalid token'}, 401
                
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Token is invalid'}, 401
        
        return f(user, *args, **kwargs)
    
    return decorated

# Authentication endpoint
class AuthAPI(Resource):
    def post(self):
        """Login and get JWT token."""
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return {'message': 'Username and password required'}, 400
        
        user = User.query.filter(
            (User.username == data['username']) | 
            (User.email == data['username'])
        ).first()
        
        if not user or not user.check_password(data['password']):
            return {'message': 'Invalid credentials'}, 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        }, JWT_SECRET, algorithm='HS256')
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return {
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username,
                'is_admin': user.is_admin,
                'department': user.department
            }
        }, 200

# User API endpoints
class UserListAPI(Resource):
    @token_required
    def get(self, current_user):
        """Get all users (admin only) or team members."""
        if not current_user.is_admin:
            return {'message': 'Access denied'}, 403
        
        users = User.query.all()
        return {
            'users': [{
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username,
                'department': user.department,
                'is_admin': user.is_admin,
                'status': user.status
            } for user in users]
        }

class UserAPI(Resource):
    @token_required
    def get(self, current_user, user_id):
        """Get user details."""
        if current_user.id != user_id and not current_user.is_admin:
            return {'message': 'Access denied'}, 403
        
        user = User.query.get_or_404(user_id)
        return {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'department': user.department,
                'phone_number': user.phone_number,
                'status': user.status,
                'is_admin': user.is_admin,
                'date_created': user.date_created.isoformat(),
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
        }

# Task API endpoints
class TaskListAPI(Resource):
    @token_required
    def get(self, current_user):
        """Get user's tasks with filtering options."""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        priority = request.args.get('priority')
        
        query = Task.query.filter(
            (Task.user_id == current_user.id) | 
            (Task.assignee_id == current_user.id)
        )
        
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        
        tasks = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'tasks': [{
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'priority': task.priority,
                'task_type': task.task_type,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'creator': task.creator.username if task.creator else None,
                'assignee': task.assignee.username if task.assignee else None,
                'created_at': task.date_created.isoformat()
            } for task in tasks.items],
            'pagination': {
                'page': tasks.page,
                'pages': tasks.pages,
                'per_page': tasks.per_page,
                'total': tasks.total
            }
        }
    
    @token_required
    def post(self, current_user):
        """Create new task."""
        data = request.get_json()
        
        if not data or not data.get('title'):
            return {'message': 'Title is required'}, 400
        
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            task_type=data.get('task_type', 'individual'),
            user_id=current_user.id,
            assignee_id=data.get('assignee_id'),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None
        )
        
        db.session.add(task)
        db.session.commit()
        
        return {
            'message': 'Task created successfully',
            'task': {
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'priority': task.priority
            }
        }, 201

class TaskAPI(Resource):
    @token_required
    def get(self, current_user, task_id):
        """Get specific task details."""
        task = Task.query.get_or_404(task_id)
        
        if (task.user_id != current_user.id and 
            task.assignee_id != current_user.id and 
            not current_user.is_admin):
            return {'message': 'Access denied'}, 403
        
        return {
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'priority': task.priority,
                'task_type': task.task_type,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'start_time': task.start_time.isoformat() if task.start_time else None,
                'end_time': task.end_time.isoformat() if task.end_time else None,
                'creator': task.creator.username if task.creator else None,
                'assignee': task.assignee.username if task.assignee else None,
                'created_at': task.date_created.isoformat()
            }
        }
    
    @token_required
    def put(self, current_user, task_id):
        """Update task."""
        task = Task.query.get_or_404(task_id)
        
        if (task.user_id != current_user.id and 
            task.assignee_id != current_user.id and 
            not current_user.is_admin):
            return {'message': 'Access denied'}, 403
        
        data = request.get_json()
        
        # Update allowed fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'priority' in data:
            task.priority = data['priority']
        if 'due_date' in data:
            task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
        
        db.session.commit()
        
        return {'message': 'Task updated successfully'}, 200
    
    @token_required
    def delete(self, current_user, task_id):
        """Delete task."""
        task = Task.query.get_or_404(task_id)
        
        if (task.user_id != current_user.id and 
            not current_user.is_admin):
            return {'message': 'Access denied'}, 403
        
        db.session.delete(task)
        db.session.commit()
        
        return {'message': 'Task deleted successfully'}, 200# Dashboard stats API
class DashboardStatsAPI(Resource):
    @token_required
    def get(self, current_user):
        """Get dashboard statistics."""
        # Task statistics
        total_tasks = Task.query.filter(
            (Task.user_id == current_user.id) | 
            (Task.assignee_id == current_user.id)
        ).count()
        
        # For now, we'll just return basic stats since status field might not exist
        return {
            'stats': {
                'total_tasks': total_tasks,
                'user_id': current_user.id,
                'username': current_user.username
            }
        }

# Register API routes
api.add_resource(AuthAPI, '/auth/login')
api.add_resource(UserListAPI, '/users')
api.add_resource(UserAPI, '/users/<int:user_id>')
api.add_resource(TaskListAPI, '/tasks')
api.add_resource(TaskAPI, '/tasks/<int:task_id>')
api.add_resource(DashboardStatsAPI, '/dashboard/stats')
