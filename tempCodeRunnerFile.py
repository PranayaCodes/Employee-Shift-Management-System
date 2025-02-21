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


import tkinter as tk

# Tkinter UI setup for updating shifts
root = tk.Tk()
root.title("Update Shift")

tk.Label(root, text="Shift ID").pack()
entry_id = tk.Entry(root)
entry_id.pack()

tk.Label(root, text="New Shift Time").pack()
entry_shift = tk.Entry(root)
entry_shift.pack()

tk.Button(root, text="Update Shift").pack()

root.mainloop()



import tkinter as tk

# Tkinter UI setup for deleting shifts
root = tk.Tk()
root.title("Delete Shift")

tk.Label(root, text="Shift ID").pack()
entry_id = tk.Entry(root)
entry_id.pack()

tk.Button(root, text="Delete Shift").pack()

root.mainloop()
