import os
import csv
import json
import datetime
import random

# Function to get all orders from the CSV file
def get_all_orders():
    """Get all orders for sales analysis"""
    if not os.path.exists('data/orders.csv'):
        return []
    
    try:
        orders = []
        with open('data/orders.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Ensure total_price is a float
                try:
                    row['total_price'] = float(row['total_price'])
                except (ValueError, TypeError):
                    row['total_price'] = 0.0
                    
                # Parse date_time
                row['date_time'] = row['date_time']
                
                orders.append(row)
                
        return orders
    except Exception as e:
        print(f"Error getting orders: {e}")
        return []

def get_weekly_sales():
    """Get weekly sales data for charts"""
    orders = get_all_orders()
    if not orders:
        return [], []
    
    # Group orders by week
    weekly_data = {}
    
    for order in orders:
        try:
            # Parse the date
            date_obj = datetime.datetime.strptime(order['date_time'], "%Y-%m-%d %H:%M:%S")
            week_num = date_obj.isocalendar()[1]  # Week number
            year = date_obj.year
            
            # Create a unique key for this week
            week_key = f"{year}-W{week_num}"
            
            # Add to the weekly totals
            if week_key not in weekly_data:
                weekly_data[week_key] = 0
                
            weekly_data[week_key] += order['total_price']
        except (ValueError, TypeError, KeyError):
            # Skip this order if we can't parse the date
            continue
    
    # Sort weeks chronologically
    sorted_weeks = sorted(weekly_data.keys())
    
    # Get the last 5 weeks only
    recent_weeks = sorted_weeks[-5:] if len(sorted_weeks) > 5 else sorted_weeks
    
    # Create labels and values
    weeks = [f"Week {wk.split('-W')[1]}" for wk in recent_weeks]
    values = [weekly_data[wk] for wk in recent_weeks]
    
    return weeks, values

def get_monthly_sales():
    """Get monthly sales data for charts"""
    orders = get_all_orders()
    if not orders:
        return [], []
    
    # Group orders by month
    monthly_data = {}
    
    for order in orders:
        try:
            # Parse the date
            date_obj = datetime.datetime.strptime(order['date_time'], "%Y-%m-%d %H:%M:%S")
            month = date_obj.month
            year = date_obj.year
            
            # Create a unique key for this month
            month_key = f"{year}-{month}"
            
            # Add to the monthly totals
            if month_key not in monthly_data:
                monthly_data[month_key] = 0
                
            monthly_data[month_key] += order['total_price']
        except (ValueError, TypeError, KeyError):
            # Skip this order if we can't parse the date
            continue
    
    # Sort months chronologically
    sorted_months = sorted(monthly_data.keys())
    
    # Get the last 6 months only
    recent_months = sorted_months[-6:] if len(sorted_months) > 6 else sorted_months
    
    # Create labels and values
    months = recent_months
    values = [monthly_data[m] for m in recent_months]
    
    return months, values

def forecast_weekly_sales():
    """Generate weekly sales forecast"""
    _, values = get_weekly_sales()
    
    if not values:
        # If no sales data, create sample data for demonstration
        return 250.00 + random.uniform(-50, 50)
    
    if len(values) < 3:
        # If we don't have enough data for a good average,
        # use what we have or a minimum value
        avg = sum(values) / len(values) if values else 200
        return avg * 1.1  # 10% growth
        
    # Use last 3 weeks for projection
    last_3_weeks_avg = sum(values[-3:]) / 3
    
    # Add a growth factor and some randomness
    forecast = last_3_weeks_avg * 1.12 + random.uniform(-20, 20)
    
    return forecast

def forecast_monthly_sales():
    """Generate monthly sales forecast"""
    _, values = get_monthly_sales()
    
    if not values:
        # If no sales data, create sample data for demonstration
        return 1000.00 + random.uniform(-100, 100)
    
    if len(values) < 3:
        # If we don't have enough data for a good average,
        # use what we have or a minimum value
        avg = sum(values) / len(values) if values else 800
        return avg * 1.05  # 5% growth
        
    # Use last 3 months for projection
    last_3_months_avg = sum(values[-3:]) / 3
    
    # Add a growth factor and some randomness
    forecast = last_3_months_avg * 1.07 + random.uniform(-50, 50)
    
    return forecast

def get_sales_summary():
    """Get a summary of sales data"""
    orders = get_all_orders()
    
    if not orders:
        # If no orders, return sample data
        return {
            'total_orders': 0,
            'total_revenue': 0,
            'avg_order_value': 0,
            'pending_orders': 0,
            'completed_orders': 0
        }
    
    # Calculate real summary
    total_orders = len(orders)
    total_revenue = sum(order['total_price'] for order in orders)
    avg_order_value = total_revenue / total_orders if total_orders else 0
    pending_orders = sum(1 for order in orders if order.get('status') == 'pending')
    completed_orders = sum(1 for order in orders if order.get('status') == 'completed')
    
    summary = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders
    }
    
    return summary

# Function to generate sample data for demonstration purposes
def generate_sample_data():
    """Generate sample sales data if no real data exists"""
    # Get current data
    weeks, weekly_values = get_weekly_sales()
    months, monthly_values = get_monthly_sales()
    
    # If we have real data, don't generate samples
    if weeks and monthly_values:
        return
    
    # Generate sample weeks
    current_date = datetime.datetime.now()
    sample_weeks = []
    sample_week_values = []
    
    for i in range(5):
        # Go back i weeks
        week_date = current_date - datetime.timedelta(weeks=i)
        week_num = week_date.isocalendar()[1]
        sample_weeks.insert(0, f"Week {week_num}")
        
        # Generate a random sales value
        value = 150 + random.uniform(50, 200)
        sample_week_values.insert(0, value)
    
    # Generate sample months
    sample_months = []
    sample_month_values = []
    
    for i in range(6):
        # Go back i months
        month_date = current_date - datetime.timedelta(days=30*i)
        month_str = f"{month_date.year}-{month_date.month}"
        sample_months.insert(0, month_str)
        
        # Generate a random sales value
        value = 600 + random.uniform(200, 600)
        sample_month_values.insert(0, value)
    
    return sample_weeks, sample_week_values, sample_months, sample_month_values

# Helper function to ensure we always have data to display
def get_display_data():
    """Get data for display, using sample data if necessary"""
    weeks, weekly_values = get_weekly_sales()
    months, monthly_values = get_monthly_sales()
    
    if not weeks or not monthly_values:
        # Generate sample data
        sample_data = generate_sample_data()
        if sample_data:
            sample_weeks, sample_week_values, sample_months, sample_month_values = sample_data
            
            # Use sample data if real data is missing
            if not weeks:
                weeks = sample_weeks
                weekly_values = sample_week_values
                
            if not monthly_values:
                months = sample_months
                monthly_values = sample_month_values
    
    return weeks, weekly_values, months, monthly_values