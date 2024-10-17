from flask import Blueprint

tasks = Blueprint('tasks', __name__)

from . import routes  # This should import your routes to register them with the blueprint