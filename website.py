from datetime import date,datetime
import sqlite3

from expense_code import create_tables,load_expenses,add_expense_from_gui,delete_expense_by_id,delete_expenses,load_budgets,save_budgets,register_user,login_user
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
from flask import Flask, json, render_template,request,url_for,redirect,session
from werkzeug.security import generate_password_hash, check_password_hash
app=Flask(__name__)
create_tables()
app.secret_key = "3e11907399be46cb271eec301f114eed11ab71bad3064278091ae366c9d40f2d"
def load_users():
    try:
        with open("users.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
def save_users(users):
    with open("users.json", "w") as file:
        json.dump(users, file, indent=4)

# def register_user(username,email,password):
#     users =load_users()
#     for user in users:
#         if user["email"]==email:
#             return False

#     new_user={
#         "id": max([user["id"] for user in users], default=0)+1,
#         "username": username,
#         "email": email,
#         "password": generate_password_hash(password)
#     }

#     users.append(new_user)
#     save_users(users)
#     return True
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        

        try:
            register_user(username, email, password)
            return redirect(url_for("login"))
        
        
        except sqlite3.IntegrityError:
            return "Email already exists. Please use a different email."

    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = login_user(email, password)

        if user is not None:
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect(url_for("home"))
    
        return "Invalid email or password!"

    return render_template("login.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
@app.route('/')
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    expenses = load_expenses(user_id)

    selected_category = request.args.get("category", "")
    total = sum(expense["amount"] for expense in expenses)
    transactions = len(expenses)
    current_month=date.today().strftime("%m-%Y")
    monthly_spending=sum(
        expense["amount"]
        for expense in expenses
        if expense["date"][3:]==current_month)

    
    budgets=load_budgets(user_id)
    current_budget=budgets.get(current_month,0)
    remaining_budget=current_budget-monthly_spending
    if current_budget > 0:
        budget_percentage = (monthly_spending / current_budget) * 100
    else:
        budget_percentage = 0
    budget_bar_width = min(budget_percentage, 100)
    if budget_percentage < 80:
        budget_color = "#22c55e"
    elif budget_percentage <= 100:
        budget_color = "#eab308"
    else:
        budget_color = "#ef4444"
    if current_budget <= 0:
        budget_status = "Set a monthly budget to track spending."
    elif remaining_budget < 0:
        budget_status = "Budget exceeded!"
    elif remaining_budget <= current_budget * 0.2:
        budget_status = "Warning: You have used 80% or more of your budget."
    else:
        budget_status = "You are within your budget." 





    category_totals={}
    for expense in expenses:
        category=expense["category"].strip().lower().title()
        amount=expense["amount"]
        if category in category_totals:
            category_totals[category]+=amount

        else:
            category_totals[category]=amount


    displayed_expenses=[]
    if selected_category:
        for expense in expenses:
            if expense["category"].lower()==selected_category.lower():
                displayed_expenses.append(expense)
    else:
        displayed_expenses=expenses  




    category_chart=None
    if category_totals:
        fig,ax=plt.subplots()
        ax.pie(
            category_totals.values(),
            labels=category_totals.keys(),
            autopct="%1.1f%%",
            startangle=90,
            textprops={"color":"white"}
        )
        ax.set_title("Spending by Category")
        fig.patch.set_alpha(0)
        ax.set_facecolor("none")

        ax.set_title(
            "Spending by Category",
            color="white"
        )

        ax.tick_params(colors="white")

        image_buffer=io.BytesIO()
        fig.savefig(image_buffer,format="png",bbox_inches="tight",transparent=True)
        image_buffer.seek(0)


        category_chart=base64.b64encode(
            image_buffer.getvalue()
        ).decode("utf-8")


        plt.close(fig)

    monthly_totals={}
    for expense in expenses:
        expense_date=datetime.strptime(
            expense["date"],"%d-%m-%Y"
        )
        month=expense_date.strftime("%b-%Y")
        monthly_totals[month]=(
            monthly_totals.get(month,0) + expense["amount"]
        )


    monthly_chart=None
    if monthly_totals:
        fig,ax=plt.subplots()
        ax.bar(
            monthly_totals.keys(),
            monthly_totals.values()
        )
        ax.set_title("Monthly Spending", color="white")
        ax.set_ylabel("Amount (₹)", color="white")
        ax.tick_params(axis="x", colors="white", rotation=45)
        ax.tick_params(axis="y", colors="white")

        fig.patch.set_alpha(0)
        ax.set_facecolor("none")
        fig.tight_layout()


        image_buffer=io.BytesIO()
        fig.savefig(
            image_buffer,
            format="png",
            bbox_inches="tight",
            transparent=True

        )
        image_buffer.seek(0)
        monthly_chart=base64.b64encode(
            image_buffer.getvalue()
        ).decode("utf-8")

        plt.close(fig)






    



    return render_template("index.html", total=total,current_budget=current_budget,budget_color=budget_color,expenses=displayed_expenses,transactions=transactions,monthly_spending=monthly_spending,remaining_budget=remaining_budget,budget_status=budget_status,category_totals=category_totals,category_chart=category_chart,monthly_chart=monthly_chart,budget_percentage=budget_percentage,budget_bar_width=budget_bar_width)
@app.route("/add", methods=["POST"])
def add_expense():
    if "user_id" not in session:    
        return redirect(url_for("login"))
    amount_text=(request.form["amount"])
    category=request.form["category"]
    description=request.form["description"]
    try:
        amount = float(amount_text)
    except ValueError:
        return "Invalid amount. Please enter a valid number."

    if amount <= 0:
        return "Amount must be greater than zero."

    user_id = session["user_id"]

    expenses = load_expenses(user_id)

    add_expense_from_gui(
        user_id,
        expenses,
        amount,
        category,
        description,
        date.today().strftime("%d-%m-%Y")
    )
    return redirect(url_for("home"))
@app.route("/delete/<int:expense_id>",methods=["POST"])
def delete_expenses(expense_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id=session["user_id"]
    expenses=load_expenses(user_id)
    delete_expense_by_id(user_id,expenses,expense_id)
    return redirect(url_for("home"))


# @app.route("/edit/<int:expense_id>", methods=["Post"])
# def edit_expense(expense_id):
#     expenses=load_expenses
#     amount=request.form.get("amount","").strip()
#     category=request.form.get("category","").strip()
#     description=request.form.get("description","").strip()
#     if not amount or not category or not description:
#         return "All fields are required.", 400

#     try:
#         amount = float(amount)
#         if amount <= 0:
#             return "Amount must be greater than zero.", 400
#     except ValueError:
#         return "Enter a valid amount.", 400

#     success=edit_expense_by_id(expenses,expense_id,amount,category,description)

#     if not success:
#         return "Expense not found.", 404

#     return redirect(url_for("home"))




@app.route("/setbudget", methods=["Post"])
def setbudget():
    if "user_id" not in session:
        return redirect(url_for("login"))
    budget_text=request.form["budget"]
    try:
        budget=float(budget_text)
    except ValueError:
        return "Please Enter A Valid Budget"
    if budget<=0:
        return "Budget Must Be greater Than Zero"
    else:
        user_id=session["user_id"]
        budgets=load_budgets(user_id)
        current_month=date.today().strftime("%m-%Y")
        budgets[current_month]=budget
        save_budgets(user_id,budgets)

        return redirect(url_for("home"))





         

    
    
   


if __name__=="__main__":
    
    app.run(debug=True)