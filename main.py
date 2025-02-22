import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# Database Setup
def setup_database():
    conn = sqlite3.connect("shifts.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT NOT NULL,
            shift_date TEXT NOT NULL,
            shift_time TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# User Registration
def register():
    username = entry_username.get()
    password = entry_password.get()
    role = role_var.get()
    
    if username and password:
        conn = sqlite3.connect("shifts.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            messagebox.showinfo("Success", "User registered successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        conn.close()
    else:
        messagebox.showerror("Error", "All fields are required")

# Login Function
def login():
    username = entry_username.get()
    password = entry_password.get()
    
    conn = sqlite3.connect("shifts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        login_window.destroy()
        open_main_window(user[0])
    else:
        messagebox.showerror("Error", "Invalid username or password")

# Functions for Manager
def add_shift():
    employee = entry_employee.get()
    date = entry_date.get()
    time = entry_time.get()
    if employee and date and time:
        conn = sqlite3.connect("shifts.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO shifts (employee_name, shift_date, shift_time) VALUES (?, ?, ?)", (employee, date, time))
        conn.commit()
        conn.close()
        view_shifts()
    else:
        messagebox.showerror("Error", "All fields are required")

def view_shifts():
    for row in shift_tree.get_children():
        shift_tree.delete(row)
    conn = sqlite3.connect("shifts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shifts")
    for row in cursor.fetchall():
        shift_tree.insert("", "end", values=row)
    conn.close()

def delete_shift():
    selected_item = shift_tree.selection()
    if selected_item:
        shift_id = shift_tree.item(selected_item)['values'][0]
        conn = sqlite3.connect("shifts.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shifts WHERE id=?", (shift_id,))
        conn.commit()
        conn.close()
        view_shifts()
    else:
        messagebox.showerror("Error", "Select a shift to delete")

def update_shift():
    selected_item = shift_tree.selection()
    if selected_item:
        shift_id = shift_tree.item(selected_item)['values'][0]
        employee = entry_employee.get()
        date = entry_date.get()
        time = entry_time.get()
        if employee and date and time:
            conn = sqlite3.connect("shifts.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE shifts SET employee_name=?, shift_date=?, shift_time=? WHERE id=?", (employee, date, time, shift_id))
            conn.commit()
            conn.close()
            view_shifts()
        else:
            messagebox.showerror("Error", "All fields are required")
    else:
        messagebox.showerror("Error", "Select a shift to update")

def logout():
    root.destroy()
    open_login_window()

def open_main_window(role):
    global root, entry_employee, entry_date, entry_time, shift_tree
    
    root = tk.Tk()
    root.title("Employee Shift Management")
    root.geometry("600x400")
    
    if role == "Manager":
        frame = tk.Frame(root)
        frame.pack(pady=10)
        
        tk.Label(frame, text="Employee Name").grid(row=0, column=0)
        tk.Label(frame, text="Shift Date").grid(row=1, column=0)
        tk.Label(frame, text="Shift Time").grid(row=2, column=0)
        
        entry_employee = tk.Entry(frame)
        entry_employee.grid(row=0, column=1)
        entry_date = tk.Entry(frame)
        entry_date.grid(row=1, column=1)
        entry_time = tk.Entry(frame)
        entry_time.grid(row=2, column=1)
        
        tk.Button(frame, text="Add Shift", command=add_shift).grid(row=3, column=0, columnspan=2)
        tk.Button(frame, text="Update Shift", command=update_shift).grid(row=4, column=0, columnspan=2)
        tk.Button(frame, text="Delete Shift", command=delete_shift).grid(row=5, column=0, columnspan=2)
    
    tk.Button(root, text="Logout", command=logout).pack()
    
    shift_tree = ttk.Treeview(root, columns=("ID", "Employee", "Date", "Time"), show="headings")
    shift_tree.heading("ID", text="ID")
    shift_tree.heading("Employee", text="Employee")
    shift_tree.heading("Date", text="Date")
    shift_tree.heading("Time", text="Time")
    shift_tree.pack(pady=10)
    
    view_shifts()
    root.mainloop()

def open_login_window():
    global login_window, role_var, entry_username, entry_password
    login_window = tk.Tk()
    login_window.title("Login / Signup")
    login_window.geometry("300x300")
    
    tk.Label(login_window, text="Select Role:").pack(pady=10)
    role_var = tk.StringVar(value="Employee")
    tk.Radiobutton(login_window, text="Manager", variable=role_var, value="Manager").pack()
    tk.Radiobutton(login_window, text="Employee", variable=role_var, value="Employee").pack()
    
    tk.Label(login_window, text="Username:").pack()
    entry_username = tk.Entry(login_window)
    entry_username.pack()
    
    tk.Label(login_window, text="Password:").pack()
    entry_password = tk.Entry(login_window, show="*")
    entry_password.pack()
    
    tk.Button(login_window, text="Login", command=login).pack(pady=5)
    tk.Button(login_window, text="Signup", command=register).pack(pady=5)
    
    login_window.mainloop()

setup_database()
open_login_window()
