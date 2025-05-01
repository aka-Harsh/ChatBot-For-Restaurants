from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import os
import json
import datetime
import secrets

# Import modules
from modules.auth import login_required, role_required, authenticate_user, register_user, initialize_users
from modules.chatbot import RestaurantChatbot
from modules.orders import (initialize_orders_csv, get_all_orders, get_user_orders, update_order_status, 
                           get_recent_orders, get_pending_orders, get_completed_orders)
from modules.sales import (get_weekly_sales, get_monthly_sales, forecast_weekly_sales, 
                          forecast_monthly_sales, get_sales_summary)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Ensure data directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('modules', exist_ok=True)
os.makedirs('static/images', exist_ok=True)
os.makedirs('templates/customer', exist_ok=True)
os.makedirs('templates/manager', exist_ok=True)

# Initialize data files
def initialize_data_files():
    # Initialize users
    initialize_users()
    
    # Initialize orders
    initialize_orders_csv()
    
    # Create menu data if it doesn't exist
    if not os.path.exists('data/menu.json'):
        create_menu_data()

def create_menu_data():
    # Menu data
    menu_data = {
        "appetizers": [
            {
                "id": "a1",
                "name": "Garlic Bread",
                "price": 4.99,
                "description": "Fresh baked Italian bread topped with garlic butter and herbs.",
                "ingredients": ["Italian bread", "Garlic butter", "Parsley", "Oregano"],
                "nutrition": {
                    "calories": 320,
                    "carbs": 40,
                    "protein": 6,
                    "fat": 15
                },
                "prepTime": "10 minutes"
            },
            {
                "id": "a2",
                "name": "Mozzarella Sticks",
                "price": 6.99,
                "description": "Golden-fried mozzarella sticks served with marinara sauce.",
                "ingredients": ["Mozzarella cheese", "Breadcrumbs", "Eggs", "Italian herbs", "Marinara sauce"],
                "nutrition": {
                    "calories": 420,
                    "carbs": 30,
                    "protein": 20,
                    "fat": 25
                },
                "prepTime": "15 minutes"
            },
            {
                "id": "a3",
                "name": "Soup of the Day",
                "price": 5.99,
                "description": "Fresh homemade soup prepared daily. Ask our chatbot for today's special!",
                "ingredients": ["Daily fresh ingredients", "Chef's selection of herbs and spices"],
                "nutrition": {
                    "calories": 220,
                    "carbs": 25,
                    "protein": 10,
                    "fat": 8
                },
                "prepTime": "20 minutes"
            },
            {
                "id": "a4",
                "name": "Bruschetta",
                "price": 7.99,
                "description": "Toasted Italian bread topped with fresh tomatoes, basil, garlic, and olive oil.",
                "ingredients": ["Italian bread", "Tomatoes", "Fresh basil", "Garlic", "Extra virgin olive oil", "Balsamic glaze"],
                "nutrition": {
                    "calories": 280,
                    "carbs": 35,
                    "protein": 5,
                    "fat": 12
                },
                "prepTime": "15 minutes"
            }
        ],
        "main_courses": [
            {
                "id": "m1",
                "name": "Margherita Pizza",
                "price": 12.99,
                "description": "Classic pizza with tomato sauce, fresh mozzarella, and basil on our house-made dough.",
                "ingredients": ["House-made dough", "San Marzano tomato sauce", "Fresh mozzarella", "Fresh basil", "Extra virgin olive oil"],
                "nutrition": {
                    "calories": 850,
                    "carbs": 90,
                    "protein": 35,
                    "fat": 35
                },
                "prepTime": "20 minutes"
            },
            {
                "id": "m2",
                "name": "Spaghetti Carbonara",
                "price": 14.99,
                "description": "Al dente spaghetti tossed with a creamy sauce of eggs, pecorino cheese, pancetta, and black pepper.",
                "ingredients": ["Spaghetti", "Eggs", "Pecorino Romano cheese", "Pancetta", "Black pepper", "Parsley"],
                "nutrition": {
                    "calories": 950,
                    "carbs": 85,
                    "protein": 40,
                    "fat": 45
                },
                "prepTime": "25 minutes"
            },
            {
                "id": "m3",
                "name": "Chicken Alfredo",
                "price": 15.99,
                "description": "Fettuccine pasta in a rich, creamy Alfredo sauce with grilled chicken breast.",
                "ingredients": ["Fettuccine pasta", "Grilled chicken breast", "Heavy cream", "Parmesan cheese", "Butter", "Garlic", "Parsley"],
                "nutrition": {
                    "calories": 1050,
                    "carbs": 80,
                    "protein": 55,
                    "fat": 50
                },
                "prepTime": "30 minutes"
            },
            {
                "id": "m4",
                "name": "Grilled Salmon",
                "price": 18.99,
                "description": "Fresh Atlantic salmon fillet, grilled and served with seasonal vegetables and lemon herb butter.",
                "ingredients": ["Atlantic salmon", "Seasonal vegetables", "Lemon", "Butter", "Fresh herbs", "Olive oil"],
                "nutrition": {
                    "calories": 620,
                    "carbs": 15,
                    "protein": 45,
                    "fat": 40
                },
                "prepTime": "25 minutes"
            },
            {
                "id": "m5",
                "name": "Vegetable Stir Fry",
                "price": 13.99,
                "description": "Colorful medley of fresh vegetables stir-fried in a savory sauce, served over steamed rice.",
                "ingredients": ["Broccoli", "Bell peppers", "Carrots", "Snap peas", "Mushrooms", "Onions", "Ginger", "Garlic", "Soy sauce", "Jasmine rice"],
                "nutrition": {
                    "calories": 450,
                    "carbs": 65,
                    "protein": 12,
                    "fat": 15
                },
                "prepTime": "20 minutes"
            }
        ],
        "desserts": [
            {
                "id": "d1",
                "name": "Tiramisu",
                "price": 6.99,
                "description": "Classic Italian dessert with layers of coffee-soaked ladyfingers and mascarpone cream.",
                "ingredients": ["Ladyfingers", "Espresso coffee", "Mascarpone cheese", "Heavy cream", "Eggs", "Sugar", "Cocoa powder"],
                "nutrition": {
                    "calories": 380,
                    "carbs": 35,
                    "protein": 7,
                    "fat": 22
                },
                "prepTime": "Prepared daily"
            },
            {
                "id": "d2",
                "name": "Chocolate Cake",
                "price": 5.99,
                "description": "Rich, moist chocolate cake with a smooth ganache topping.",
                "ingredients": ["Chocolate", "Flour", "Sugar", "Eggs", "Butter", "Vanilla extract", "Heavy cream"],
                "nutrition": {
                    "calories": 450,
                    "carbs": 50,
                    "protein": 6,
                    "fat": 25
                },
                "prepTime": "Prepared daily"
            },
            {
                "id": "d3",
                "name": "Cheesecake",
                "price": 6.99,
                "description": "Creamy New York style cheesecake with a graham cracker crust and berry compote.",
                "ingredients": ["Cream cheese", "Sugar", "Eggs", "Vanilla extract", "Graham crackers", "Butter", "Mixed berries"],
                "nutrition": {
                    "calories": 480,
                    "carbs": 40,
                    "protein": 8,
                    "fat": 30
                },
                "prepTime": "Prepared daily"
            },
            {
                "id": "d4",
                "name": "Ice Cream Sundae",
                "price": 4.99,
                "description": "Vanilla ice cream topped with chocolate sauce, whipped cream, and a cherry.",
                "ingredients": ["Vanilla ice cream", "Chocolate sauce", "Whipped cream", "Maraschino cherry", "Chopped nuts"],
                "nutrition": {
                    "calories": 350,
                    "carbs": 45,
                    "protein": 5,
                    "fat": 18
                },
                "prepTime": "5 minutes"
            }
        ],
        "drinks": [
            {
                "id": "dr1",
                "name": "Soda",
                "price": 2.49,
                "description": "Choice of Coca-Cola, Diet Coke, Sprite, or Fanta.",
                "ingredients": ["Carbonated water", "Sweeteners", "Natural flavors"],
                "nutrition": {
                    "calories": 140,
                    "carbs": 39,
                    "protein": 0,
                    "fat": 0
                },
                "prepTime": "Served immediately"
            },
            {
                "id": "dr2",
                "name": "Iced Tea",
                "price": 2.99,
                "description": "Freshly brewed unsweetened or sweet tea with lemon.",
                "ingredients": ["Black tea", "Optional: sugar", "Lemon"],
                "nutrition": {
                    "calories": 0,
                    "carbs": 0,
                    "protein": 0,
                    "fat": 0
                },
                "prepTime": "Served immediately"
            },
            {
                "id": "dr3",
                "name": "Coffee",
                "price": 3.49,
                "description": "Premium Italian coffee, available as espresso, americano, or cappuccino.",
                "ingredients": ["Freshly ground coffee beans", "Optional: milk, sugar"],
                "nutrition": {
                    "calories": 5,
                    "carbs": 0,
                    "protein": 0,
                    "fat": 0
                },
                "prepTime": "5 minutes"
            },
            {
                "id": "dr4",
                "name": "House Wine (Glass)",
                "price": 7.99,
                "description": "Selection of red or white house wines. Ask our chatbot for current offerings.",
                "ingredients": ["Grapes", "Natural fermentation"],
                "nutrition": {
                    "calories": 120,
                    "carbs": 4,
                    "protein": 0,
                    "fat": 0
                },
                "prepTime": "Served immediately"
            }
        ]
    }
    
    # Save menu as JSON
    with open('data/menu.json', 'w') as f:
        json.dump(menu_data, f, indent=4)

