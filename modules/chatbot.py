import json
import os
import re
import random
import difflib
import traceback
from .orders import add_to_cart, get_cart, clear_cart, place_order, get_order_by_id, get_user_orders, cancel_order

# NLP prediction phrases
PREDICTION_PHRASES = [
    "What's on the menu?",
    "I'd like to order a pizza",
    "Do you have vegetarian options?",
    "Can I get a glass of wine?",
    "What are your appetizers?",
    "How much is the margherita pizza?",
    "What are your hours?",
    "Tell me about the soup of the day",
    "I'd like a coffee please",
    "Is the pasta spicy?",
    "Can I get my pizza without cheese?",
    "What desserts do you have?",
    "I want to cancel my order",
    "What wine do you recommend with salmon?",
    "Can you suggest something light?",
    "What's your specialty?",
    "I'm very hungry, what do you recommend?",
    "It's hot today, what's refreshing?",
    "I'm in a good mood, what should I try?",
    "What's popular here?",
    "Yes, I'd like that",
    "No, thank you"
]

# Menu synonyms and fuzzy matching
MENU_SYNONYMS = {
    "coffee": ["coffee", "cofee", "cafe", "caffeine", "espresso", "cappuccino", "americano"],
    "pizza": ["pizza", "piza", "pizzas", "pie"],
    "spaghetti": ["spaghetti", "pasta", "noodles", "spagetti"],
    "wine": ["wine", "vino", "red wine", "white wine", "rose", "champagne"],
    "garlic bread": ["garlic bread", "garlicbread", "garlic"],
    "soda": ["soda", "coke", "pepsi", "soft drink", "pop", "cola"],
    "dessert": ["dessert", "sweet", "cake", "ice cream", "tiramisu"],
    "salad": ["salad", "salads", "greens", "vegetable plate"],
}

# Mood-based food suggestions
MOOD_SUGGESTIONS = {
    "happy": ["Our Margherita Pizza is a crowd-pleaser and sure to match your good mood!",
              "I'd recommend our Tiramisu for a perfect mood-lifting treat!",
              "How about celebrating with a glass of our House Wine?"],
    "sad": ["Our Chocolate Cake is the perfect comfort food to brighten your day.",
            "A warm bowl of our Soup of the Day might help you feel better.",
            "Our Spaghetti Carbonara is rich and comforting - perfect for lifting spirits."],
    "tired": ["Our Coffee will give you the energy boost you need!",
              "Try our Grilled Salmon - it's packed with nutrients to fight fatigue.",
              "A refreshing Iced Tea might help you feel more alert."],
    "hungry": ["Our Chicken Alfredo is filling and satisfying for a hearty appetite.",
               "The Margherita Pizza with added toppings would be perfect when you're really hungry!",
               "I'd suggest starting with Mozzarella Sticks and then having our Grilled Salmon as a main."],
    "hot": ["Our Iced Tea is perfectly refreshing on a hot day.",
            "Try our Ice Cream Sundae to cool down!",
            "A light Vegetable Stir Fry would be perfect in hot weather."],
    "cold": ["Our Soup of the Day will warm you right up!",
             "A hot Coffee or Cappuccino would be perfect to fight the cold.",
             "Our Spaghetti Carbonara is a warming, comforting dish for cold days."],
}

# Weather-based food suggestions
WEATHER_SUGGESTIONS = {
    "hot": ["Our Iced Tea is perfectly refreshing when it's hot outside.",
            "I'd recommend our Ice Cream Sundae - perfect for cooling down!",
            "A light Vegetable Stir Fry won't weigh you down in hot weather."],
    "cold": ["Our Soup of the Day is perfect for warming up!",
             "A hot Coffee would be lovely in cold weather.",
             "Our hearty Spaghetti Carbonara will warm you from the inside."],
    "rainy": ["Nothing beats our Soup of the Day on a rainy day.",
              "Our Tiramisu pairs perfectly with Coffee for a rainy day treat.",
              "The comforting Chicken Alfredo is popular during rainy weather."],
    "sunny": ["Our House Wine enjoyed outdoors is perfect on a sunny day!",
              "Try our refreshing Iced Tea when it's sunny and warm.",
              "Our Bruschetta makes for a light, fresh appetizer that's perfect for sunny days."],
}

