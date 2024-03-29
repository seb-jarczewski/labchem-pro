from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, EmailField
from wtforms.validators import InputRequired, EqualTo, Length
from datetime import datetime
import secrets

# Create application (a Flask Instance)
app = Flask(__name__)

## CREATE DATABASE
# Configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///labchem.db"
# Generate secret key for each session
app.config["SECRET_KEY"] = "super_secret_key"

# Create the extension (initialize the database)
db = SQLAlchemy()

# SQLALchemy - Object Relational Mapping library - map the relationships in the database into Objects (tables as Classes, rows as Objects, fields as Object properties)

# Initialize the app with the extension
db.init_app(app)


## CREATE TABLES
class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)

class Reagent(db.Model):
    reagentid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    concentration = db.Column(db.Float, nullable=False)
    supplier = db.Column(db.String(100), nullable=False)
    cas = db.Column(db.String(30), nullable=False)
    capacity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    # user = db.Column(db.Integer, db.ForeignKey("user.userid"), nullable=False)
    comment = db.Column(db.String(500))

# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()

##Define forms
# Define new_user form
class NewUserForm(FlaskForm):
    firstname = StringField("First Name", validators=[InputRequired()])
    lastname = StringField("Last Name", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=3)])
    password_confirm = PasswordField("Repeat Password", validators=[InputRequired(), EqualTo("password", message="Passwords must match.")])
    submit = SubmitField("Create account")

# Define new_reagent form
class NewReagentForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    concentration = StringField("Concentration", validators=[InputRequired()])
    supplier = StringField("Supplier", validators=[InputRequired()])
    cas = StringField("CAS", validators=[InputRequired()])
    capacity = StringField("Capacity", validators=[InputRequired()])
    unit = SelectField("Unit", validators=[InputRequired()], choices=[("µl"), ("ml"), ("L"), ("mg"), ("g"), ("kg")])
    location = StringField("Location", validators=[InputRequired()])
    stock = StringField("Stock", validators=[InputRequired()])
    # date = StringField("Date", validators=[InputRequired()])
    # user = StringField("User", validators=[InputRequired()])
    comment = StringField("Comment")
    submit = SubmitField("Add to database")


## Define routes
# Define homepage route
@app.route("/")
def home():
    return render_template("index.html")

# Define new_user route
@app.route("/new_user", methods=["GET", "POST"])
def new_user():
    #Create NewUserForm form
    form = NewUserForm()
    if form.validate_on_submit():
        #Create a new record into User table
        new_user = User(
            firstname = form.firstname.data,
            lastname = form.lastname.data,
            email = form.email.data,
            password = form.password.data,
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("database"))
    return render_template("new_user.html", form=form)

# Define default table database route
@app.route("/database")
def database():
    # Query the databese for all reagents. Convert the data into a Python list
    result = db.session.execute(db.select(Reagent))
    reagents = result.scalars().all()
    return render_template("database.html", reagents=reagents)

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
            capacity = form.capacity.data,
            unit = form.unit.data,
            location = form.location.data,
            stock = form.stock.data,
            date = datetime.now().strftime("%d-%m-%Y %X"),
            # user = form.user.data,
            comment = form.comment.data,
        )
        db.session.add(new_reagent)
        db.session.commit()
        return redirect(url_for("database"))
    return render_template("new_reagent.html", form=form)

# Edit exidting record
@app.route("/edit/<int:reagentid>", methods=["GET", "POST"])
def edit(reagentid):
    reagent = db.get_or_404(Reagent, reagentid)
    form = NewReagentForm(
        name = reagent.name,
        concentration = reagent.concentration,
        supplier = reagent.supplier,
        cas = reagent.cas,
        capacity = reagent.capacity,
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
        reagent.capacity = form.capacity.data
        reagent.unit = form.unit.data
        reagent.location = form.location.data
        reagent.stock = form.stock.data
        reagent.comment = form.comment.data
        db.session.commit()
        return redirect(url_for("database"))
    return render_template("edit_record.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)