# Create chatbot instance
chatbot = RestaurantChatbot()

# Routes
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if session['role'] == 'customer':
        return redirect(url_for('customer_menu'))
    elif session['role'] == 'manager':
        return redirect(url_for('manager_dashboard'))
    
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = authenticate_user(username, password)
        if user:
            session['username'] = username
            session['role'] = user['role']
            
            if user['role'] == 'customer':
                return redirect(url_for('customer_menu'))
            elif user['role'] == 'manager':
                return redirect(url_for('manager_dashboard'))
        
        flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        
        success, message = register_user(username, password, name, email, phone, address)
        if success:
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        else:
            flash(message)
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Customer Routes
@app.route('/customer/menu')
@login_required
@role_required('customer')
def customer_menu():
    return render_template('customer/menu.html', username=session['username'])

@app.route('/customer/orders')
@login_required
@role_required('customer')
def customer_orders():
    # Get orders for the logged-in customer
    orders = get_user_orders(session['username'])
    return render_template('customer/orders.html', orders=orders, username=session['username'])

# Manager Routes
@app.route('/manager/dashboard')
@login_required
@role_required('manager')
def manager_dashboard():
    # Get order statistics
    sales_summary = get_sales_summary()
    recent_orders = get_recent_orders(5)
    
    return render_template('manager/dashboard.html',
                           total_orders=sales_summary['total_orders'],
                           pending_orders=sales_summary['pending_orders'],
                           completed_orders=sales_summary['completed_orders'],
                           total_revenue=sales_summary['total_revenue'],
                           recent_orders=recent_orders,
                           username=session['username'])

