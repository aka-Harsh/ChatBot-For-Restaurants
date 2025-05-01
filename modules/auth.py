import csv
import datetime
from functools import wraps
from flask import session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

# Authentication functions for the restaurant application

def login_required(f):
    """Decorator to ensure user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    """Decorator to ensure user has the required role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def authenticate_user(username, password):
    """Authenticate a user with username and password"""
    with open('data/users.csv', 'r') as file:
        reader = csv.DictReader(file)
        for user in reader:
            if user['username'] == username and check_password_hash(user['password'], password):
                return user
    return None

def register_user(username, password, name, email, phone, address):
    """Register a new user"""
    # Check if username already exists
    with open('data/users.csv', 'r') as file:
        reader = csv.DictReader(file)
        for user in reader:
            if user['username'] == username:
                return False, "Username already exists"
    
    # Add new user
    with open('data/users.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            username, 
            generate_password_hash(password), 
            'customer',  # Default role is customer
            name,
            email,
            phone,
            address,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
    
    return True, "Registration successful"

def get_user_info(username):
    """Get user information by username"""
    with open('data/users.csv', 'r') as file:
        reader = csv.DictReader(file)
        for user in reader:
            if user['username'] == username:
                return user
    return None

def initialize_users():
    """Initialize the users.csv file with sample users if it doesn't exist"""
    try:
        with open('data/users.csv', 'x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'password', 'role', 'name', 'email', 'phone', 'address', 'registration_date'])
            # Add sample users
            writer.writerow(['customer', generate_password_hash('123'), 'customer', 'Sample Customer', 
                          'customer@example.com', '555-1234', '123 Main St', 
                          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow(['manager', generate_password_hash('123'), 'manager', 'Sample Manager', 
                          'manager@example.com', '555-5678', '456 Oak St', 
                          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            return True
    except FileExistsError:
        return False