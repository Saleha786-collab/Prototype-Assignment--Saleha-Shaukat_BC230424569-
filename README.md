This project is an AI-powered restaurant chatbot built using Google Dialogflow, Flask (Python), and HTML/CSS with JavaScript. The chatbot handles customer requests like checking order status, reserving tables, and asking about menu items. It aims to simplify customer service by giving instant, helpful answers.
Repo Structure Note: The repository includes docs and schema folders first for documentation and database design clarity, followed by the src folder which contains all the core source code (app.py, model.py, etc.).
Key Features Order Status Users can ask for their order update by sharing the order ID.
Product Information Bot tells if a menu item is available and its price.
Table Reservation User gives date, time, and guests, and the bot books the table.
Technical Support When users face issues, the bot creates support tickets.
Greetings & Farewells Friendly messages at the start and end of each chat.
How to Set Up Clone this repository



Step 1: Clone the Repository
https://github.com/Saleha786-collab/Prototype-Assignment--Saleha-Shaukat_BC230424569-.git cd Prototype-Assignment--Saleha-Shaukat_BC230424569- 
Step 2: Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
Step 3: Install Dependencies
pip install -r requirements.txt 
Step 4: Run the Flask app
python3 app.py 



Dialogflow Integration Agent: Set up in Dialogflow for restaurant-specific needs
Webhook: Connected to Flask for backend logic
Handled Intents:
Order status checking
Placing orders
Table reservations
Reporting issues
Responses: Controlled through Flask and returned based on Dialogflow input
What I Learned Building a chatbot with Dialogflow + Flask integration
Handling user intents and context with webhooks
Querying and updating a real database through conversational input
Designing smooth, user-friendly chatbot flows 
Future Improvements Add more chatbot features like:
Let users cancel or change their orders
Ask users for feedback after a chat
Improvements for Fast Food Orders:
Suggest popular combos and meal deals
Help users quickly reorder their past meals
Support large group orders for parties or events
Show calorie details for food items
Recommend extras like fries, drinks, or sauces
Make the website look better and work well on mobile phones

