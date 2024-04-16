# LabChem PRO

Labchem PRO is a web app laboratory inventory system, based on my Labchem-db preliminary project. 

The project is currently **in development phase**, constantly improved.

## Installation

1. Clone the repository.
2. Install requirements from `requirements.txt`.
3. Run the development server.

## Usage

The main page shows the welcome screen with access to the main table in read only mode for not logged in users.
Currently, only one table is available - the chemical reagents inventory table.

You can log in to get access to the edit mode.

You can delete any record by clicking 🗑️.
You can edit any record by clicking ✏️.
You can find any reagent by choosing ctrl+f.

Logged in users can add new users to the User table and new reagents to the Reagent table.
Passwords are stored as hashes.

**Improvements planned to be implemented:**

- adding, editing and deleting users restricted only to Admin user,
- changing passwords by users,
- adding new, customized tables,
- adding new, customized columns in tables,
- dynamic filtering and sorting data in tables,
- alerts about stock levels,
- exporting reports,
- exporting/importing backup files,

## Technologies Used

- Python
- HTML 5
- CSS
- Flask
- Flask-Login
- Flask-WTF
- SQL
- SQLAlchemy
- 

## License


