from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from .forms import TaskForm

tasks = Blueprint('tasks', __name__)

@tasks.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = TaskForm()  # Instantiate the task form
    user_tasks = []  # This will hold the tasks for the user (replace with actual retrieval from the database)

    if form.validate_on_submit():  # Check if the form was submitted and valid
        # Here you would handle the form data (e.g., save to the database)
        # task = Task(title=form.task_title.data, description=form.task_description.data, ...)
        flash('Task created successfully!', 'success')
        return redirect(url_for('tasks.dashboard'))  # Redirect to the dashboard

    # Pass the form and tasks to the template
    return render_template('dashboard.html', form=form, tasks=user_tasks)