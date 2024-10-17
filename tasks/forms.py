from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired

class TaskForm(FlaskForm):
    task_title = StringField('Task Title', validators=[DataRequired()])
    task_description = TextAreaField('Task Description')
    task_type = SelectField('Task Type', choices=[('individual', 'Individual'), ('group', 'Group')], validators=[DataRequired()])
    submit = SubmitField('Create Task')