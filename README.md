# School Management System

A web-based school management system that allows administrators to manage student information and track fees.

## Features

- Admin authentication
- Add new students with automatic enrollment number generation
- Search students by enrollment number
- View detailed student information including personal details and fee status
- Track remaining fees for each student

## Setup Instructions

1. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python app.py
```

4. Open your web browser and navigate to:

```
http://localhost:5000
```

## Default Admin Credentials

- Username: admin
- Password: admin123

**Important**: Please change the default admin password after first login for security purposes.

## Database

The application uses SQLite as its database. The database file (`school.db`) will be automatically created when you first run the application.

## Security Notes

- The default admin credentials should be changed immediately after first login
- The secret key in `app.py` should be changed to a secure value before deployment
- All passwords are hashed before storage
- The application uses Flask-Login for secure session management

## Requirements

- Python 3.7 or higher
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Werkzeug
- python-dotenv
