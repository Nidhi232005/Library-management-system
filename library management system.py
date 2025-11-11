import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from datetime import datetime, timedelta

# ---------- Database Connection ----------
def connect():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="nidhi@232005",
        database="librarydb"
    )

# ---------- Setup Database ----------
def setup_db():
    con = connect()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS books(
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(100),
            author VARCHAR(100),
            status VARCHAR(20) DEFAULT 'Available',
            student_name VARCHAR(100),
            roll_no VARCHAR(50),
            due_date DATE
        )
    """)
    con.commit(); con.close()

# ---------- Functions ----------
def add_book():
    t, a = title.get(), author.get()
    if not t or not a:
        messagebox.showwarning("Input Error", "Please enter Title and Author!")
        return
    con = connect(); cur = con.cursor()
    cur.execute("INSERT INTO books (title, author) VALUES (%s, %s)", (t, a))
    con.commit(); con.close()
    title.delete(0, tk.END); author.delete(0, tk.END)
    show_books()

def get_books(search=""):
    con = connect(); cur = con.cursor()
    if search:
        cur.execute("""
            SELECT id, title, author, status, 
                   IFNULL(student_name,''), IFNULL(roll_no,''), 
                   IFNULL(DATE_FORMAT(due_date, '%Y-%m-%d'),'')
            FROM books 
            WHERE title LIKE %s OR author LIKE %s
        """, (f"%{search}%", f"%{search}%"))
    else:
        cur.execute("""
            SELECT id, title, author, status, 
                   IFNULL(student_name,''), IFNULL(roll_no,''), 
                   IFNULL(DATE_FORMAT(due_date, '%Y-%m-%d'),'')
            FROM books
        """)
    data = cur.fetchall(); con.close()
    return data

def update_book(action):
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Select Book", "Please select a book first!")
        return
    book_id = tree.item(sel[0])['values'][0]
    con = connect(); cur = con.cursor()

    if action == "borrow":
        student = simpledialog.askstring("Student Name", "Enter Student Name:")
        roll = simpledialog.askstring("Roll Number", "Enter Roll Number:")
        if not student or not roll:
            messagebox.showwarning("Input Error", "Both fields are required!")
            con.close(); return
        due_date = datetime.now() + timedelta(days=30)
        cur.execute("""
            UPDATE books 
            SET status='Borrowed', student_name=%s, roll_no=%s, due_date=%s
            WHERE id=%s
        """, (student, roll, due_date.strftime("%Y-%m-%d"), book_id))

    elif action == "return":
        cur.execute("""
            UPDATE books 
            SET status='Available', student_name=NULL, roll_no=NULL, due_date=NULL
            WHERE id=%s
        """, (book_id,))

    elif action == "delete":
        cur.execute("DELETE FROM books WHERE id=%s", (book_id,))

    con.commit(); con.close()
    show_books()

def show_books(search=""):
    for i in tree.get_children(): 
        tree.delete(i)
    for b in get_books(search):
        tree.insert("", "end", values=b)

# ---------- Main App ----------
def open_app():
    login.destroy()
    app = tk.Tk()
    app.title("📚 Library Management System")
    app.geometry("1100x560")
    app.config(bg="#EAF0F6")

    # Header
    tk.Label(app, text="📘 Library Management System",
             font=("Segoe UI", 18, "bold"), bg="#D8BFD8", fg="#1B263B").pack(fill="x", pady=8)

    # Add Book Frame
    f1 = tk.Frame(app, bg="#F7F9FB"); f1.pack(fill="x", pady=10)
    tk.Label(f1, text="Title:", bg="#F7F9FB", fg="#1B263B").grid(row=0, column=0)
    global title, author
    title = ttk.Entry(f1, width=25); title.grid(row=0, column=1, padx=5)
    tk.Label(f1, text="Author:", bg="#F7F9FB", fg="#1B263B").grid(row=0, column=2)
    author = ttk.Entry(f1, width=25); author.grid(row=0, column=3, padx=5)
    ttk.Button(f1, text="Add", command=add_book).grid(row=0, column=4, padx=5)

    # Search Frame
    f2 = tk.Frame(app, bg="#E3DFF2"); f2.pack(fill="x", pady=8)
    search = ttk.Entry(f2, width=40); search.grid(row=0, column=0, padx=10)
    ttk.Button(f2, text="Search", command=lambda: show_books(search.get())).grid(row=0, column=1, padx=5)
    ttk.Button(f2, text="Show All", command=lambda: show_books()).grid(row=0, column=2, padx=5)

    # Book Table
    global tree
    cols = ("ID", "Title", "Author", "Status", "Student Name", "Roll No", "Due Date")
    style = ttk.Style()
    style.configure("Treeview", background="#F7F9FB", foreground="black", rowheight=25, fieldbackground="#F7F9FB")
    style.map("Treeview", background=[("selected", "#B6A6CA")])
    tree = ttk.Treeview(app, columns=cols, show="headings", height=15)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=140, anchor="center")
    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # Buttons
    f3 = tk.Frame(app, bg="#EAF0F6"); f3.pack(pady=10)
    tk.Button(f3, text="Borrow", bg="#A7C7E7", fg="black", width=10,
              command=lambda: update_book("borrow")).grid(row=0, column=0, padx=10)
    tk.Button(f3, text="Return", bg="#C8A2C8", fg="black", width=10,
              command=lambda: update_book("return")).grid(row=0, column=1, padx=10)
    tk.Button(f3, text="Delete", bg="#F5B7B1", fg="black", width=10,
              command=lambda: update_book("delete")).grid(row=0, column=2, padx=10)

    show_books()
    app.mainloop()

# ---------- Login Window ----------
setup_db()
login = tk.Tk()
login.title("Login")
login.geometry("400x250")
login.config(bg="#E3DFF2")

tk.Label(login, text="Library Login", font=("Segoe UI", 16, "bold"),
         bg="#A7C7E7", fg="#1B263B").pack(fill="x", pady=10)

frame = tk.Frame(login, bg="#E3DFF2"); frame.pack(pady=30)
tk.Label(frame, text="Username:", bg="#E3DFF2").grid(row=0, column=0)
user = ttk.Entry(frame, width=25); user.grid(row=0, column=1)
tk.Label(frame, text="Password:", bg="#E3DFF2").grid(row=1, column=0)
pas = ttk.Entry(frame, show="*", width=25); pas.grid(row=1, column=1)

def login_user():
    u, p = user.get(), pas.get()
    if (u == "admin" and p == "password") or (u == "nidhi" and p == "1234"):
        open_app()
    else:
        messagebox.showerror("Error", "Invalid username or password!")

tk.Button(frame, text="Login", bg="#A7C7E7", fg="black", width=10, command=login_user).grid(row=2, column=0, pady=15)
tk.Button(frame, text="Exit", bg="#F5B7B1", fg="black", width=10, command=login.destroy).grid(row=2, column=1, pady=15)

login.mainloop()