# Recommendations based on items
ITEM_RECOMMENDATIONS = {
    # Appetizers
    "Garlic Bread": ["Margherita Pizza", "Spaghetti Carbonara", "House Wine (Glass)"],
    "Mozzarella Sticks": ["Margherita Pizza", "Soda", "Chicken Alfredo"],
    "Soup of the Day": ["Grilled Salmon", "Garlic Bread", "Iced Tea"],
    "Bruschetta": ["Vegetable Stir Fry", "House Wine (Glass)", "Tiramisu"],
    
    # Main Courses
    "Margherita Pizza": ["Garlic Bread", "Tiramisu", "Soda"],
    "Spaghetti Carbonara": ["Garlic Bread", "House Wine (Glass)", "Tiramisu"],
    "Chicken Alfredo": ["Garlic Bread", "Cheesecake", "Iced Tea"],
    "Grilled Salmon": ["Bruschetta", "House Wine (Glass)", "Chocolate Cake"],
    "Vegetable Stir Fry": ["Bruschetta", "Iced Tea", "Ice Cream Sundae"],
    
    # Desserts
    "Tiramisu": ["Coffee", "Spaghetti Carbonara", "Garlic Bread"],
    "Chocolate Cake": ["Coffee", "Ice Cream Sundae", "Margherita Pizza"],
    "Cheesecake": ["Coffee", "Chicken Alfredo", "Soda"],
    "Ice Cream Sundae": ["Coffee", "Chocolate Cake", "Margherita Pizza"],
    
    # Drinks
    "Soda": ["Margherita Pizza", "Mozzarella Sticks", "Ice Cream Sundae"],
    "Iced Tea": ["Vegetable Stir Fry", "Chicken Alfredo", "Cheesecake"],
    "Coffee": ["Tiramisu", "Cheesecake", "Chocolate Cake"],
    "House Wine (Glass)": ["Grilled Salmon", "Spaghetti Carbonara", "Bruschetta"]
}

