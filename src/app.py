import os
import json
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, time
from sqlalchemy.exc import SQLAlchemyError 
from sqlalchemy import text,and_, or_
from model import db, User, SupportTicket, Product, Order, OrderItem, ProductInquiry, TableReservation,RoomAvailability
from form import RegistrationForm, LoginForm, Accountform
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from dateutil.parser import isoparse,parse as parse_date
from datetime import datetime, date, timedelta
from collections import Counter

if os.getenv("FLASK_ENV") == "development":
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)


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
        return product_inquiry(req)
    elif intent == 'Order taking intent - cancel':
        return cancel_order(req)
    elif intent =='Add order item':
        return add_order_item(req)
    elif intent=='Remove order item':
        return remove_order_item(req)
    elif intent=='cancel table reservation':
        return cancel_table_reservation(req)
    elif intent=='Hotel Room Availability':
        return room_availability(req)
    


    return fallback_response()



def handle_order_status(req):
    params=req['queryResult']['parameters']
    order_id=params.get('order_id')
    if not order_id:
        return jsonify({
            'fulfillmentText':'Can you please provide your order_id?'
        })
    try:
        order_id=int(order_id)
    except ValueError:
        return jsonify({
            'fulfillmentText':'This order id is not valid.Please provide the valid order_id'
        })
    order=Order.query.filter_by(order_id=order_id).first()
    if not order:
        return jsonify({
            'fulfillmentText':'We have not any order with this order_id please check your order id again'
        })
    
    if order:
        delivery_date = order.delivery_date.strftime("%d %B %Y %I:%M %p") if order.delivery_date else "your order delivery status will be upload soon"
        return jsonify({
        'fulfillmentText': f'''The order status of your order is {order.order_status} and order delivery time is {delivery_date}'''
    })
    

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

       


        order = Order(user_id=user.user_id)
        db.session.add(order)
        db.session.flush()  

       
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


def add_order_item(req):
    params = req['queryResult']['parameters']
    product_name = params.get('productname')
    quantity = params.get('quantity')
    order_id = params.get('order_id')

    if not product_name:
        return jsonify({
            "fulfillmentText": "What product do you want to add?"
        })
    if not quantity:
        return jsonify({
            "fulfillmentText": "How many quantity do you want to add?"
        })
    if not order_id:
        return jsonify({
            "fulfillmentText": "What is your order_id?"
        })

 
    order = Order.query.filter_by(order_id=order_id).first()
    if not order:
        return jsonify({
            "fulfillmentText": "We could not find any order with this order_id. Please check your order_id again."
        })

    product = Product.query.filter_by(name=product_name).first()
    if not product:
        return jsonify({
            "fulfillmentText": f"The product {product_name} is not available in our menu. Please choose another product."
        })

   
    add_product = OrderItem(product_id=product.product_id, quantity=quantity, order_id=order_id)
    db.session.add(add_product)
    db.session.commit()

   
    text_response = f'Your product item {quantity} x {product_name} has been added to your order.'

    return jsonify({
        'fulfillmentText': text_response
    })


    
    
def remove_order_item(req):
    params = req['queryResult']['parameters']
    product_name = params.get('productname')
    quantity = params.get('quantity')
    order_id = params.get('order_id')


    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        return jsonify({
            'fulfillmentText': "Please provide a valid quantity."
        })
    
    if not product_name:
        return jsonify({
            'fulfillmentText': "Please provide the product name that you want to remove"
        })
    
    if not quantity or quantity <= 0:  
       
        return jsonify({
            'fulfillmentText': "Can you please provide the quantity of the product that you want to remove? It should be a positive number."
        })
        
    if not order_id:
        return jsonify({
            'fulfillmentText': "Can you please provide your existing order_id?"
        })
    
    order = Order.query.filter_by(order_id=order_id).first()
    if not order:
        return jsonify({
            'fulfillmentText': 'We could not find any order with this order_id. Please check your order_id again.'
        })
    
    product = Product.query.filter_by(name=product_name).first()
    if not product:
        return jsonify({
            'fulfillmentText': "This product is not available. Please provide another product name. You can see product names from our menu."
        })
    
    order_item = OrderItem.query.filter_by(order_id=order_id, product_id=product.product_id).first()
    if not order_item:
        return jsonify({
            'fulfillmentText': "No matching product found in the order. Please check the product name."
        })

    if order_item.quantity > quantity:
        order_item.quantity -= quantity
        db.session.commit()
        return jsonify({
            'fulfillmentText': f"{quantity} of {product_name} has been removed from your order."
        })
    elif order_item.quantity < quantity:
        db.session.delete(order_item)
        db.session.commit()
        return jsonify({
            'fulfillmentText': f"Your given quantity is greater than the quantity you have on your order. The product {order_item.quantity} has been completely removed from your order."
        })
    else:
        db.session.delete(order_item)
        db.session.commit()
        return jsonify({
            'fulfillmentText': f"The product {product_name} has been completely removed from your order."
        })


