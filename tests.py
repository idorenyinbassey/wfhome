#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Basic tests for WFHome application
"""

import pytest
import tempfile
import os
from app import create_app, db
from models import User, Task


class TestConfig:
    """Test configuration class"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file for the test database
    app = create_app()
    app.config.from_object(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


def test_app_creation(app):
    """Test that the app was created successfully."""
    assert app is not None
    assert app.config['TESTING'] is True


def test_index_route(client):
    """Test the index route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'WFHome' in response.data or b'wfhome' in response.data.lower()


def test_login_page(client):
    """Test the login page loads."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'login' in response.data.lower()


def test_register_page(client):
    """Test the register page loads."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'register' in response.data.lower()


def test_dashboard_redirect_when_not_logged_in(client):
    """Test that dashboard redirects to login when not authenticated."""
    response = client.get('/dashboard')
    assert response.status_code == 302  # Redirect to login


def test_user_model():
    """Test user model creation."""
    user = User(
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User'
    )
    user.set_password('password123')
    
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.check_password('password123')
    assert not user.check_password('wrongpassword')


def test_task_model():
    """Test task model creation."""
    task = Task(
        title='Test Task',
        description='This is a test task',
        priority='high',
        user_id=1
    )
    
    assert task.title == 'Test Task'
    assert task.description == 'This is a test task'
    assert task.priority == 'high'
    assert task.user_id == 1


if __name__ == '__main__':
    pytest.main([__file__])
