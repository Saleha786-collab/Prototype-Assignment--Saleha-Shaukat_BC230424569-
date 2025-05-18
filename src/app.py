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
    params = req['queryResult']['parameters']
    number_of_guests = params.get('number')
    date = params.get('date')   
    time = params.get('time')
    email = params.get('email')

    
    if isinstance(date, list):
        date = date[0]
    if isinstance(time, list):
        time = time[0]

   
    if not number_of_guests:
        return jsonify({"fulfillmentText": "Please provide the number of guests to reserve the table for."})
    if not date:
        return jsonify({"fulfillmentText": "Please tell me the date you want to reserve for."})
    if not time:
        return jsonify({"fulfillmentText": "Please tell me the time you want to reserve for."})
    if not email:
        return jsonify({"fulfillmentText": "Can you please provide your email for booking the table?"})

    try:
        
        reservation_date = datetime.fromisoformat(date).date()
        reservation_time = datetime.fromisoformat(time).time()
        formatted_date = reservation_date.strftime("%d %B %Y")  
        formatted_time = reservation_time.strftime("%I:%M %p")  

        # Check if the user exists in the database
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                "fulfillmentText": "Your email is not valid. Please enter the login email you use for your account."
            })

        user_id = user.user_id  # Get the user_id

        # Create the table reservation
        reservation = TableReservation(
            guests=number_of_guests,
            date=reservation_date,
            time=reservation_time,
            user_id=user_id
        )

        db.session.add(reservation)
        db.session.commit()

        # Prepare the response message
        response_text = (
            f"Your table for {number_of_guests} on {formatted_date} at {formatted_time} "
            f"is confirmed! Your reservation ID is {reservation.id}."
        )

    except Exception as e:
        db.session.rollback()  
        response_text = "Something went wrong while booking your reservation. Please try again later."

    return jsonify({"fulfillmentText": response_text})


    

def Order_taking(req):
    params = req['queryResult']['parameters']
    product_name = params.get('ProductName')
    quantity = params.get('quantity')
    email = params.get('email')


    # Check if the product_name, quantity, and email are provided
    if not product_name:
        return jsonify({
            "fulfillmentText": 'What product do you want to order?'
        })
    if not quantity:
        return jsonify({
            "fulfillmentText": f'How much {product_name} do you want to order?'
        })
    try:
        quantity = int(quantity)
    except ValueError:
        return jsonify({
        "fulfillmentText": "Please provide a valid number for quantity."
    })
    if not email:
        return jsonify({
            "fulfillmentText": 'Can you please tell me your email for placing your order?'
        })

    try:
        # Fetch the product from the database
        product = Product.query.filter(Product.name.ilike(f'%{product_name}%')).first()
        if not product:
            return jsonify({
                "fulfillmentText": f'{product_name} is not available in our menu. You can see our menu by typing "I want to see the menu" and order anything else from that menu. Thanks!'
            })

        

        # Check if the user exists in the database
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                "fulfillmentText": "We couldn't find your account. Please check your account and send the email again."
            })

       

        # Create a new order for the user
        order = Order(user_id=user.user_id)
        db.session.add(order)
        db.session.flush()  # Get the order ID

        # Add the order item (product) to the order
        order_item = OrderItem(order_id=order.order_id, product_id=product.product_id, quantity=quantity)
        db.session.add(order_item)

     
        db.session.commit()

      
        product_name_plural = f"{product_name}s" if quantity > 1 else product_name  
        text_response = f'Your order of {quantity} {product_name_plural} has been placed. Your order ID is {order.order_id}.'

        return jsonify({
            "fulfillmentText": text_response
        })

    except Exception as e:
        db.session.rollback()
        text_response = 'Due to a server issue, your order could not be placed. Please try again later.'
        return jsonify({
            "fulfillmentText": text_response
        })



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
    params = req['queryResult']['parameters']
    order_id = params.get('order_id')
    
    if not order_id:
        return jsonify({
            "fulfillmentText": "Can you please tell your order_id?"
        })
    
    try:    
        order_id = int(order_id)  
    except:
        return jsonify({
            "fulfillmentText": "Your order_id is not valid. Please provide a valid order_id."
        })

    
    cancel_order_id = Order.query.filter_by(order_id=order_id).first()
    
    if not cancel_order_id:
        return jsonify({
            "fulfillmentText": "I could not find your order_id. Please check your order_id again."
        })
    
    
    order_items = OrderItem.query.filter_by(order_id=cancel_order_id.order_id).all()
    if not order_items:
        return jsonify({
            "fulfillmentText": "No items found for this order."
        })

    
    db.session.delete(cancel_order_id)
    db.session.commit()
    product_names = ', '.join([item.product.name for item in order_items])

    response_text = f"Your order with ID {cancel_order_id.order_id} has been cancelled. The order contained: {product_names}. The order has been successfully removed from our system."

    return jsonify({
        "fulfillmentText": response_text
    })




def init_db():
    with app.app_context():
        db.create_all()



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
