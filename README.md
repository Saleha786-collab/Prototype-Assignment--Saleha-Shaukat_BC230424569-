## Setup Instructions

## Clone the repository:

https://github.com/Saleha786-collab/Prototype-Assignment--Saleha-Shaukat_BC230424569-.git

cd Prototype-Assignment--Saleha-Shaukat_BC230424569- 

 ## Create and activate a virtual environment:

python -m venv venv

For Mac: source venv/bin/activate And for Windows: venv\Scripts\activate

 ## Install dependencies:

pip install -r requirements.txt

## Open your project folder and go to src/app.py
 Find the line with database settings and change it to:


python
CopyEdit
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/db'

Replace password with your real MySQL password.
## Set up your MySQL database:

Open MySQL

Create a database named db

Import the database file:

mysql -u root -p db < db/db.sql

## Run Instructions
Go to the src folder
cd src
## Run your Flask app
python app.py
     Your chatbot will run on:
     http://127.0.0.1:5000/home