def cancel_table_reservation(req):
    param = req['queryResult']['parameters']
    reservation_id = param.get('reservation_id')

    if not reservation_id:
        return jsonify({
            'fulfillmentText': 'Can you provide your reservation ID?'
        })

    reservation = TableReservation.query.filter_by(id=reservation_id).first()

   
    if not reservation:
        return jsonify({
            'fulfillmentText': 'Sorry, we could not find a reservation with that ID. Please check and provide a valid reservation ID.'
        })


    try:
        db.session.delete(reservation)
        db.session.commit()
        text_response = f'Your reservation with ID {reservation.id} has been cancelled. Thanks!'
        return jsonify({
            'fulfillmentText': text_response
        })
    except Exception as e:
        return jsonify({
            'fulfillmentText': f"Sorry, there was an error canceling your reservation. Please try again later. Error: {str(e)}"
        })

def product_inquiry(req):
     params=req['queryResult']['parameters']
     product_name=params.get('ProductName')
     if not product_name:
         return jsonify({
             'fulfillmentText':'Can you please tell the name of product that you have to add'
         })
     product=Product.query.filter_by(name=product_name).first()
     if not product:
         return jsonify({
            'fulfillmentText':f'This product is not in our menu you can order by seeing our menu'
        })
     if product.stock == 'Available':
         return jsonify({
            'fulfillmentText':f"{product_name} is in stock. The price of {product_name} is ${product.price}"
        })
     else:
         return jsonify({
            'fulfillmentText':f"Sorry currently {product_name} is not in stock.You can order anything esle.Thanks "
        })
    

def normalize_date(val):
    """
    Turn Dialogflow’s parameter into a datetime.date:
      - Handles lists by picking the first element
      - Handles datetime.date or datetime.datetime directly
      - Handles strings like "2025-04-30", "30 April", "1 may", etc.
      - Returns None if parsing fails
    """
    
    if isinstance(val, list) and val:
        val = val[0]

    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val

   
    if isinstance(val, str):
        s = val.strip().title()       
        try:
           
            return parse_date(s, dayfirst=True).date()
        except Exception:
            
            for fmt in ("%d %B", "%d %b"):
                try:
                    dt = datetime.strptime(s, fmt)
                    return dt.replace(year=date.today().year).date()
                except Exception:
                    continue
    return None

def room_availability(req):
    params = req['queryResult']['parameters']
    sd_raw = params.get('start_date')
    ed_raw = params.get('end_date')

    
    check_in = normalize_date(sd_raw)
    if not check_in:
        return jsonify({
            'fulfillmentText': "Sorry, I couldn’t understand the check-in date. Please say something like “30 April” or “2025-04-30.”"
        })

    
    if not ed_raw:
        check_out = check_in + timedelta(days=1)
    else:
        check_out = normalize_date(ed_raw)
        if not check_out:
            return jsonify({
                'fulfillmentText': "Sorry, I couldn’t understand the check-out date. Please try again."
            })

    
    rooms = RoomAvailability.query.filter(
        and_(
            RoomAvailability.room_available == True,
            or_(
                RoomAvailability.start_date.is_(None),
                RoomAvailability.end_date.is_(None),
                RoomAvailability.end_date < check_in,
                RoomAvailability.start_date > check_out
            )
        )
    ).all()


    if not rooms:
        return jsonify({
            'fulfillmentText': (
                f"Sorry, no rooms free from "
                f"{check_in:%d %b %Y} to {check_out:%d %b %Y}."
            )
        })

 
    from collections import Counter
    counts = Counter(r.room_type for r in rooms)
    summary = ', '.join(f"{num} {rtype}" for rtype, num in counts.items())

    return jsonify({
        'fulfillmentText': (
            f"Great! Available from {check_in:%d %b} to {check_out:%d %b}: "
            f"{summary}."
        )
    })
def init_db():
    with app.app_context():
        db.create_all()



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
