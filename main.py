import tkinter as tk
from tkinter import messagebox

# Tkinter UI setup
root = tk.Tk()
root.title("Login System")

# UI Elements
tk.Label(root, text="Username").pack()
entry_user = tk.Entry(root)
entry_user.pack()

tk.Label(root, text="Password").pack()
entry_pass = tk.Entry(root, show="*")
entry_pass.pack()

tk.Button(root, text="Login").pack()
tk.Button(root, text="Signup").pack()

root.mainloop()
