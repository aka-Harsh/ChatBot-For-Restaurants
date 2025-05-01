import csv
import json
import datetime
import os
import random
import traceback

# User carts stored in memory (would be a database in production)
user_carts = {}

def initialize_orders_csv():
    """Initialize the orders CSV file if it doesn't exist"""
    if not os.path.exists('data/orders.csv'):
        with open('data/orders.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['order_id', 'username', 'date_time', 'items', 'special_instructions', 'total_price', 'status'])
        return True
    return False

def generate_order_id():
    """Generate a unique order ID"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices('0123456789', k=4))
    return f"ORD-{timestamp}-{random_suffix}"

def add_to_cart(username, item, quantity=1, special_instructions=''):
    """Add an item to a user's cart"""
    if username not in user_carts:
        user_carts[username] = {
            'items': [],
            'total_price': 0.0,
            'special_instructions': ''
        }
    
    # Add the item
    for _ in range(quantity):
        user_carts[username]['items'].append({
            'id': item.get('id', 'unknown'),
            'name': item.get('name', 'Unknown Item'),
            'price': float(item.get('price', 0)),
            'special_instructions': special_instructions
        })
        user_carts[username]['total_price'] += float(item.get('price', 0))
    
    # Add special instructions if provided
    if special_instructions:
        if user_carts[username]['special_instructions']:
            user_carts[username]['special_instructions'] += "; " + special_instructions
        else:
            user_carts[username]['special_instructions'] = special_instructions
    
    return True

def get_cart(username):
    """Get a user's current cart"""
    if username not in user_carts:
        user_carts[username] = {
            'items': [],
            'total_price': 0.0,
            'special_instructions': ''
        }
    
    return user_carts[username]

def clear_cart(username):
    """Clear a user's cart"""
    user_carts[username] = {
        'items': [],
        'total_price': 0.0,
        'special_instructions': ''
    }
    return True

def place_order(username, cart=None):
    """Place an order from a user's cart"""
    initialize_orders_csv()
    
    # If cart is not provided, use the user's current cart
    if cart is None:
        cart = get_cart(username)
    
    # Don't place empty orders
    if not cart['items']:
        return None
    
    # Generate order ID
    order_id = generate_order_id()
    
    # Save to CSV
    try:
        with open('data/orders.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                order_id,
                username,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                json.dumps(cart['items']),
                cart['special_instructions'],
                cart['total_price'],
                'pending'  # Default status
            ])
        
        # Clear the cart after successful order
        clear_cart(username)
        return order_id
    
    except Exception as e:
        print(f"Error placing order: {e}")
        traceback.print_exc()
        return None

def get_all_orders():
    """Get all orders from the CSV file"""
    initialize_orders_csv()
    
    orders = []
    try:
        with open('data/orders.csv', 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Debug print
                    print(f"Processing order row: {row['order_id']}")
                    
                    # Check if items is a string and parse it
                    if 'items' in row and isinstance(row['items'], str):
                        try:
                            row['items'] = json.loads(row['items'])
                            print(f"Successfully parsed items for order {row['order_id']}: {row['items'][:50]}...")
                        except json.JSONDecodeError:
                            print(f"JSON decode error for items in order {row['order_id']}: {row['items'][:50]}...")
                            row['items'] = []
                    else:
                        print(f"Items not found or not a string in order {row['order_id']}")
                        row['items'] = []
                    
                    # Make sure items is a list
                    if not isinstance(row['items'], list):
                        print(f"Items is not a list in order {row['order_id']}, type: {type(row['items'])}")
                        row['items'] = []
                    
                    # Convert total_price to float
                    try:
                        row['total_price'] = float(row['total_price'])
                    except (ValueError, TypeError):
                        row['total_price'] = 0.0
                    
                    orders.append(row)
                except Exception as e:
                    print(f"Error processing order row: {e}")
                    traceback.print_exc()
                    # Skip this row and continue
                    continue
    except Exception as e:
        print(f"Error reading orders CSV: {e}")
        traceback.print_exc()
        return []
    
    # Sort by date, newest first
    orders.sort(key=lambda x: x['date_time'], reverse=True)
    
    return orders

def get_user_orders(username):
    """Get all orders for a specific user"""
    all_orders = get_all_orders()
    return [order for order in all_orders if order['username'] == username]

def get_order_by_id(order_id):
    """Get an order by its ID"""
    all_orders = get_all_orders()
    for order in all_orders:
        if order['order_id'] == order_id:
            return order
    return None

def cancel_order(order_id):
    """Cancel an order by ID"""
    order = get_order_by_id(order_id)
    if order and order['status'] == 'pending':
        update_order_status(order_id, 'cancelled')
        return True
    return False

def update_order_status(order_id, status):
    """Update the status of an order"""
    initialize_orders_csv()
    
    # Read all orders
    all_orders = []
    try:
        with open('data/orders.csv', 'r') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            for order in reader:
                # Update the status if this is the target order
                if order['order_id'] == order_id:
                    order['status'] = status
                all_orders.append(order)
    except Exception as e:
        print(f"Error reading orders for status update: {e}")
        traceback.print_exc()
        return False
    
    # Write back all orders
    try:
        with open('data/orders.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_orders)
        return True
    except Exception as e:
        print(f"Error writing orders back after status update: {e}")
        traceback.print_exc()
        return False

def get_pending_orders():
    """Get all pending orders"""
    all_orders = get_all_orders()
    return [order for order in all_orders if order['status'] == 'pending']

def get_completed_orders():
    """Get all completed orders"""
    all_orders = get_all_orders()
    return [order for order in all_orders if order['status'] == 'completed']

def get_recent_orders(limit=5):
    """Get most recent orders"""
    all_orders = get_all_orders()
    return all_orders[:limit] if all_orders else []

def ensure_order_items_are_list(order):
    """Ensure order items are a list"""
    if not order:
        return {'order_id': '', 'username': '', 'date_time': '', 'items': [], 
                'special_instructions': '', 'total_price': 0, 'status': 'pending'}
    
    # Make sure items is a list
    if not isinstance(order.get('items', []), list):
        try:
            if isinstance(order['items'], str):
                order['items'] = json.loads(order['items'])
            else:
                order['items'] = []
        except (json.JSONDecodeError, KeyError, TypeError):
            order['items'] = []
    
    # Ensure total_price is a float
    try:
        order['total_price'] = float(order.get('total_price', 0))
    except (ValueError, TypeError):
        order['total_price'] = 0.0
    
    return order

def recreate_orders_csv():
    """Recreate the orders CSV file while fixing item formats"""
    if not os.path.exists('data/orders.csv'):
        initialize_orders_csv()
        return
    
    # Read all orders
    try:
        orders = []
        with open('data/orders.csv', 'r') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            for order in reader:
                # Try to parse items if they're a string
                if 'items' in order and isinstance(order['items'], str):
                    try:
                        items = json.loads(order['items'])
                        # Re-encode to ensure proper formatting
                        order['items'] = json.dumps(items)
                    except (json.JSONDecodeError, TypeError):
                        # If parsing fails, create a placeholder
                        order['items'] = json.dumps([{"name": "Unknown Item", "price": 0.0}])
                else:
                    order['items'] = json.dumps([{"name": "Unknown Item", "price": 0.0}])
                
                orders.append(order)
        
        # Write back all orders with fixed formats
        with open('data/orders.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(orders)
        
        print("Orders CSV recreated with fixed item formats")
        return True
    
    except Exception as e:
        print(f"Error recreating orders CSV: {e}")
        traceback.print_exc()
        return False