class RestaurantChatbot:
    """Restaurant chatbot class to handle user conversations"""
    
    def __init__(self):
        self.menu = self._load_menu()
        self.conversation_history = []
        self.menu_items_by_name = self._create_item_name_lookup()
        self.last_ordered_item = None
        self.last_recommendation = None
        self.awaiting_recommendation_response = False
    
    def _load_menu(self):
        """Load menu data from JSON file"""
        try:
            with open('data/menu.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return empty menu if file doesn't exist or is invalid
            return {
                "appetizers": [],
                "main_courses": [],
                "desserts": [],
                "drinks": []
            }
    
    def _create_item_name_lookup(self):
        """Create a lookup dictionary of item names to full items"""
        lookup = {}
        for category, items in self.menu.items():
            for item in items:
                lookup[item['name'].lower()] = (item, category)
        return lookup
    
    def _find_best_match(self, query, choices, threshold=0.6):
        """Find the best matching string using difflib"""
        if not query or not choices:
            return None
        
        # Convert query to lowercase for matching
        query = query.lower()
        
        # Check exact matches first
        for choice in choices:
            if choice.lower() == query:
                return choice
        
        # Try fuzzy matching
        matches = difflib.get_close_matches(query, choices, n=1, cutoff=threshold)
        return matches[0] if matches else None
    
    def _extract_menu_item_from_text(self, text):
        """Extract a menu item from text using synonyms and fuzzy matching"""
        text = text.lower()
        
        # Extract potential item names from the text
        words = text.split()
        potential_items = []
        
        # Try different word combinations
        for i in range(len(words)):
            for j in range(i+1, min(i+5, len(words)+1)):  # Look at up to 4 words at a time
                phrase = " ".join(words[i:j])
                potential_items.append(phrase)
        
        # Check for exact matches in menu
        for phrase in potential_items:
            if phrase in self.menu_items_by_name:
                return self.menu_items_by_name[phrase]
        
        # Check for matches using synonyms
        for canonical_name, synonyms in MENU_SYNONYMS.items():
            for synonym in synonyms:
                if synonym in text:
                    # Find the closest actual menu item
                    menu_items = list(self.menu_items_by_name.keys())
                    best_match = self._find_best_match(canonical_name, menu_items)
                    if best_match:
                        return self.menu_items_by_name[best_match]
        
        # Try fuzzy matching on menu items
        menu_items = list(self.menu_items_by_name.keys())
        for phrase in potential_items:
            best_match = self._find_best_match(phrase, menu_items)
            if best_match:
                return self.menu_items_by_name[best_match]
        
        return None, None
    
    def _detect_mood_or_weather(self, message):
        """Detect mood or weather mentions in the message"""
        message = message.lower()
        
        # Check for mood mentions
        moods = {
            "happy": ["happy", "good mood", "great mood", "cheerful", "joyful", "excited"],
            "sad": ["sad", "down", "blue", "unhappy", "depressed", "upset"],
            "tired": ["tired", "exhausted", "sleepy", "fatigued", "no energy"],
            "hungry": ["hungry", "starving", "famished", "really hungry", "very hungry"],
            "hot": ["hot", "warm", "heat", "burning", "sweating"],
            "cold": ["cold", "chilly", "freezing", "cool"]
        }
        
        for mood, keywords in moods.items():
            if any(keyword in message for keyword in keywords):
                if mood in ["hot", "cold"]:
                    # These could be weather or feelings
                    if any(weather_term in message for weather_term in ["weather", "outside", "day", "temperature", "degrees"]):
                        return "weather", mood
                    else:
                        return "mood", mood
                return "mood", mood
        
        # Check for weather mentions
        weather_types = {
            "hot": ["hot weather", "hot day", "hot outside", "heat wave"],
            "cold": ["cold weather", "cold day", "cold outside", "freezing"],
            "rainy": ["rainy", "raining", "rain", "wet weather", "pouring"],
            "sunny": ["sunny", "sunshine", "sun", "clear sky", "nice weather", "beautiful day"]
        }
        
        for weather, keywords in weather_types.items():
            if any(keyword in message for keyword in keywords):
                return "weather", weather
        
        return None, None
    
    def _extract_order_id(self, message):
        """Extract an order ID from a message"""
        # Look for patterns like "order number ORD-20230412123456-7890"
        pattern = r'order\s+(?:number|id|#)?\s*(ORD-\d+-\d+)'
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Also look for just "ORD-20230412123456-7890" pattern
        pattern = r'(ORD-\d+-\d+)'
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None
    
    def _get_item_by_name(self, name):
        """Get a menu item by name"""
        name_lower = name.lower()
        if name_lower in self.menu_items_by_name:
            return self.menu_items_by_name[name_lower]
        return None, None
    
    def _handle_recommendation_response(self, message, username):
        """Handle user response to a recommendation"""
        if self.last_recommendation is None:
            return None
            
        # Check if the response is positive
        positive_responses = ["yes", "yeah", "sure", "ok", "okay", "sounds good", "i'd like", "i would like"]
        negative_responses = ["no", "nope", "no thanks", "not now", "later", "pass"]
        
        message_lower = message.lower()
        
        # Check if it's a positive response
        if any(response in message_lower for response in positive_responses):
            # Find the item they're agreeing to
            item, category = self._get_item_by_name(self.last_recommendation)
            
            if item and category:
                # Add to cart
                add_to_cart(username, item)
                
                # Reset recommendations
                recommendation_item = self.last_recommendation
                self.last_recommendation = None
                self.awaiting_recommendation_response = False
                
                return f"Great! I've added {recommendation_item} to your cart. Your total is now ${get_cart(username)['total_price']:.2f}. Would you like anything else?"
            else:
                self.last_recommendation = None
                self.awaiting_recommendation_response = False
                return "I'm sorry, I couldn't find that item in our menu. Can I help you with something else?"
                
        # Check if it's a negative response
        elif any(response in message_lower for response in negative_responses):
            self.last_recommendation = None
            self.awaiting_recommendation_response = False
            return "No problem! Is there anything else you'd like to order or ask about?"
            
        # If it's neither clearly positive nor negative
        return None
    
    def process_message(self, message, username=None):
        """Process user message and return a response"""
        try:
            # Add to conversation history
            self.conversation_history.append({"role": "user", "message": message})
            
            # Convert message to lowercase for easier processing
            message_lower = message.lower()
            
            # If waiting for a recommendation response, handle it first
            if self.awaiting_recommendation_response:
                recommendation_response = self._handle_recommendation_response(message, username)
                if recommendation_response:
                    self.conversation_history.append({"role": "bot", "message": recommendation_response})
                    return recommendation_response
            
            # Check for order cancellation with order ID
            order_id = self._extract_order_id(message)
            if order_id and any(word in message_lower for word in ["cancel", "remove", "delete"]):
                if username:
                    return self._handle_cancel_order_by_id(order_id, username)
                else:
                    return "You need to be logged in to cancel orders."
            
            # Check for mood or weather-based recommendations
            context_type, context_value = self._detect_mood_or_weather(message)
            if context_type and any(term in message_lower for term in ["recommend", "suggest", "what should", "what would", "what can"]):
                if context_type == "mood":
                    return self._get_mood_suggestion(context_value)
                elif context_type == "weather":
                    return self._get_weather_suggestion(context_value)
            
            # Check for menu inquiries
            if any(keyword in message_lower for keyword in ["menu", "what do you have", "what food", "what dishes"]):
                response = self._handle_menu_inquiry(message_lower)
            
            # Check for specific category inquiries
            elif "appetizer" in message_lower:
                response = self._get_category_items("appetizers")
            
            elif any(keyword in message_lower for keyword in ["main", "entree", "course"]):
                response = self._get_category_items("main_courses")
            
            elif "dessert" in message_lower:
                response = self._get_category_items("desserts")
            
            elif any(keyword in message_lower for keyword in ["drink", "beverage"]):
                response = self._get_category_items("drinks")
            
            # Check for recommendations
            elif any(keyword in message_lower for keyword in ["recommend", "suggest", "popular", "specialty", "best"]):
                response = self._handle_recommendation_request(message_lower)
            
            # Check for order intent
            elif any(keyword in message_lower for keyword in ["order", "want", "like", "get", "have", "bring"]):
                if username:
                    response = self._handle_order_intent(message_lower, username)
                else:
                    response = "You need to be logged in to place an order."
            
            # Check for checkout intent
            elif any(keyword in message_lower for keyword in ["checkout", "place order", "complete order"]):
                if username:
                    response = self._handle_checkout(username)
                else:
                    response = "You need to be logged in to place an order."
            
            # Check for cart inquiries
            elif "cart" in message_lower:
                if username:
                    response = self._handle_cart_inquiry(username)
                else:
                    response = "You need to be logged in to use the cart."
            
            # Check for order cancellation intent (general)
            elif any(keyword in message_lower for keyword in ["cancel", "clear cart"]):
                if username:
                    clear_cart(username)
                    response = "I've cleared your cart. Is there anything else I can help you with?"
                else:
                    response = "You need to be logged in to manage your cart."
            
            # Check for order status inquiry
            elif any(keyword in message_lower for keyword in ["order status", "my order", "track"]):
                if username:
                    response = self._handle_order_status_inquiry(username)
                else:
                    response = "You need to be logged in to check order status."
            
            # Check for hours
            elif any(keyword in message_lower for keyword in ["hour", "open", "close"]):
                response = "We're open Monday through Thursday from 11:00 AM to 10:00 PM, Friday and Saturday from 11:00 AM to 11:00 PM, and Sunday from 12:00 PM to 9:00 PM."
            
            # Check for location
            elif any(keyword in message_lower for keyword in ["location", "address", "where"]):
                response = "We're located at 123 Main Street, Downtown. Would you like directions or information about parking?"
            
            # Check for vegetarian options
            elif any(keyword in message_lower for keyword in ["vegetarian", "vegan"]):
                response = "Yes, we have several vegetarian options! These include Margherita Pizza, Vegetable Stir Fry, and all of our appetizers except the Soup of the Day (which varies). Would you like more details about any of these dishes?"
            
            # Default response for other inquiries
            else:
                response = "I'm here to help with menu information, taking orders, and answering questions about our restaurant. How can I assist you today?"
            
            # Add to conversation history
            self.conversation_history.append({"role": "bot", "message": response})
            return response
            
        except Exception as e:
            print(f"Error processing message: {e}")
            traceback.print_exc()
            return "I'm sorry, I encountered an error processing your message. How else can I help you today?"
    
    def _handle_menu_inquiry(self, message):
        """Handle general menu inquiries"""
        return "Our menu includes appetizers like Garlic Bread and Mozzarella Sticks, main courses such as Margherita Pizza and Grilled Salmon, desserts including Tiramisu and Cheesecake, and various drinks. Would you like details about any specific category?"
    
    def _get_category_items(self, category):
        """Get formatted list of items in a category"""
        if category not in self.menu or not self.menu[category]:
            return f"I'm sorry, we don't have any {category} on the menu right now."
        
        items = ", ".join([f"{item['name']} (${item['price']:.2f})" for item in self.menu[category]])
        return f"Our {category.replace('_', ' ')} include: {items}."
    
    def _handle_recommendation_request(self, message):
        """Handle requests for recommendations"""
        # Check for specific food types in the request
        if "coffee" in message or "caffeine" in message:
            return "I'd recommend our premium Italian Coffee. It's freshly ground, rich, and aromatic. Would you like to order one?"
        
        if "pizza" in message:
            return "Our Margherita Pizza is our specialty - with fresh mozzarella, basil, and our house-made tomato sauce. It's a customer favorite!"
        
        if "wine" in message:
            return "We have an excellent House Wine selection. The red pairs beautifully with our Grilled Salmon or any pasta dish."
        
        if "dessert" in message:
            return "Our Tiramisu is made fresh daily and is absolutely delicious! It's the perfect way to end your meal."
        
        # Default to a general recommendation
        return "I'd recommend starting with our Bruschetta, followed by the Margherita Pizza or Chicken Alfredo. And don't miss our Tiramisu for dessert - it's a customer favorite!"
    
    def _get_mood_suggestion(self, mood):
        """Get food suggestions based on mood"""
        if mood in MOOD_SUGGESTIONS:
            suggestions = MOOD_SUGGESTIONS[mood]
            return random.choice(suggestions) + " Would you like to order that?"
        
        # Default suggestion if mood not found
        return "I'd recommend our Margherita Pizza - it's a customer favorite! Would you like to order one?"
    
    def _get_weather_suggestion(self, weather):
        """Get food suggestions based on weather"""
        if weather in WEATHER_SUGGESTIONS:
            suggestions = WEATHER_SUGGESTIONS[weather]
            return random.choice(suggestions) + " Would you like to order that?"
        
        # Default suggestion if weather not found
        return "I'd recommend our Margherita Pizza - it's perfect for any weather! Would you like to order one?"
    
    def _get_item_recommendation(self, item_name):
        """Get a recommendation based on an ordered item"""
        if item_name in ITEM_RECOMMENDATIONS:
            # Select a random recommendation from the list
            recommendations = ITEM_RECOMMENDATIONS[item_name]
            return random.choice(recommendations)
        return None
    
    def _handle_order_intent(self, message, username):
        """Handle intent to order items"""
        # Try to identify the item from the message
        item, category = self._extract_menu_item_from_text(message)
        
        if item and category:
            # Check for special instructions
            no_ingredients = []
            extra_ingredients = []
            
            # Look for "without" or "no" instructions
            if "without" in message:
                parts = message.split("without")
                if len(parts) > 1:
                    no_ingredient = parts[1].strip().split()[0]  # Take first word after 'without'
                    no_ingredients.append(no_ingredient)
            
            if "no " in message:
                parts = message.split("no ")
                if len(parts) > 1:
                    no_ingredient = parts[1].strip().split()[0]  # Take first word after 'no '
                    no_ingredients.append(no_ingredient)
            
            # Look for "extra" instructions
            if "extra " in message:
                parts = message.split("extra ")
                if len(parts) > 1:
                    extra_ingredient = parts[1].strip().split()[0]  # Take first word after 'extra '
                    extra_ingredients.append(extra_ingredient)
            
            # Combine special instructions
            special_instructions = ""
            if no_ingredients:
                special_instructions += "No " + ", ".join(no_ingredients)
            
            if extra_ingredients:
                if special_instructions:
                    special_instructions += "; "
                special_instructions += "Extra " + ", ".join(extra_ingredients)
            
            # Add item to cart
            add_to_cart(username, item, 1, special_instructions)
            
            # Store this item for recommendations
            self.last_ordered_item = item['name']
            
            # Get a recommendation
            recommendation = self._get_item_recommendation(item['name'])
            if recommendation:
                self.last_recommendation = recommendation
                self.awaiting_recommendation_response = True
                
                # Confirmation message with recommendation
                if special_instructions:
                    return f"I've added one {item['name']} to your cart with the following special instructions: {special_instructions}. Your current total is ${get_cart(username)['total_price']:.2f}. Would you like to add {recommendation} as well? It pairs perfectly with your order."
                else:
                    return f"I've added one {item['name']} to your cart. Your current total is ${get_cart(username)['total_price']:.2f}. Would you like to add {recommendation} as well? It pairs perfectly with your order."
            else:
                # Regular confirmation without recommendation
                if special_instructions:
                    return f"I've added one {item['name']} to your cart with the following special instructions: {special_instructions}. Your current total is ${get_cart(username)['total_price']:.2f}. Would you like anything else?"
                else:
                    return f"I've added one {item['name']} to your cart. Your current total is ${get_cart(username)['total_price']:.2f}. Would you like anything else?"
        else:
            # If no specific item found, give a more helpful response
            menu_categories = list(self.menu.keys())
            category_items = [item['name'] for category in menu_categories for item in self.menu[category]]
            
            if category_items:
                suggestions = random.sample(category_items, min(3, len(category_items)))
                suggestions_str = ", ".join(suggestions)
                return f"I'm not sure which item you'd like to order. Here are some options you might enjoy: {suggestions_str}. Would you like to order any of these?"
            else:
                return "I'm not sure which item you'd like to order. Could you please specify the name of the item?"
    
    def _handle_cart_inquiry(self, username):
        """Handle inquiries about the cart"""
        cart = get_cart(username)
        
        if not cart['items']:
            return "Your cart is currently empty. Would you like to see our menu to start ordering?"
        
        items = ", ".join([f"{item['name']} (${item['price']:.2f})" for item in cart['items']])
        return f"Your cart contains: {items}. Your total is ${cart['total_price']:.2f}. Ready to place your order or would you like to add more items?"
    
    def _handle_checkout(self, username):
        """Handle checkout process"""
        cart = get_cart(username)
        
        if not cart['items']:
            return "Your cart is empty. Please add some items before checking out."
        
        # Place the order
        order_id = place_order(username, cart)
        
        if order_id:
            return f"Thank you for your order! Your order ID is {order_id}. You can check your order status in the Order History page. Your order has been placed and will be ready shortly."
        else:
            return "Sorry, there was an issue placing your order. Please try again."
    
    def _handle_order_status_inquiry(self, username):
        """Handle inquiries about order status"""
        orders = get_user_orders(username)
        
        if not orders:
            return "You don't have any orders yet. Would you like to place an order now?"
        
        # Get the most recent order
        latest_order = orders[0]  # Assuming orders are sorted with most recent first
        
        return f"Your most recent order (ID: {latest_order['order_id']}) is currently {latest_order['status']}. You can view all your orders in the Order History page."
    
    def _handle_cancel_order_by_id(self, order_id, username):
        """Handle cancellation of a specific order by ID"""
        # Check if the order exists and belongs to the user
        order = get_order_by_id(order_id)
        if not order:
            return f"I couldn't find an order with ID {order_id}. Please check the order number and try again."
        
        if order['username'] != username:
            return "I'm sorry, but you can only cancel your own orders."
        
        # Try to cancel the order
        if cancel_order(order_id):
            return f"Order {order_id} has been cancelled successfully."
        else:
            return f"Sorry, I couldn't cancel order {order_id}. It may have already been completed or cancelled."
    
    def get_predictions(self, partial_input, max_predictions=5):
        """Get message predictions based on partial input"""
        if not partial_input or len(partial_input) < 2:
            return []
        
        partial_input = partial_input.lower()
        
        # Use difflib to find close matches
        matching_predictions = []
        for phrase in PREDICTION_PHRASES:
            if partial_input in phrase.lower():
                matching_predictions.append(phrase)
            else:
                # Try fuzzy matching for typos
                similarity = difflib.SequenceMatcher(None, partial_input, phrase.lower()).ratio()
                if similarity > 0.6:  # Threshold for similarity
                    matching_predictions.append(phrase)
        
        # Add custom predictions based on menu items
        for category in self.menu:
            for item in self.menu[category]:
                item_phrase = f"I'd like to order a {item['name']}"
                if partial_input in item_phrase.lower():
                    matching_predictions.append(item_phrase)
        
        # Remove duplicates and limit to max_predictions
        unique_predictions = list(dict.fromkeys(matching_predictions))
        return unique_predictions[:max_predictions]