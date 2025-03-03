import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime


# Database Connection
def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost", user="root", password="root", database="finance_db"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error connecting to database: {err}")
        return None


def create_table():
    db = connect_db()
    if db:
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                amount DECIMAL(10,2),
                category VARCHAR(255),
                date DATE,
                transaction_type ENUM('income', 'expense')
            )
        """)
        db.commit()
        db.close()


# Add Transaction
def add_transaction():
    amount = amount_entry.get().strip()
    category = category_entry.get().strip()
    date = date_entry.get().strip()
    transaction_type = transaction_type_var.get()

    # Validate input
    if not amount or not category or not date:
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
    except ValueError:
        messagebox.showerror("Error", "Invalid amount. Enter a positive number.")
        return

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
        return

    db = connect_db()
    if db:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO transactions (amount, category, date, transaction_type) VALUES (%s, %s, %s, %s)",
            (amount, category, date, transaction_type)
        )
        db.commit()
        db.close()
        messagebox.showinfo("Success", "Transaction added successfully")
        update_summary()
        update_transaction_list()


# Update Summary
def update_summary():
    db = connect_db()
    if db:
        cursor = db.cursor()
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE transaction_type='income'")
        income = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE transaction_type='expense'")
        expenses = cursor.fetchone()[0] or 0
        db.close()
        balance = income - expenses
        summary_label.config(text=f"Income: ${income:.2f} | Expenses: ${expenses:.2f} | Balance: ${balance:.2f}")


# Fetch and display transactions
def update_transaction_list():
    db = connect_db()
    if db:
        cursor = db.cursor()
        cursor.execute("SELECT amount, category, date, transaction_type FROM transactions ORDER BY date DESC")
        rows = cursor.fetchall()
        db.close()

        # Clear existing data
        for row in transaction_tree.get_children():
            transaction_tree.delete(row)

        # Insert new data
        for row in rows:
            transaction_tree.insert("", "end", values=row)


# GUI Setup
root = tk.Tk()
root.title("Personal Finance Tracker")
root.geometry("500x450")
root.resizable(False, False)
root.configure(bg="#f0f0f0")  # Set background color

# Inputs Frame
frame = tk.Frame(root, padx=10, pady=10, bg="#f0f0f0")
frame.pack()

tk.Label(frame, text="Amount:", bg="#f0f0f0").grid(row=0, column=0, sticky="w")
amount_entry = tk.Entry(frame)
amount_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Category:", bg="#f0f0f0").grid(row=1, column=0, sticky="w")
category_entry = tk.Entry(frame)
category_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame, text="Date (YYYY-MM-DD):", bg="#f0f0f0").grid(row=2, column=0, sticky="w")
date_entry = tk.Entry(frame)
date_entry.grid(row=2, column=1, padx=5, pady=5)

transaction_type_var = tk.StringVar(value="income")
tk.Radiobutton(frame, text="Income", variable=transaction_type_var, value="income", bg="#f0f0f0").grid(row=3, column=0,
                                                                                                       sticky="w")
tk.Radiobutton(frame, text="Expense", variable=transaction_type_var, value="expense", bg="#f0f0f0").grid(row=3,
                                                                                                         column=1,
                                                                                                         sticky="w")

add_button = tk.Button(frame, text="Add Transaction", command=add_transaction, bg="#d9ead3")
add_button.grid(row=4, columnspan=2, pady=5)

# Summary
summary_label = tk.Label(root, text="Income: $0.00 | Expenses: $0.00 | Balance: $0.00", font=("Arial", 12, "bold"),
                         bg="#f0f0f0")
summary_label.pack(pady=5)

# Transaction List
columns = ("Amount", "Category", "Date", "Type")
transaction_tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    transaction_tree.heading(col, text=col)
transaction_tree.pack(fill="both", expand=True, padx=10, pady=5)

# Initialize
create_table()
update_summary()
update_transaction_list()

root.mainloop()