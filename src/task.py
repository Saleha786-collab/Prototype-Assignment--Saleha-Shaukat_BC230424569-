from datetime import datetime, timezone
from app import app, db  # Flask app aur db import
from model import Order  # Order model ko import

def update_order_status():
    # Flask app context ko set karenge
    with app.app_context():  # This is necessary to access the db session
        orders = Order.query.filter(Order.delivery_date <= datetime.now(timezone.utc), Order.order_status == 'pending').all()

        # Har order ka status 'delivered' mein update karenge
        for order in orders:
            order.order_status = 'delivered'  # Order ka status update karna
            db.session.commit()  # Commit karna changes ko database mein
        print(f"Updated {len(orders)} orders to 'delivered'.")

if __name__ == "__main__":
    update_order_status()
