import sqlite3
import json
import os

import matplotlib.pyplot as plt
def get_user_file(user_id, file_type):
    filename = f"user_{user_id}_{file_type}.json"
    return os.path.join("user_data", filename)
def get_connection():
    conn=sqlite3.connect("expenses.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
def create_tables():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(''' 
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE NOT NULL,
email TEXT UNIQUE NOT NULL,
password TEXT NOT NULL)
    ''')
    cursor.execute('''
CREATE TABLE IF NOT EXISTS expenses (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER NOT NULL,
amount REAL NOT NULL,
category TEXT NOT NULL,
description TEXT,
date TEXT NOT NULL,
FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    conn.commit()
    conn.close()
from werkzeug.security import generate_password_hash
def register_user(username,email,password):
    conn=get_connection()
    cursor=conn.cursor()
    hashed_password=generate_password_hash(password)
    cursor.execute('''INSERT INTO users(username,email,password) 
    VALUES(?,?,?)
    ''',(username,email,hashed_password))
    conn.commit()
    conn.close()
from werkzeug.security import check_password_hash
def login_user(email,password):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE email=?
    ''',(email,))
    user=cursor.fetchone()
    conn.close()
    if user is None:
        return None
    if check_password_hash(user[3],password):
        return user
    return None

    
    


Budget_file="budgets.json"
def load_budgets(user_id):
    filename=get_user_file(user_id, "budgets")
    try:
        with open(filename,"r") as file:
            return json.load(file)

    except FileNotFoundError:
        return {}

def save_budgets(user_id,budgets):
    filename=get_user_file(user_id, "budgets")
    with open(filename,"w") as file:
        json.dump(budgets,file,indent=4)

File_name="expenses.json"


def load_expenses(user_id):
    file_name=get_user_file(user_id, "expenses")
    try:
        with open(file_name,"r") as file:
            return json.load(file)

    except FileNotFoundError:
        return []

def save_expenses(user_id,expenses):
    file_name=get_user_file(user_id, "expenses")
    with open(file_name,"w") as file:
        json.dump(expenses,file,indent=4)

def add_expenses(expenses):
    while True:
        try:
            amount = float(input("Enter amount: ₹"))
            if amount <= 0:
                print("Amount must be greater than zero. Please try again.")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a valid number for the amount.")

   
    category = input("Enter category: ")

    description = input("Enter description: ")

    date = input("Enter date (DD-MM-YYYY): ")
    if expenses:
        new_id=max(expense["id"] for expense in expenses)+1
    else:
        new_id=1


    expense={
        "id":new_id,
        "amount":amount,
        "category":category,
        "description":description,
        "date":date
              }
    expenses.append(expense)
    save_expenses(expenses)
    print("\nExpense added successfully!")

def view_expenses(expenses):
    if not expenses:
        print("No Expenses Found")

    else:
        for expense in expenses:
            print(
                f"ID:{expense['id']} | "
                f"Rs.:{expense['amount']} | "
                f"{expense['category']} | "
                f"{expense['description']} | "
                f"{expense['date']}"
            )
            

# Function For Terminal
def delete_expenses(expenses):
    if not expenses:
        print("No Expenses To Delete")

    else:
        expense_id=int(input("Enter the Id number You Want To Delete:"))
        for expense in expenses:
            if expense["id"]==expense_id:
                expenses.remove(expense)
                save_expenses(expenses)
                print("Expenses deleted succesfully!")
                break

        else:
            print("Expense ID not found")


# Function for website
def delete_expense_by_id(user_id,expenses, expense_id):
    for expense in expenses:
        if expense["id"] == expense_id:
            expenses.remove(expense)
            save_expenses(user_id,expenses)
            return True

    return False

def total_expenses(expenses):
    total=0
    for expense in expenses:
        total+=expense["amount"]

    print(f"The total spendings are: {total:.2f}")

def category_summary(expenses):
    if not expenses:
        print("No Expenses Found")

    else:
        categories={}
        for expense in expenses:
            category=expense["category"]
            amount=expense["amount"]
            if category in categories:
                categories[category]+=amount

            else:
                categories[category]=amount

        print("\n======= CATEGORY SUMMARY =======")
        for category,amount in categories.items():
            print(f"{category}:₹{amount:.2f}")

def category_graph(expenses):
    if not expenses:
        print("No Expenses Found")

    else:
        categories={}
        for expense in expenses:
            category=expense["category"]
            amount=expense["amount"]
            if category in categories:
                categories[category]+=amount

            else:
                categories[category]=amount

        plt.bar(categories.keys(),categories.values())
        plt.title("Spending by Category")
        plt.xlabel("Category")
        plt.ylabel("Amount (₹)")
        plt.show()


def monthly_graph(expenses):
    if not expenses:
        print("No Expenses Found")

    else:
        months={}
        for expense in expenses:
            month=expense['date'][3:]
            amount=expense["amount"]
            if month in months:
                months[month]+=amount
            else:
                months[month]=amount

        plt.bar(months.keys(),months.values())
        plt.title("Monthly Spendings")
        plt.xlabel("Month")
        plt.ylabel("Amount (₹)")
        plt.show()



def edit_expenses(expenses):
    if not expenses:
        print("No Expenses to Edit")

    else:
        expense_id=int(input("Enter the ID of the expense you want to edit:"))
        for expense in expenses:
            if expense["id"]==expense_id:

                print("\nWhat do you want to edit?")
                print("1. Amount")
                print("2. Category")
                print("3. Description")
                print("4. Date")

                edit_choice=int(input("Enter your choice (1-4):"))
                if edit_choice==1:
                    expense['amount']=float(input("Enter a new amount:₹"))
                elif edit_choice==2:
                    expense['category']=input("Enter a new category:")
                elif edit_choice==3:
                    expense['description']=input("Enter a new description:")
                elif edit_choice==4:
                    expense['date']=input("Enter a new date (DD-MM-YYYY):")
                
                else:
                    print("Invalid choice,Please Select from 1-4")
                    return

                save_expenses(expenses)
                print("Expense updated successfully!")
                return

            else:
                print("Expense ID not found")


def search_expenses(expenses):
    if not expenses:
        print("No Expenses Found")

    else:
        found=False
        search=input("Enter category or description to search for:").lower()
        for expense in expenses:
           if search in expense["category"].lower() or search in expense["description"].lower():
               print(
                   f"ID:{expense["id"]} |" 
                   f"Rs.:{expense["amount"]} |" 
                   f"{expense["category"]} |" 
                   f"{expense["description"]} |" 
                   f"{expense["date"]}"
               )

               found=True
           if not found:
               print("No matching expenses found.")


def monthly_summary(expenses):
    if not expenses:
        print("No Expenses Found")

    else:
        month=input("Enter the month (MM-YYYY):")
        total_monthly=0
        found=False
        for expense in expenses:
            if expense['date'][3:]==month:
                total_monthly +=expense["amount"]
                found=True

        if found:
            print(f"The total spendings for {month} are: rs.{total_monthly:.2f}")

        else:
        
            print("No expenses found for the specified month or invalid date format.")
    

def set_budget(budgets):
    month = input("Enter the month (MM-YYYY): ")
    while True:
        try:
            budget=float(input("Enter Your Budget:₹"))
            if budget<=0:
                print("Budget must be greater than zero. Please try again.")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a valid number for the budget.")

    budgets[month] = budget
    save_budgets(budgets)
    
    print(f"Budget for {month} set successfully: ₹{budget:.2f}")


def check_budget(expenses, budgets):
    month = input("Enter the month (MM-YYYY) to check budget: ")
    if month not in budgets:
        print(f"No budget set for {month}. Please set a budget first.")
    else:
        budget = budgets[month]
        total_monthly=0
        for expense in expenses:
            if expense['date'][3:]==month:
                total_monthly +=expense["amount"]


        print("\n======= BUDGET STATUS =======")
        print(f"Budget: ₹{budget:.2f}")
        print(f"Spent: ₹{total_monthly:.2f}")

        if total_monthly > budget:
            print("You have exceeded your budget!")
        elif total_monthly == budget:
            print("You have reached your budget limit.")
        else:
            print(f"You are within your budget. You have ₹{budget - total_monthly:.2f} remaining.")



def add_expense_from_gui(user_id,expenses, amount, category, description, date):
    if expenses:
        new_id = max(expense["id"] for expense in expenses) + 1
    else:
        new_id = 1

    expense = {
        "id": new_id,
        "amount": float(amount),
        "category": category,
        "description": description,
        "date": date
    }

    expenses.append(expense)
    save_expenses(user_id,expenses)

# function for website
# def edit_expense_by_id(expenses,expense_id,amount,category,description):
#     for expense in expenses:
#          if expense["id"] == expense_id:
#             expense["amount"] = float(amount)
#             expense["category"] = category
#             expense["description"] = description
#             save_expenses(expenses)
#             return True
#     return False






            

if __name__ == "__main__":
    create_tables()
    expenses=load_expenses() 
    budgets=load_budgets()

    while True:


        
        print("===== EXPENSE TRACKER =====")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Delete Expense")
        print("4. Total Expenses")
        print("5. Category Summary")
        print("6. Edit Expenses")
        print("7. Search Expenses")
        print("8. Monthly Summary")
        print("9. Set Budget")
        print("10. Check Budget")
        print("11. Category Graph")
        print("12. Monthly Graph")
        print("13. Exit")

        







        choice = int(input("Enter your choice (1-13): "))
        if choice ==1:
            print("Add Expense")
            add_expenses(expenses)
        elif choice ==2:
            print("View Expenses")
            view_expenses(expenses)

        elif choice ==3:
            print("Delete Expense")
            delete_expenses(expenses)

        elif choice ==4:
            print("Total Spending")
            total_expenses(expenses)
        elif choice ==5:
            print("Category Summary")
            category_summary(expenses)

        elif choice ==6:
            print("Edit Expenses")
            edit_expenses(expenses)

        elif choice ==7:
            print("Search Expenses")
            search_expenses(expenses)

        elif choice ==8:
            print("Monthly Summary")
            monthly_summary(expenses)

        elif choice ==9:
            print("Set Budget")
            set_budget(budgets)

        elif choice ==10:
            print("Check Budget")
            check_budget(expenses, budgets)

        elif choice ==11:
            print("Category Graph")
            category_graph(expenses)

        elif choice ==12:
            print("Monthly Graph")
            monthly_graph(expenses)
            

        elif choice ==13:
            print("Goodbye!")
            break

        else:
            print("Invalid choice.")


