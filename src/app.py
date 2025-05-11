import os
import json
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, time
from sqlalchemy.exc import SQLAlchemyError 
from sqlalchemy import text 
from model import db, User, SupportTicket, Product, Order, OrderItem, ProductInquiry, TableReservation
from form import RegistrationForm, LoginForm, Accountform
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from dateutil.parser import isoparse  
# Configure logging
if os.getenv("FLASK_ENV") == "development":
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)

# Initialize Flask app
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:Saleha%40786@localhost/db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'defaultsecretkey')

# Initialize the database and migration
db.init_app(app)
migrate = Migrate(app, db)


bcrypt = Bcrypt(app)

# Initialize Login Manager
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None

# Routes for user registration and login
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pwd)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data): 
            login_user(user, form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = Accountform()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your Account has been updated')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('account.html', title='Account', form=form)

@app.route('/home')
def home():
    return render_template('home.html')


# Dialogflow Webhook Route - Protected with login_required
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(force=True)
    logging.debug(f"Received Request: {req}")
    
    # Handle different intents
    intent = req['queryResult']['intent']['displayName']
    if intent == 'Technical Support Intent':
        return Technical_Support(req)
    elif intent == 'Issue Described Intent':
        return Issue_Described(req)
    elif intent == 'Issue Resolved Intent':
        return Issue_Resolved(req)
    elif intent == 'Issue Not Resolved Intent':
        return Issue_Not_Resolved(req)
    elif intent == 'Email Capture':
        return check_ticket_creation(req)
    elif intent == 'Default Welcome Intent':
        return Default_Welcome(req)
    elif intent == 'Invalid Input':
        return invalid_input(req)
    elif intent == 'Multiple Intents Detected':
        return Multiple_Intents_Detected(req)
    elif intent == 'Ending Conversation Intent':
        return Closing_Conversation()
    elif intent == 'Order Status Intent':
        return handle_order_status(req)
    elif intent == 'Table reservation intent':
        return Table_reservation(req)
    elif intent == 'Order taking intent':
        return Order_taking(req)
    elif intent == 'product related query':
        return product_query(req)
    elif intent == 'Order taking intent - add':
        return Order_taking_add(req)
    elif intent == 'Order taking intent - cancel':
        return cancel_order(req)
    

    return fallback_response()

def Default_Welcome(req):
    if current_user.is_authenticated:
        response = f"Hello! Welcome to the Restaurant. How can I assist you today?"
    else:
        response = "Hello! Welcome to the Restaurant. How can I assist you today?"
    return jsonify({'fulfillmentText': response})

def handle_order_status(req):
    try:
       
        logging.debug(f"Full Request: {req}")
        
        # Extract parameters safely
        parameters = req.get('queryResult', {}).get('parameters', {})
        order_id = parameters.get('order_id')

        logging.debug(f"Extracted Order ID: {order_id}")

        if not order_id:
            
            return jsonify({'fulfillmentText': "Please provide an Order ID."})

        try:
            
            order_id = int(order_id)  
            logging.debug(f"Order ID after conversion: {order_id}")
        except ValueError:
            return jsonify({'fulfillmentText': "Invalid Order ID format. Please provide a valid number."})

        # Query the order from the database
        order = Order.query.get(order_id)
        logging.debug(f"Order found in database: {order}")

        if order:
            delivery_date = order.delivery_date.strftime("%d %B %Y") if order.delivery_date else "not set"
            return jsonify({
                'fulfillmentText': f"Order #{order_id}\nStatus: {order.order_status}\nDelivery: {delivery_date} Would you like anything else?"
            })
        else:
            return jsonify({'fulfillmentText': f"No order found with ID {order_id}"})

    except Exception as e:
        logging.error(f"Error processing order status: {str(e)}")
        return jsonify({'fulfillmentText': "System error. Contact support."})



def fallback_response():
    response = "I'm sorry, I didn't quite understand. Could you please rephrase your question?"
    return jsonify({'fulfillmentText': response})

def Closing_Conversation():
    response = "Thank you for chatting with us. Have a great day!"
    return jsonify({'fulfillmentText': response})

def Technical_Support(req):
    response = 'Could you please describe the issue you are facing?'
    return jsonify({'fulfillmentText': response})

def Issue_Described(req):
    issue = req['queryResult']['parameters'].get('issue')
    response = "I'm sorry to hear that. Let's try some basic troubleshooting steps. Have you tried resetting the device by holding the power button for 10 seconds?"
    return jsonify({'fulfillmentText': response})

def Issue_Resolved(req):
    response = "Glad to hear! Anything else I can help with?"
    return jsonify({'fulfillmentText': response})

def Issue_Not_Resolved(req):
    response = "I'll create a support ticket for further assistance. Can you confirm your email address?"
    return jsonify({'fulfillmentText': response})

def check_ticket_creation(req):
    try:
       
        email = req['queryResult']['parameters'].get('email', 'unknown@example.com')
        name = req['queryResult']['parameters'].get('name', 'Guest')

      
        issue_description = req['queryResult']['parameters'].get('issue', 'Technical issue reported by user')
        logging.debug(f"Creating support ticket for issue: {issue_description}")

     
        new_ticket = SupportTicket(user_id=None, issue_description=issue_description, email=email)
        db.session.add(new_ticket)
        db.session.commit()
        logging.debug(f"Ticket created successfully with ID: {new_ticket.ticket_id}")
        
        return jsonify({'fulfillmentText': "Your support ticket has been created successfully. Our team will get back to you shortly."})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error while creating ticket: {e}")
        return jsonify({'fulfillmentText': f"Error occurred while creating ticket: {e}"})


def invalid_input(req):
    response = "Sorry, that doesn't seem to be a valid order number. Could you check and try again?"
    return jsonify({'fulfillmentText': response})

def Multiple_Intents_Detected(req):
    response = "I see you're asking about multiple things. Which one would you like to start with?"
    return jsonify({'fulfillmentText': response})

def product_query(req):
    parameters = req['queryResult']['parameters']
    product_name = parameters.get('ProductName')

    product = Product.query.filter_by(name=product_name).first()

    if product:
        if product.stock.lower() == 'available':
            text = f"The {product.name} is currently available. It costs Rs. {product.price}."
        else:
            text = f"Currently, the {product.name} is out of stock. Would you like me to notify you when it's back?"
        
        
        return jsonify({
            "fulfillmentText": text,
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [text]
                    }
                }
            ]
        })

    else:
        text = "Sorry, this product is not in our menu. You can see our full menu by saying 'show me the menu'."
        return jsonify({
            "fulfillmentText": text,
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [text]
                    }
                }
            ]
        })


