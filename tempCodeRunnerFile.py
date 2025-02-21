import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import re

# Database Setup
def init_db():
    conn = sqlite3.connect("shifts.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee TEXT,
            shift_time TEXT,
            manager TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Main App Class
class ShiftManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Shift Management System")
        self.root.geometry("600x500")
        self.current_user = None
        self.role = None
        self.create_login_page()
    
    # Aaryaman - User Login & Signup
    def create_login_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title
        tk.Label(self.root, text="Welcome to Employee Shift Management System", font=("Arial", 16, "bold")).pack(pady=20)

        # Username and Password Inputs
        tk.Label(self.root, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)

        tk.Label(self.root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)
        
        # Role Selection
        self.role_var = tk.StringVar(value="employee")
        tk.Radiobutton(self.root, text="Employee", variable=self.role_var, value="employee").pack(pady=5)
        tk.Radiobutton(self.root, text="Manager", variable=self.role_var, value="manager").pack(pady=5)
        
        # Buttons
        tk.Button(self.root, text="Login", command=self.login, width=20).pack(pady=10)
        tk.Button(self.root, text="Signup", command=self.signup, width=20).pack(pady=10)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        conn = sqlite3.connect("shifts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.current_user = user[1]
            self.role = user[3]
            self.create_dashboard()
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        conn = sqlite3.connect("shifts.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                           (username, password, role))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        conn.close()

    # Microsoft Shift Management Dashboard
    def create_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Dashboard Header
        tk.Label(self.root, text=f"Welcome {self.current_user} ({self.role})", font=("Arial", 14, "bold")).pack(pady=20)

        if self.role == "manager":
            tk.Button(self.root, text="View All Shifts", command=self.view_shifts, width=30).pack(pady=10)
            tk.Button(self.root, text="Add Shift", command=self.add_shift, width=30).pack(pady=10)
            tk.Button(self.root, text="Update Shift", command=self.update_shift, width=30).pack(pady=10)
            tk.Button(self.root, text="Delete Shift", command=self.delete_shift, width=30).pack(pady=10)
            tk.Button(self.root, text="View Employee Shifts", command=self.view_employee_shifts, width=30).pack(pady=10)
        else:
            tk.Button(self.root, text="View My Shifts", command=self.view_shifts, width=30).pack(pady=10)

        tk.Button(self.root, text="Logout", command=self.create_login_page, width=30).pack(pady=20)

    # View Shifts for Employees and Managers
    def view_shifts(self):
        conn = sqlite3.connect("shifts.db")
        cursor = conn.cursor()

        if self.role == "employee":
            cursor.execute("SELECT * FROM shifts WHERE employee=?", (self.current_user,))
        else:
            cursor.execute("SELECT * FROM shifts")

        shifts = cursor.fetchall()
        conn.close()

        view_window = tk.Toplevel(self.root)
        view_window.title("Shifts")

        tk.Label(view_window, text="Shift Schedule", font=("Arial", 14, "bold")).pack(pady=10)

        if shifts:
            for shift in shifts:
                tk.Label(view_window, text=f"Shift ID: {shift[0]}, Employee: {shift[1]}, Time: {shift[2]}, Manager: {shift[3]}").pack(pady=5)
        else:
            tk.Label(view_window, text="No shifts available.").pack(pady=10)

    # View Shifts for Manager to filter by Employee
    def view_employee_shifts(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("View Employee Shifts")
        
        tk.Label(view_window, text="Enter Employee Name:").pack(pady=5)
        emp_name_entry = tk.Entry(view_window)
        emp_name_entry.pack(pady=5)

        def filter_shifts():
            emp_name = emp_name_entry.get()
            conn = sqlite3.connect("shifts.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM shifts WHERE employee=?", (emp_name,))
            shifts = cursor.fetchall()
            conn.close()

            if shifts:
                for widget in view_window.winfo_children():
                    widget.destroy()
                tk.Label(view_window, text="Filtered Shifts", font=("Arial", 14, "bold")).pack(pady=10)
                for shift in shifts:
                    tk.Label(view_window, text=f"Shift ID: {shift[0]}, Employee: {shift[1]}, Time: {shift[2]}, Manager: {shift[3]}").pack(pady=5)
            else:
                messagebox.showerror("Error", f"No shifts found for employee {emp_name}")

        tk.Button(view_window, text="Filter Shifts", command=filter_shifts, width=30).pack(pady=10)

    # Add Shift
    def add_shift(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Shift")
        tk.Label(add_window, text="Employee Name:").pack(pady=5)
        emp_entry = tk.Entry(add_window)
        emp_entry.pack(pady=5)
        tk.Label(add_window, text="Shift Time (HH:MM):").pack(pady=5)
        shift_entry = tk.Entry(add_window)
        shift_entry.pack(pady=5)

        def save_shift():
            shift_time = shift_entry.get()
            if not self.validate_shift_time(shift_time):
                messagebox.showerror("Error", "Invalid time format. Please enter time as HH:MM.")
                return
            
            conn = sqlite3.connect("shifts.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO shifts (employee, shift_time, manager) VALUES (?, ?, ?)",
                           (emp_entry.get(), shift_time, self.current_user))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Shift added successfully!")
            add_window.destroy()
        
        tk.Button(add_window, text="Save", command=save_shift, width=20).pack(pady=10)

    # Update Shift
    def update_shift(self):
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Shift")
        tk.Label(update_window, text="Shift ID to Update:").pack(pady=5)
        id_entry = tk.Entry(update_window)
        id_entry.pack(pady=5)
        tk.Label(update_window, text="New Shift Time (HH:MM):").pack(pady=5)
        new_shift_entry = tk.Entry(update_window)
        new_shift_entry.pack(pady=5)

        def update():
            shift_time = new_shift_entry.get()
            if not self.validate_shift_time(shift_time):
                messagebox.showerror("Error", "Invalid time format. Please enter time as HH:MM.")
                return
            
            conn = sqlite3.connect("shifts.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE shifts SET shift_time=? WHERE id=?", (shift_time, id_entry.get()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Shift updated successfully!")
            update_window.destroy()
        
        tk.Button(update_window, text="Update", command=update, width=20).pack(pady=10)

    # Delete Shift
    def delete_shift(self):
        delete_window = tk.Toplevel(self.root)
        delete_window.title("Delete Shift")
        tk.Label(delete_window, text="Shift ID to Delete:").pack(pady=5)
        id_entry = tk.Entry(delete_window)
        id_entry.pack(pady=5)

        def delete():
            conn = sqlite3.connect("shifts.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM shifts WHERE id=?", (id_entry.get(),))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Shift deleted successfully!")
            delete_window.destroy()
        
        tk.Button(delete_window, text="Delete", command=delete, width=20).pack(pady=10)

    # Validate Shift Time Format (HH:MM)
    def validate_shift_time(self, time_str):
        return bool(re.match(r"^\d{2}:\d{2}$", time_str))

# Run App
if __name__ == "__main__":
    root = tk.Tk()
    app = ShiftManagementApp(root)
    root.mainloop()