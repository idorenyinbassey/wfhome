from flask import Blueprint, render_template

auth = Blueprint('auth', __name__)

# Define the route for the landing page
@auth.route('/')
def landing_page():
    return render_template('index.html')  # Assuming 'index.html' is your landing page template

# Import other routes after defining the landing page route
from . import routes  # Keep this if you have more routes defined in another file