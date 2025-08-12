from flask import Flask , render_template , request ,url_for , flash , redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Initialize Flask application
app =Flask(__name__)

# Load environment variables from .env file
load_dotenv()

#Configure the SQLite database
app.secret_key = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'

#initialize SQLAlchemy and Migrate
db = SQLAlchemy(app)

#Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable = False)
    password = db.Column(db.String(200),nullable =False)

# Initialize database migrations
migrate = Migrate(app,db)

# Configuring the Flask application
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]

        #Check if email and password are correct
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            return redirect(url_for('welcome'))
        else:
            flash("Invalid email or password")
            return render_template("login.html") 
    return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method =="POST":
        email = request.form["email"]
        password = request.form["password"]

        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists. Please log in.")
            return render_template("login.html")
        
        #create a new user
        hashed_password = generate_password_hash(password)
        new_user = User(email = email,password= hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            return render_template("welcome.html", message = "User created successfully!")
        except Exception as e:
            return f"An error occurred while creating the user: {e}"
        
    return render_template("signup.html")


@app.route("/welcoome")
def welcome():
    return render_template("welcome.html")

#  initialize the database only one time
with app.app_context():
    db.create_all()

# or we can use the command line to create the database
# from main import db
# db.create_all()

if __name__ == "__main__":
    app.run(debug = True)
    