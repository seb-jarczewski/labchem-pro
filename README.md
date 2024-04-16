# LabChem PRO

Labchem PRO is a web app laboratory inventory management system, based on my Labchem-db preliminary project. 

The project is currently **in development phase**, constantly improved.

## Installation

1. Clone the repository.
2. Install requirements from `requirements.txt`.
3. Run the development server.

## Usage

The home page shows welcome screen with access to the main table in read only mode for not logged in users.
Currently, only Reagent table is available - the chemical reagents inventory table.

Information you can store in the record:
- Unique ID
- Name
- CAS no.
- Capacity
- Unit
- Manufaturer
- Location in lab
- Added on
- Comment

You can login to get access to edit mode!

  You can delete any record by clicking 🗑️.

  You can edit any record by clicking ✏️.

  You can find any reagent by choosing ctrl+f.

Logged in users can add new users to the User table and new reagents to the Reagent table.

Passwords are stored as hashes.

## Improvements planned to be implemented in the near future:

- adding, editing and deleting users restricted only to Admin user,
- reset passwords by users,
- adding new, customized tables,
- adding new, customized columns in tables,
- filtering and sorting data in tables,
- exporting reports with some statistics and/or graphs,
- exporting/importing backup tables,
- css modern styling (currently a preliminary css styling is added).

## Technologies/Libraries/Packages Used

- Python
- HTML5
- CSS
- Flask
- Flask-Login
- Flask-WTF
- SQLAlchemy
- werkzeug.security

## License
Sebastian Jarczewski copyright 2024

