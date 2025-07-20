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
    form.assignee.choices = [(user.id, user.username) 
                            for user in User.query.all()]
    
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
        (Task.user_id == current_user.id) | 
        (Task.assignee_id == current_user.id)
    ).order_by(Task.date_created.desc()).all()
    
    return render_template('dashboard.html',
                          form=form,
                          tasks=user_tasks,
                          user=current_user)


@tasks.route('/task/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Edit an existing task."""
    task = Task.query.get_or_404(task_id)
    if (task.user_id != current_user.id and 
        task.assignee_id != current_user.id):
        abort(403)

    form = TaskForm(obj=task)
    form.assignee.choices = [(user.id, user.username) 
                            for user in User.query.all()]

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
    if (task.user_id != current_user.id and 
        task.assignee_id != current_user.id):
        abort(403)

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('tasks.dashboard'))


@tasks.route('/end_task/<int:task_id>', methods=['POST'])
@login_required
def end_task(task_id):
    """Mark a task as completed and set the end time."""
    task = Task.query.get_or_404(task_id)
    if (task.user_id != current_user.id and 
        task.assignee_id != current_user.id):
        abort(403)

    if not task.end_time:
        task.end_time = datetime.utcnow()
        db.session.commit()
        flash('Task marked as completed!', 'success')
    else:
        flash('Task has already been completed.', 'warning')

    return redirect(url_for('tasks.dashboard'))
