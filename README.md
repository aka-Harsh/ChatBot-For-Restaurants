# 🍽️ Restaurant Chatbot FullStack Project

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![Status](https://img.shields.io/badge/status-active-green.svg)

An interactive restaurant management system with an intelligent chatbot that helps customers browse the menu, place orders, and provides personalized recommendations. The system includes separate interfaces for customers and managers, complete with authentication, order tracking, and sales analytics.

## ✨ Features

- **Intelligent Chatbot**: NLP-powered assistant that understands natural language, handles typos, and offers contextual suggestions
- **Interactive Menu**: Visual menu with detailed item cards showing ingredients, nutrition facts, and preparation time
- **Food Recommendations**: Recommendations on food is provided based on user selections, mood, and weather.
- **Dual Interfaces**: Separate views for customers (ordering) and managers (administration)
- **Order Management**: Place orders through natural conversation with special instructions support
- **Sales Analytics**: Charts and forecasts for weekly and monthly sales data
- **Role-Based Access**: Secure authentication system with customer and manager accounts
- **Responsive Design**: Modern UI that works on desktop and mobile devices

---

## 🛠️ Prerequisites

- Python 3.8 or higher
- Flask web framework
- Modern web browser

---

## 🚀 Getting Started

Follow these steps to deploy the project on your local system:

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/restaurant-chatbot.git
cd restaurant-chatbot
```

### 2. Set Up Python Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# For Windows:
venv\Scripts\activate
# For macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install flask pandas numpy werkzeug
```

### 3. Run the Application

```bash
python app.py
```

### 4. Access the Application

Open your web browser and navigate to: http://localhost:5000

### 5. Login Credentials

Use these credentials to test the system:
- **Customer**: username: `customer`, password: `123`
- **Manager**: username: `manager`, password: `123`

---

## 💡 Usage Guide

### Customer Interface

1. **Browse Menu**: Scroll through categorized food items
2. **View Details**: Click on any menu item to see detailed information
3. **Chat to Order**: Use natural language to interact with the chatbot
   - "I'd like to order a Margherita Pizza"
   - "Can I get a coffee please?"
   - "What would you recommend for a hot day?"
4. **Add Instructions**: Specify special requests
   - "I want a pizza without cheese"
   - "Can I get extra sauce on that?"
5. **Complete Order**: Ask the chatbot to place your order or use the checkout button
6. **View History**: Check your order history and status

### Manager Interface

1. **Dashboard**: View key statistics about orders and revenue
2. **Manage Orders**: Update order status from pending to completed
3. **Sales Analytics**: View sales charts and forecasts for business planning

---

## 🧠 Chatbot Capabilities

The chatbot understands various types of requests:

- **Menu Inquiries**: "What's on the menu?", "Tell me about the desserts"
- **Recommendations**: "What's popular?", "What goes well with wine?"
- **Contextual Suggestions**: 
  - Mood-based: "I'm in a good mood, what should I try?"
  - Weather-based: "It's hot today, what's refreshing?"
- **Order Placement**: "I'd like to order a Margherita Pizza"
- **Special Instructions**: "No cheese", "Extra sauce"
- **Order Management**: "Cancel my order", "What's in my cart?"

The system also handles typos and synonyms intelligently.

---

## 🔭 Project Outlook
