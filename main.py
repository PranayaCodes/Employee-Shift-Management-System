import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

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
        self.root.title("Shift Management System")
        self.root.geometry("500x400")
        self.current_user = None
        self.create_login_page()
    
    # Aaryaman - User Login & Signup
    def create_login_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()
        
        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()
        
        self.role_var = tk.StringVar(value="employee")
        tk.Radiobutton(self.root, text="Employee", variable=self.role_var, value="employee").pack()
        tk.Radiobutton(self.root, text="Manager", variable=self.role_var, value="manager").pack()
        
        tk.Button(self.root, text="Login", command=self.login).pack()
        tk.Button(self.root, text="Signup", command=self.signup).pack()
    
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
            self.create_main_page()
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()
        conn = sqlite3.connect("shifts.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        conn.close()

    # Main Page
    def create_main_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text=f"Welcome {self.current_user} ({self.role})").pack()
        if self.role == "manager":
            tk.Button(self.root, text="Add Shift", command=self.add_shift).pack()
            tk.Button(self.root, text="Update Shift", command=self.update_shift).pack()
            tk.Button(self.root, text="Delete Shift", command=self.delete_shift).pack()
        tk.Button(self.root, text="Logout", command=self.create_login_page).pack()
    
    # Bibek - Add Shift
    def add_shift(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Shift")
        tk.Label(add_window, text="Employee Name:").pack()
        emp_entry = tk.Entry(add_window)
        emp_entry.pack()
        tk.Label(add_window, text="Shift Time:").pack()
        shift_entry = tk.Entry(add_window)
        shift_entry.pack()
        
        def save_shift():
            conn = sqlite3.connect("shifts.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO shifts (employee, shift_time, manager) VALUES (?, ?, ?)",
                           (emp_entry.get(), shift_entry.get(), self.current_user))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Shift added successfully!")
            add_window.destroy()
        
        tk.Button(add_window, text="Save", command=save_shift).pack()
    
    # Nirajan - Update Shift
    def update_shift(self):
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Shift")
        tk.Label(update_window, text="Shift ID to Update:").pack()
        id_entry = tk.Entry(update_window)
        id_entry.pack()
        tk.Label(update_window, text="New Shift Time:").pack()
        new_shift_entry = tk.Entry(update_window)
        new_shift_entry.pack()
        
        def update():
            conn = sqlite3.connect("shifts.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE shifts SET shift_time=? WHERE id=?", (new_shift_entry.get(), id_entry.get()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Shift updated successfully!")
            update_window.destroy()
        
        tk.Button(update_window, text="Update", command=update).pack()
    
    # Pranaya - Delete Shift
    def delete_shift(self):
        delete_window = tk.Toplevel(self.root)
        delete_window.title("Delete Shift")
        tk.Label(delete_window, text="Shift ID to Delete:").pack()
        id_entry = tk.Entry(delete_window)
        id_entry.pack()
        
        def delete():
            conn = sqlite3.connect("shifts.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM shifts WHERE id=?", (id_entry.get(),))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Shift deleted successfully!")
            delete_window.destroy()
        
        tk.Button(delete_window, text="Delete", command=delete).pack()

# Run App
if __name__ == "__main__":
    root = tk.Tk()
    app = ShiftManagementApp(root)
    root.mainloop()
