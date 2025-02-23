import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manager_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Helper: Get the first manager's id
def get_first_manager():
    conn = sqlite3.connect("shifts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE role='Manager' ORDER BY id ASC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Enhanced UI Components & Styles
class AppStyles:
    BG_COLOR = "#f0f0f0"
    PRIMARY_COLOR = "#2c3e50"
    SECONDARY_COLOR = "#3498db"  # Blue color
    SUCCESS_COLOR = "#27ae60"
    DANGER_COLOR = "#e74c3c"
    FONT = ("Helvetica", 16)       # Increased font size
    TITLE_FONT = ("Helvetica", 20, "bold")  # Increased title font size

def create_button(parent, text, command, bg_color=AppStyles.SECONDARY_COLOR):
    return tk.Button(parent, text=text, command=command, 
                    bg=bg_color, fg="white", font=AppStyles.FONT,
                    relief="flat", padx=10, pady=5)

# Manager Approval System
def show_manager_requests():
    def approve_request():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a request")
            return
        username = tree.item(selected)['values'][1]
        conn = sqlite3.connect("shifts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM manager_requests WHERE username=?", (username,))
        password = cursor.fetchone()[0]
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                           (username, password, "Manager"))
            cursor.execute("DELETE FROM manager_requests WHERE username=?", (username,))
            conn.commit()
            messagebox.showinfo("Success", f"Approved {username} as Manager")
            update_request_list()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        conn.close()

    def reject_request():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a request")
            return
        username = tree.item(selected)['values'][1]
        conn = sqlite3.connect("shifts.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM manager_requests WHERE username=?", (username,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Request rejected")
        update_request_list()

    def update_request_list():
        for item in tree.get_children():
            tree.delete(item)
        conn = sqlite3.connect("shifts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM manager_requests")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    window = tk.Toplevel()
    window.title("Manager Requests")
    window.geometry("600x400")
    
    frame = tk.Frame(window, bg=AppStyles.BG_COLOR)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    tree = ttk.Treeview(frame, columns=("ID", "Username"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Username", text="Username")
    tree.pack(fill="both", expand=True, pady=10)
    
    btn_frame = tk.Frame(frame, bg=AppStyles.BG_COLOR)
    btn_frame.pack(pady=10)
    
    create_button(btn_frame, "Approve", approve_request, AppStyles.SUCCESS_COLOR).pack(side="left", padx=20)
    create_button(btn_frame, "Reject", reject_request, AppStyles.DANGER_COLOR).pack(side="left", padx=20)
    
    update_request_list()

# Registration Function
def register():
    username = entry_username.get()
    password = entry_password.get()
    role = role_var.get()
    
    if not username or not password:
        messagebox.showerror("Error", "All fields are required")
        return
    
    conn = sqlite3.connect("shifts.db")
    cursor = conn.cursor()
    
    try:
        if role == "Manager":
            if get_first_manager():
                cursor.execute("INSERT INTO manager_requests (username, password) VALUES (?, ?)",
                               (username, password))
                messagebox.showinfo("Success", "Manager request submitted for approval")
            else:
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                               (username, password, role))
                messagebox.showinfo("Success", "First manager registered")
        else:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                           (username, password, role))
            messagebox.showinfo("Success", "Employee registered")
        
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists")
    finally:
        conn.close()

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

# Shift Management Functions
def view_shifts():
    for row in shift_tree.get_children():
        shift_tree.delete(row)
    conn = sqlite3.connect("shifts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shifts")
    for row in cursor.fetchall():
        shift_tree.insert("", "end", values=row)
    conn.close()

def add_shift():
    window = tk.Toplevel()
    window.title("Add Shift")
    window.geometry("300x250")
    window.configure(bg=AppStyles.BG_COLOR)
    
    frame = tk.Frame(window, bg=AppStyles.BG_COLOR)
    frame.pack(pady=10, padx=10, fill="both", expand=True)
    
    tk.Label(frame, text="Employee Name:", bg=AppStyles.BG_COLOR, font=AppStyles.FONT).pack(pady=10)
    entry_emp = tk.Entry(frame, font=AppStyles.FONT, width=25)
    entry_emp.pack(pady=10)
    
    tk.Label(frame, text="Shift Date:", bg=AppStyles.BG_COLOR, font=AppStyles.FONT).pack(pady=10)
    entry_date = tk.Entry(frame, font=AppStyles.FONT, width=25)
    entry_date.pack(pady=10)
    
    tk.Label(frame, text="Shift Time:", bg=AppStyles.BG_COLOR, font=AppStyles.FONT).pack(pady=10)
    entry_time = tk.Entry(frame, font=AppStyles.FONT, width=25)
    entry_time.pack(pady=10)
    
    def submit_shift():
        emp = entry_emp.get()
        date = entry_date.get()
        time = entry_time.get()
        if not emp or not date or not time:
            messagebox.showerror("Error", "All fields are required")
            return
        conn = sqlite3.connect("shifts.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO shifts (employee_name, shift_date, shift_time) VALUES (?, ?, ?)", (emp, date, time))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Shift added successfully")
        window.destroy()
        view_shifts()
    
    create_button(frame, "Submit", submit_shift, AppStyles.SECONDARY_COLOR).pack(pady=10)

def update_shift():
    selected = shift_tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a shift to update")
        return
    values = shift_tree.item(selected)['values']  # (id, employee, date, time)
    shift_id = values[0]
    
    window = tk.Toplevel()
    window.title("Update Shift")
    window.geometry("300x250")
    window.configure(bg=AppStyles.BG_COLOR)
    
    frame = tk.Frame(window, bg=AppStyles.BG_COLOR)
    frame.pack(pady=10, padx=10, fill="both", expand=True)
    
    tk.Label(frame, text="Employee Name:", bg=AppStyles.BG_COLOR, font=AppStyles.FONT).pack(pady=10)
    entry_emp = tk.Entry(frame, font=AppStyles.FONT, width=25)
    entry_emp.insert(0, values[1])
    entry_emp.pack(pady=10)
    
    tk.Label(frame, text="Shift Date:", bg=AppStyles.BG_COLOR, font=AppStyles.FONT).pack(pady=10)
    entry_date = tk.Entry(frame, font=AppStyles.FONT, width=25)
    entry_date.insert(0, values[2])
    entry_date.pack(pady=10)
    
    tk.Label(frame, text="Shift Time:", bg=AppStyles.BG_COLOR, font=AppStyles.FONT).pack(pady=10)
    entry_time = tk.Entry(frame, font=AppStyles.FONT, width=25)
    entry_time.insert(0, values[3])
    entry_time.pack(pady=10)
    
    def submit_update():
        emp = entry_emp.get()
        date = entry_date.get()
        time = entry_time.get()
        if not emp or not date or not time:
            messagebox.showerror("Error", "All fields are required")
            return
        conn = sqlite3.connect("shifts.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE shifts SET employee_name=?, shift_date=?, shift_time=? WHERE id=?", (emp, date, time, shift_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Shift updated successfully")
        window.destroy()
        view_shifts()
    
    create_button(frame, "Update", submit_update, AppStyles.SECONDARY_COLOR).pack(pady=10)

def delete_shift():
    selected = shift_tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a shift to delete")
        return
    shift_id = shift_tree.item(selected)['values'][0]
    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this shift?")
    if confirm:
        conn = sqlite3.connect("shifts.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shifts WHERE id=?", (shift_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Shift deleted successfully")
        view_shifts()

def logout():
    root.destroy()
    open_login_window()

# Main Window
def open_main_window(role):
    global root, shift_tree
    root = tk.Tk()
    root.title("Shift Management")
    root.geometry("800x600")
    root.configure(bg=AppStyles.BG_COLOR)
    
    header_frame = tk.Frame(root, bg=AppStyles.PRIMARY_COLOR)
    header_frame.pack(fill="x", pady=10)
    tk.Label(header_frame, text="Employee Shift Management System",
             fg="white", bg=AppStyles.PRIMARY_COLOR, font=AppStyles.TITLE_FONT).pack(pady=10)
    
    if role == "Manager" and get_first_manager():
        manager_frame = tk.Frame(root, bg=AppStyles.BG_COLOR)
        manager_frame.pack(pady=10)
        create_button(manager_frame, "Add Shift", add_shift).pack(side="left", padx=20)
        create_button(manager_frame, "Update Shift", update_shift, AppStyles.SUCCESS_COLOR).pack(side="left", padx=20)
        create_button(manager_frame, "Delete Shift", delete_shift, AppStyles.DANGER_COLOR).pack(side="left", padx=20)
        create_button(manager_frame, "Manage Requests", show_manager_requests, AppStyles.SUCCESS_COLOR).pack(side="left", padx=20)
    
    tk.Button(root, text="Logout", command=logout, bg=AppStyles.DANGER_COLOR, fg="white", font=AppStyles.FONT).pack(pady=10)
    
    shift_tree = ttk.Treeview(root, columns=("ID", "Employee", "Date", "Time"), show="headings")
    shift_tree.heading("ID", text="ID")
    shift_tree.heading("Employee", text="Employee")
    shift_tree.heading("Date", text="Date")
    shift_tree.heading("Time", text="Time")
    shift_tree.pack(pady=10, fill="both", expand=True)
    
    view_shifts()
    root.mainloop()

# Enhanced Login Window with Image on Left and Centered (and Lower) Login Form on Right
def open_login_window():
    global login_window, role_var, entry_username, entry_password
    login_window = tk.Tk()
    login_window.title("Shift Management System")
    login_window.geometry("1000x600")
    login_window.configure(bg=AppStyles.BG_COLOR)
    
    # Main container frame with two columns
    container = tk.Frame(login_window, bg=AppStyles.BG_COLOR)
    container.pack(fill="both", expand=True, padx=0, pady=20)
    
    # Left Frame for Image using Pillow
    left_frame = tk.Frame(container, bg=AppStyles.BG_COLOR)
    left_frame.grid(row=0, column=0, sticky="nsew", padx=(0,20), pady=150)
    image_path = "Shift_Manager\Image_folder\image.png"
    if os.path.exists(image_path):
        pil_image = Image.open(image_path)
        # Resize using the new resampling attribute
        pil_image = pil_image.resize((700, 600), Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(pil_image)
        img_label = tk.Label(left_frame, image=img, bg=AppStyles.BG_COLOR)
        img_label.image = img  # keep a reference
        img_label.pack(expand=True)
    else:
        tk.Label(left_frame, text="[Image Not Available]", bg=AppStyles.BG_COLOR, font=AppStyles.FONT).pack(expand=True)
    
    # Right Frame for Login Form
    right_frame = tk.Frame(container, bg=AppStyles.BG_COLOR)
    right_frame.grid(row=0, column=1, sticky="nsew")
    
    # Spacer to push the login form lower
    tk.Label(right_frame, text="", bg=AppStyles.BG_COLOR).pack(pady=100)
    
    tk.Label(right_frame, text="Shift Management System", 
             bg=AppStyles.BG_COLOR, fg=AppStyles.PRIMARY_COLOR, font=AppStyles.TITLE_FONT).pack(pady=20)
    
    role_frame = tk.Frame(right_frame, bg=AppStyles.BG_COLOR)
    role_frame.pack(pady=10)
    role_var = tk.StringVar(value="Employee")
    tk.Radiobutton(role_frame, text="Manager", variable=role_var, value="Manager",
                  bg=AppStyles.BG_COLOR, font=AppStyles.FONT).pack(side="left", padx=20)
    tk.Radiobutton(role_frame, text="Employee", variable=role_var, value="Employee",
                  bg=AppStyles.BG_COLOR, font=AppStyles.FONT).pack(side="left", padx=20)
    
    input_frame = tk.Frame(right_frame, bg=AppStyles.BG_COLOR)
    input_frame.pack(pady=20)
    tk.Label(input_frame, text="Username:", bg=AppStyles.BG_COLOR, font=AppStyles.FONT).grid(row=0, column=0, pady=10)
    entry_username = tk.Entry(input_frame, font=AppStyles.FONT, width=30)
    entry_username.grid(row=0, column=1, pady=10)
    tk.Label(input_frame, text="Password:", bg=AppStyles.BG_COLOR, font=AppStyles.FONT).grid(row=1, column=0, pady=10)
    entry_password = tk.Entry(input_frame, show="*", font=AppStyles.FONT, width=30)
    entry_password.grid(row=1, column=1, pady=10)
    
    btn_frame = tk.Frame(right_frame, bg=AppStyles.BG_COLOR)
    btn_frame.pack(pady=20)
    create_button(btn_frame, "Login", login).pack(side="left", padx=20)
    create_button(btn_frame, "Register", register, AppStyles.SUCCESS_COLOR).pack(side="left", padx=20)
    
    container.grid_columnconfigure(0, weight=1)
    container.grid_columnconfigure(1, weight=1)
    
    login_window.mainloop()

setup_database()
open_login_window()
