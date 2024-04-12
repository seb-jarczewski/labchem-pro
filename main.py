from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, EmailField
from wtforms.validators import InputRequired, EqualTo, Length
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user
import secrets

# Create application (a Flask Instance)
app = Flask(__name__)

## CREATE DATABASE
# Configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///labchem.db"
# Generate secret key for each session
app.config["SECRET_KEY"] = "some_secret_key" #TODO Create randomly generated secret key with: secrets.token_hex()

# Create the extension (initialize the database)
db = SQLAlchemy()
# Initialize the app with the extension
db.init_app(app)

# SQLALchemy - Object Relational Mapping library - map the relationships in the database into Objects (tables as Classes, rows as Objects, fields as Object properties)

# Create a Login Manager class
login_manager = LoginManager()
# Initialize the app with the extension
login_manager.init_app(app)
# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def load_user(id):
    return db.get_or_404(User, id)

## CREATE TABLES
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    # reagents = db.relationship("Reagent", backref="user")

class Reagent(db.Model):
    reagentid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    concentration = db.Column(db.String, nullable=False)
    supplier = db.Column(db.String(100), nullable=False)
    cas = db.Column(db.String(30), nullable=False)
    quantity = db.Column(db.String, nullable=False)
    unit = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    # userid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comment = db.Column(db.String(500))

# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()

## Define forms
# Define login form
class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


# Define new_user form
class NewUserForm(FlaskForm):
    firstname = StringField("First Name", validators=[InputRequired()])
    lastname = StringField("Last Name", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=3)]) #TODO Set more restrictions for password
    password_confirm = PasswordField("Repeat Password", validators=[InputRequired(), EqualTo("password", message="Passwords must match.")])
    submit = SubmitField("Create account")

# Define new_reagent form
class NewReagentForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    concentration = StringField("Concentration", validators=[InputRequired()])
    supplier = StringField("Supplier", validators=[InputRequired()])
    cas = StringField("CAS", validators=[InputRequired()])
    quantity = StringField("Quantity", validators=[InputRequired()])
    unit = SelectField("Unit", validators=[InputRequired()], choices=[("µl"), ("ml"), ("L"), ("mg"), ("g"), ("kg")])
    location = StringField("Location", validators=[InputRequired()])
    stock = StringField("Stock", validators=[InputRequired()]) #TODO Create separate website to set Stock with unit list etc.
    comment = StringField("Comment (optional)")
    submit = SubmitField("Add to database")


## Define routes
# Homepage route
@app.route("/", methods=["GET", "POST"])
def home():
    # Create login form
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        # Find user by email and find user's hashed password
        user = db.get_or_404(User, email)
        pwhash = db.get_or_404(User, password)
        # Check stored password hash against entered password
        if password == pwhash:
            # Use the login_user method to log in the user
            login_user(user)
            return redirect(url_for("database")) #TODO Not found error
    return render_template("index.html", form=form)

# Add new userroute
@app.route("/new_user", methods=["GET", "POST"])
def new_user():
    #Create NewUserForm form
    form = NewUserForm()
    if form.validate_on_submit():
        # Hashing and salting the password entered by the user 
        pwhash = generate_password_hash(form.password.data, method="pbkdf2:sha256", salt_length=8)
        #Create a new record into User table
        new_user = User(
            firstname = form.firstname.data,
            lastname = form.lastname.data,
            email = form.email.data,
            password = pwhash
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("new_user.html", form=form)

# Default table database route
@app.route("/database")
def database():
    # Query the databese for all reagents. Convert the data into a Python list
    all_reagents = db.session.execute(db.select(Reagent))
    reagents = all_reagents.scalars().all()
    return render_template("database.html", reagents=reagents)

# Add new reagent
@app.route("/new_reagent", methods=["GET", "POST"])
def new_reagent():
    form = NewReagentForm()
    if form.validate_on_submit():
        # Create a new record into database
        new_reagent = Reagent(
            name = form.name.data,
            concentration = form.concentration.data,
            supplier = form.supplier.data,
            cas = form.cas.data,
            quantity = form.quantity.data,
            unit = form.unit.data,
            location = form.location.data,
            stock = form.stock.data,
            date = datetime.now().strftime("%d-%m-%Y"),
            # userid = 1, #TODO Change the code to use logged in user
            comment = form.comment.data,
        )
        db.session.add(new_reagent)
        db.session.commit()
        return redirect(url_for("database"))
    return render_template("new_reagent.html", form=form)

# Edit existing record route
@app.route("/edit/<int:reagentid>", methods=["GET", "POST"])
def edit(reagentid):
    reagent = db.get_or_404(Reagent, reagentid)
    form = NewReagentForm(
        name = reagent.name,
        concentration = reagent.concentration,
        supplier = reagent.supplier,
        cas = reagent.cas,
        quantity = reagent.quantity,
        unit = reagent.unit,
        location = reagent.location,
        stock = reagent.stock,
        comment = reagent.comment,
    )
    if form.validate_on_submit():
        reagent.name = form.name.data
        reagent.concentration = form.concentration.data
        reagent.supplier = form.supplier.data
        reagent.cas = form.cas.data
        reagent.quantity = form.quantity.data
        reagent.unit = form.unit.data
        reagent.location = form.location.data
        reagent.stock = form.stock.data
        reagent.comment = form.comment.data
        db.session.commit()
        return redirect(url_for("database"))
    return render_template("edit_record.html", form=form)

# Delete existing record route
@app.route("/delete/<int:reagentid>")
def delete(reagentid):
    reagent_to_delete = db.get_or_404(Reagent, reagentid)
    db.session.delete(reagent_to_delete)
    db.session.commit()
    flash(f'You have deleted: {reagent_to_delete.name}.')
    return redirect(url_for("database"))


if __name__ == "__main__":
    app.run(debug=True)


