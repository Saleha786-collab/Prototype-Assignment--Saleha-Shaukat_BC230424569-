Project Overview:
This project is an AI-powered restaurant chatbot built using Google Dialog flow, Flask (Python), and HTML/CSS and javascript. The chatbot handles customer queries like checking order status, viewing the menu, and general restaurant information.  The main goal is to provide users with an easy and efficient way to get information such as order status, product-related inquiries, and technical support through a conversational interface. It is designed to improve user experience by providing automated, real-time responses.
Key Features:
Order Status: Users can check the status of their orders by providing the order ID.


Product Information: Users can inquire about product availability, pricing, and details.


Technical Support: The chatbot assists in troubleshooting common technical issues or creates support tickets for further assistance.


Greeting & Farewell: The chatbot offers a friendly welcome and ends the conversation with a polite farewell message.

Setup Instructions:

Clone the repository:
Open your terminal and run:
https://github.com/Saleha786-collab/Prototype-Assignment--Saleha-Shaukat_BC230424569-.git
Create a Virtual Environment
python3 -m venv venv
source venv/bin/activate



Install required dependencies: Navigate to the project directory and install the necessary Python libraries.
pip install -r requirements.txt

 Run the App
python3 app.py

     3. Chatbot Dialog flow Integration Details:
Dialog flow Project: Integrated with a Dialogflow agent set up for restaurant use cases.


Intent Used: OrderStatusIntent for order checking.


Webhook: Connected via Flask backend using dialogflow_fulfillment.


Responses: Based on training phrases and entities mapped in Dialog flow.


Backend: app.py manages intent routing, response handling, and server setup.


Frontend: Simple user interface built with HTML/CSS for user interaction.

   4. Reflection and Learning:
Reflection and Learning
Through this project, I learned:
How to create a chatbot using Dialog flow and connect it with a Flask backend.


How to handle intents and webhooks programmatically.


How to style and structure HTML pages and integrate them with backend responses.


The importance of error handling and smooth conversation flow in chatbots.

Future Work
Add support for more intents like:


Book Table


Take Order


Modify Order


Cancel Order


Give Feedback


Improve the UI with better design using HTML/CSS/JavaScript.


Develop a customer dashboard with role-based access control.