@app.route('/manager/orders')
@login_required
@role_required('manager')
def manager_orders():
    # Get all orders
    orders = get_all_orders()
    return render_template('manager/orders.html', orders=orders, username=session['username'])

@app.route('/manager/update_order_status', methods=['POST'])
@login_required
@role_required('manager')
def update_order_status_route():
    order_id = request.form['order_id']
    status = request.form['status']
    
    success = update_order_status(order_id, status)
    if success:
        flash('Order status updated')
    else:
        flash('Error updating order status')
        
    return redirect(url_for('manager_orders'))

@app.route('/manager/sales')
@login_required
@role_required('manager')
def manager_sales():
    # Import the get_display_data function
    from modules.sales import get_display_data, forecast_weekly_sales, forecast_monthly_sales
    
    # Get sales data, using sample data if necessary
    weeks, weekly_values, months, monthly_values = get_display_data()
    
    # Get forecasts
    weekly_forecast = forecast_weekly_sales()
    monthly_forecast = forecast_monthly_sales()
    
    # Debug output
    print(f"Weeks: {weeks}")
    print(f"Weekly values: {weekly_values}")
    print(f"Months: {months}")
    print(f"Monthly values: {monthly_values}")
    print(f"Weekly forecast: {weekly_forecast}")
    print(f"Monthly forecast: {monthly_forecast}")
    
    return render_template('manager/sales.html',
                          weeks=weeks,
                          weekly_values=weekly_values,
                          months=months,
                          monthly_values=monthly_values,
                          weekly_forecast=weekly_forecast,
                          monthly_forecast=monthly_forecast,
                          username=session['username'])

# API Routes
@app.route('/api/menu', methods=['GET'])
def api_menu():
    # Return the menu data
    try:
        with open('data/menu.json', 'r') as f:
            menu_data = json.load(f)
        return jsonify(menu_data)
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({})

@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    # Process chat message
    data = request.json
    user_message = data.get('message', '')
    
    # Process the message using the chatbot
    response = chatbot.process_message(user_message, session.get('username'))
    
    return jsonify({'response': response})

@app.route('/api/place_order', methods=['POST'])
@login_required
@role_required('customer')
def api_place_order():
    from modules.orders import place_order, get_cart
    
    # Get current cart
    cart = get_cart(session['username'])
    
    # Place the order
    order_id = place_order(session['username'], cart)
    
    if order_id:
        return jsonify({'success': True, 'order_id': order_id})
    else:
        return jsonify({'success': False, 'message': 'Error placing order'})

@app.route('/api/user_orders', methods=['GET'])
@login_required
def api_user_orders():
    # Get orders for the logged-in user
    orders = get_user_orders(session['username'])
    return jsonify({'orders': orders})

@app.route('/api/predictions', methods=['POST'])
@login_required
def api_predictions():
    # Get predictions for chat input
    data = request.json
    partial_input = data.get('input', '')
    
    predictions = chatbot.get_predictions(partial_input)
    return jsonify({'predictions': predictions})

# Initialize everything when the app starts
initialize_data_files()

if __name__ == '__main__':
    app.run(debug=True)