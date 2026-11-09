# Expense Tracker

A multi-user expense tracking web application built using **Python and Flask** to manage daily expenses, track monthly spending, and monitor budgets.

🌐 **Live Website:** https://zohebkhan.pythonanywhere.com/

## Features

- User registration and login
- Password hashing for secure authentication
- Add and delete expenses
- Categorize expenses
- Monthly spending overview
- Monthly budget tracking
- Expense visualization using charts
- Separate expense data for each user

## Technologies Used

- **Python** – Backend programming
- **Flask** – Web framework
- **SQLite** – User authentication and database management
- **JSON** – Expense and budget data storage
- **HTML & CSS** – Frontend development
- **Matplotlib** – Data visualization

## Project Structure

```text
expense-tracker/
│
├── website.py
├── expense_code.py
├── templates/
│   ├── index.html
│   ├── login.html
│   └── register.html
│
└── .gitignore
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/zohebkhan1707/expense-tracker.git
```

### 2. Navigate to the project folder

```bash
cd expense-tracker
```

### 3. Install dependencies

```bash
pip install flask werkzeug matplotlib
```

### 4. Configure the Flask secret key

Set the `FLASK_SECRET_KEY` environment variable before running the application.

### 5. Run the application

```bash
python website.py
```

Open the local address displayed in your terminal to access the application.

## Deployment

The application is deployed using **PythonAnywhere**.

🌐 https://zohebkhan.pythonanywhere.com/

## Author

**Md Zoheb Khan**

- GitHub: [@zohebkhan1707](https://github.com/zohebkhan1707)

---

Developed as a learning project to gain practical experience in Python programming, web development, database management, authentication, and deployment.
