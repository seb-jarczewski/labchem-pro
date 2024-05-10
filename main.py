from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, EmailField
from wtforms.validators import InputRequired, EqualTo, Length
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
import secrets

# Create application (a Flask Instance)
app = Flask(__name__)

## CREATE DATABASE
# Configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///labchem.db"
# Generate secret key for each session
app.config["SECRET_KEY"] = "some_secret_key" #TODO Create randomly generated secret key with: secrets.token_hex()


db = SQLAlchemy() # Create the extension (initialize the database)
db.init_app(app) # Initialize the app with the extension

# SQLALchemy - Object Relational Mapping library - map the relationships in the database into Objects (tables as Classes, rows as Objects, fields as Object properties)

login_manager = LoginManager() # Create a Login Manager class
login_manager.init_app(app) # Initialize the app with the extension
login_manager.login_view = "login"

# Creates a user loader callback that returns the user object
@login_manager.user_loader # Load user when logged in
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

# Define my ModelView and inherit from ModelView to overwrite some parameters
class MyModelView(ModelView):
    def is_accessible(self):
        return False

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return False

admin = Admin(app, index_view=MyAdminIndexView()) # Creates admin object and add my own Admin index view to ovwerwrite
admin.add_view(MyModelView(User, db.session)) # Create ModelView for User table using sqlalchemy
admin.add_view()

class Reagent(db.Model):
    reagentid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    concentration = db.Column(db.String, nullable=False)
    manufacturer = db.Column(db.String(100), nullable=False)
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
    manufacturer = StringField("Manufacturer", validators=[InputRequired()])
    cas = StringField("CAS", validators=[InputRequired()])
    quantity = StringField("Quantity", validators=[InputRequired()])
    unit = SelectField("Unit", validators=[InputRequired()], choices=[("ml"), ("L"), ("µl"), ("g"), ("mg"), ("kg")])
    location = StringField("Location", validators=[InputRequired()])
    stock = StringField("Stock", validators=[InputRequired()]) #TODO Create separate website to set Stock with unit list etc.
    comment = StringField("Comment (optional)")
    submit = SubmitField("Add to database")




## Define routes
# Homepage route
@app.route("/")
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)

@app.route("/login", methods=["GET", "POST"])
def login():
    # Create login form
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        email = form.email.data
        login_password = form.password.data
        # Find user by email and find user's hashed password
        result = db.session.execute(db.select(User).where(User.email==email))
        user = result.scalar() # user should be an instance of 'User' class
        if user:
            login_user(user)
            if check_password_hash(user.password, login_password):
                flash("Login succesfull")
                return redirect(url_for("database"))
            else:
                flash("Wrong password. Try again.")
        else:
            flash("That email does not exist. Try again.")
    return render_template("login.html", form=form)

# Add new userroute
@app.route("/new_user", methods=["GET", "POST"])
@login_required
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
    return render_template("new_user.html", form=form, logged_in=current_user.is_authenticated)

# Database route editable
@app.route("/database")
def database():
    # Query the databese for all reagents. Convert the data into a Python list
    all_reagents = db.session.execute(db.select(Reagent))
    reagents = all_reagents.scalars().all()
    return render_template("database.html", reagents=reagents, logged_in=current_user.is_authenticated)

# Add new reagent
@app.route("/new_reagent", methods=["GET", "POST"])
@login_required
def new_reagent():
    form = NewReagentForm()
    if form.validate_on_submit():
        # Create a new record into database
        new_reagent = Reagent(
            name = form.name.data,
            concentration = form.concentration.data,
            manufacturer = form.manufacturer.data,
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
    return render_template("new_reagent.html", form=form, logged_in=current_user.is_authenticated)

# Edit existing record route
@app.route("/edit/<int:reagentid>", methods=["GET", "POST"])
@login_required
def edit(reagentid):
    reagent = db.get_or_404(Reagent, reagentid)
    form = NewReagentForm(
        name = reagent.name,
        concentration = reagent.concentration,
        manufacturer = reagent.manufacturer,
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
        reagent.manufacturer = form.manufacturer.data
        reagent.cas = form.cas.data
        reagent.quantity = form.quantity.data
        reagent.unit = form.unit.data
        reagent.location = form.location.data
        reagent.stock = form.stock.data
        reagent.comment = form.comment.data
        db.session.commit()
        return redirect(url_for("database"))
    return render_template("edit_record.html", form=form, logged_in=current_user.is_authenticated)

# Delete existing record route
@app.route("/delete/<int:reagentid>")
@login_required
def delete(reagentid):
    reagent_to_delete = db.get_or_404(Reagent, reagentid)
    db.session.delete(reagent_to_delete)
    db.session.commit()
    flash(f'You have deleted: {reagent_to_delete.name}.')
    return redirect(url_for("database"))    

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
