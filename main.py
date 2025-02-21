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
    def _init_(self, root):
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