def Table_reservation(req):
    try:
        parameters = req['queryResult'].get('parameters', {})
        logging.debug(f"Parameters received: {parameters}")

        guests = parameters.get('number')
        date_str = parameters.get('date')
        time_str = parameters.get('time')

        # Validate and prompt for missing fields
        if not date_str:
            return jsonify({'fulfillmentText': "Please tell me the date for your reservation."})
        if not time_str:
            return jsonify({'fulfillmentText': "What time should I reserve the table for?"})
        if not guests:
            return jsonify({'fulfillmentText': "How many guests should I reserve the table for?"})

        try:
            guests = int(guests)
        except (ValueError, TypeError):
            return jsonify({'fulfillmentText': "Please provide a valid number of guests (e.g., 2, 4, 6)."})

        # Parse date and time safely
        try:
            reservation_date = isoparse(date_str).date()
        except Exception as e:
            logging.error(f"Invalid date format: {date_str} - {e}")
            return jsonify({'fulfillmentText': "Please provide a valid reservation date."})

        try:
            reservation_time = isoparse(time_str).time()
        except Exception as e:
            logging.error(f"Invalid time format: {time_str} - {e}")
            return jsonify({'fulfillmentText': "Please provide a valid reservation time."})

        # Save to database
        new_reservation = TableReservation(
            user_id=None,  # If you have user login, replace None with actual user ID
            date=reservation_date,
            time=reservation_time,
            guests=guests
        )
        db.session.add(new_reservation)
        db.session.commit()

        # Get reservation ID after commit
        reservation_id = new_reservation.id

        return jsonify({
            'fulfillmentText': (
                f"Your table for {guests} guest(s) on {reservation_date.strftime('%d %B %Y')} "
                f"at {reservation_time.strftime('%I:%M %p')} has been reserved! "
                f"Your reservation ID is #{reservation_id}."
            )
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Unexpected error in Table_reservation: {str(e)}")
        return jsonify({'fulfillmentText': "Sorry, something went wrong while reserving your table."})
    

def Order_taking(req):
    try:
        parameters = req['queryResult'].get('parameters', {})
        contexts = req['queryResult'].get('outputContexts', [])

        product_name = parameters.get('ProductName') or parameters.get('productname')
        quantity = parameters.get('quantity') or parameters.get('number')

        for ctx in contexts:
            ctx_params = ctx.get('parameters', {})
            if not product_name:
                product_name = ctx_params.get('ProductName') or ctx_params.get('productname')
            if not quantity:
                quantity = ctx_params.get('quantity') or ctx_params.get('number')

        if not product_name:
            return jsonify({'fulfillmentText': "Please specify the product you want to order."})

        product = Product.query.filter(Product.name.ilike(f"%{product_name}%")).first()
        if not product:
            return jsonify({'fulfillmentText': f"Sorry, we couldn't find a product named '{product_name}'."})

        # Check stock status from string
        stock_status = (product.stock or "").strip().lower()
        if stock_status != "available":
            return jsonify({'fulfillmentText': f"Sorry, '{product.name}' is currently out of stock."})

        if quantity is None:
            return jsonify({'fulfillmentText': f"'{product.name}' is available. How many units would you like to order?"})

        try:
            quantity = int(float(quantity))
        except Exception:
            return jsonify({'fulfillmentText': "Please provide a valid number for quantity."})

        if quantity <= 0:
            return jsonify({'fulfillmentText': "Quantity must be at least 1."})

        # Proceed with creating the order
        new_order = Order(user_id=None)
        db.session.add(new_order)
        db.session.commit()

        order_item = OrderItem(order_id=new_order.order_id, product_id=product.product_id, quantity=quantity)
        db.session.add(order_item)
        db.session.commit()

        return jsonify({
            'fulfillmentText': f"Your order for {quantity} unit(s) of '{product.name}' has been placed. Your order ID is {new_order.order_id}."
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in Order_taking: {str(e)}")
        return jsonify({'fulfillmentText': "There was an error placing your order. Please try again."})



def Order_taking_add(req):
    try:
        parameters = req['queryResult'].get('parameters', {})
        contexts = req['queryResult'].get('outputContexts', [])
        
        order_id = parameters.get('order_id')
        product_name = parameters.get('ProductName') or parameters.get('productname')
        quantity = parameters.get('quantity') or parameters.get('number')

        # Convert product name from list to string if needed
        if isinstance(product_name, list):
            product_name = ' '.join(product_name).strip()

        # Extract from contexts if missing
        for ctx in contexts:
            ctx_params = ctx.get('parameters', {})
            if not order_id:
                order_id = ctx_params.get('order_id')
            if not product_name:
                product_name = ctx_params.get('ProductName') or ctx_params.get('productname')
                if isinstance(product_name, list):
                    product_name = ' '.join(product_name).strip()
            if not quantity:
                quantity = ctx_params.get('quantity') or ctx_params.get('number')

        # Validate all required fields
        if not order_id:
            return jsonify({'fulfillmentText': "Please provide your order ID to add items."})
        if not product_name:
            return jsonify({'fulfillmentText': "Which product would you like to add?"})
        if not quantity:
            return jsonify({'fulfillmentText': f"How many units of {product_name} would you like to add?"})

        # Validate order and product
        order = db.session.get(Order, order_id)

        if not order:
            return jsonify({'fulfillmentText': f"No order found with ID {order_id}."})

        product = Product.query.filter(Product.name.ilike(f"%{product_name}%")).first()
        if not product:
            return jsonify({'fulfillmentText': f"Product '{product_name}' not found in our menu."})

        # Add item to order
        new_item = OrderItem(order_id=order.order_id, product_id=product.product_id, quantity=int(quantity))
        db.session.add(new_item)
        db.session.commit()

        return jsonify({
            'fulfillmentText': f"Added {quantity} unit(s) of '{product.name}' to your order #{order_id}."
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in Order_taking_add: {str(e)}")
        return jsonify({'fulfillmentText': "Sorry, there was a problem adding that item. Please try again."})


def cancel_order(req):
    try:
        parameters = req['queryResult'].get('parameters', {})
        contexts = req['queryResult'].get('outputContexts', [])

        order_id = parameters.get('order_id')

        for ctx in contexts:
            if not order_id:
                order_id = ctx.get('parameters', {}).get('order_id')

        if not order_id:
            return jsonify({'fulfillmentText': "Please provide the order ID you want to cancel."})

        order = db.session.get(Order, order_id)
        if not order:
            return jsonify({'fulfillmentText': f"No order found with ID #{order_id}."})

        # Delete all items in the order first
        db.session.query(OrderItem).filter_by(order_id=order_id).delete()
        db.session.delete(order)
        db.session.commit()

        return jsonify({'fulfillmentText': f"Your order #{order_id} has been successfully canceled."})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error canceling order: {e}")
        return jsonify({'fulfillmentText': "Failed to cancel the order. Please try again later."})




def init_db():
    with app.app_context():
        db.create_all()



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
