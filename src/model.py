from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Initialize db and login_manager
db = SQLAlchemy()


# User Model
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255))  # Increase size if needed
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    tickets = db.relationship('SupportTicket', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    inquiries = db.relationship('ProductInquiry', backref='user', lazy=True)


    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f'<User {self.username}>'

  
    def set_password(self, password):
        self.password = generate_password_hash(password)  # Hash the password before storing it

    # Password checking method
    def check_password(self, password):
        return check_password_hash(self.password, password)
          



# SupportTicket Model
class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    ticket_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    issue_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('open', 'closed', 'pending'), default='open')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    resolved_at = db.Column(db.TIMESTAMP)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    email = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<SupportTicket {self.ticket_id}>'

# Product Model
class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2))
    stock = db.Column(db.Integer)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    # Relationship
    inquiries = db.relationship('ProductInquiry', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.name}>'

# Order Model
class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    order_status = db.Column(db.Enum('pending', 'shipped', 'delivered'), default='pending')
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_date = db.Column(db.DateTime, nullable=True)  

    # Relationship 
    items = db.relationship('OrderItem', backref='order', lazy=True)

    def __repr__(self):
        return f'<Order {self.order_id}>'

   


# OrderItem Model
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    order_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    quantity = db.Column(db.Integer)

    def __repr__(self):
        return f'<OrderItem {self.order_item_id}>'

# ProductInquiry Model
class ProductInquiry(db.Model):
    __tablename__ = 'product_inquiries'
    inquiry_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    inquiry_text = db.Column(db.Text, nullable=False)
    response_text = db.Column(db.Text)
    inquiry_date = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return f'<ProductInquiry {self.inquiry_id}>'

class TableReservation(db.Model):
    __tablename__ = 'table_reservation'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='reservations')

def init_db(app):
    with app.app_context():
        db.create_all()

