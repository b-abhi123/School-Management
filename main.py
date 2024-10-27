from email import message
from multiprocessing.util import sub_debug
from re import search
from sqlite3 import connect
from ssl import Options
import tkinter as tk
from tkinter import StringVar, messagebox,ttk
import mysql.connector as sql
from numpy import delete
from prettytable import PrettyTable
import configparser
import hashlib
import platform

from ttkthemes import ThemedStyle

global currentUser
currentUser = None

def add_record_to_db(name,passwd,classname,identity,connection):
    cursor = connection.cursor()
    
    split_classname = classname.split()
    class_int = int(split_classname[0])
    section_str = str(split_classname[1])

    values = (name,passwd,class_int,section_str,identity)

    QUERY = "INSERT INTO users (Name,Password,Class,Section,Identity) VALUES (%s,%s,%s,%s,%s)"

    cursor.execute(QUERY,values)
    
    if cursor.rowcount > 0:
        messagebox.showinfo("Success","Account created successfully!")
        connection.commit()
    else:
        messagebox.showerror("Error","An error occured. Please double-check your info.")

def get_record_from_db(name,connection):

    cursor = connection.cursor()
    QUERY = "SELECT ID, Name, Password, CONCAT(Class, Section) AS NewClass, IDENTITY FROM users WHERE Name LIKE %s;"


    cursor.execute(QUERY, (name + "%",))

    rows = cursor.fetchall()

    return rows

def delete_record_from_db(name,connection):
    
    cursor = connection.cursor()
    QUERY = "DELETE FROM users WHERE Name LIKE %s LIMIT 1"

    cursor.execute(QUERY, (name + "%",))

    if cursor.rowcount > 0:
        messagebox.showinfo("Success","Account deleted successfully!")
        connection.commit()
    else:
        messagebox.showerror("Error","An error occured. Please double-check your info.")

def add_notice_to_db(noticetext,connection):
    cursor = connection.cursor()

    QUERY = "INSERT INTO notices (NoticeText) VALUES (%s);"

    cursor.execute(QUERY,(noticetext,))

    if cursor.rowcount > 0:
        messagebox.showinfo("Success","Notice was successfully posted.")
        connection.commit()
    else:
        messagebox.showerror("Error","An error occured.")

def get_notice_from_db(connection):

    cursor = connection.cursor()
    QUERY = "SELECT NoticeText FROM notices ORDER BY ID DESC;"

    cursor.execute(QUERY)

    rows = cursor.fetchall()

    return rows

def get_class_from_db(classname,sectionname,connection):

    cursor = connection.cursor()

    QUERY = "SELECT ID,Name,Password,CONCAT(Class, Section) AS NewClass,Identity FROM users WHERE (Class = %s AND Section = %s AND Identity = 'Student');"

    cursor.execute(QUERY,(classname,sectionname))

    rows = cursor.fetchall()

    return rows

def add_remark_to_db(studentname,classname,sectionname,remark,connection):
    cursor = connection.cursor()

    QUERY = "UPDATE users SET Remarks = %s WHERE Name = %s AND (Class = %s AND Section = %s);"

    cursor.execute(QUERY,(remark,studentname,classname,sectionname))

    if cursor.rowcount > 0:
        messagebox.showinfo("Success","Student Remark successfully changed.")
        connection.commit()
    else:
        messagebox.showerror("Error","An error occured. Please double-check your info.")

def get_remark_from_db(studentname,classname,sectionname,connection):

    cursor = connection.cursor()

    QUERY = "SELECT Remarks FROM users WHERE (Name = %s AND Class = %s AND Section = %s);"

    cursor.execute(QUERY,(studentname,classname,sectionname))

    row = cursor.fetchone()

    if row != []:
        messagebox.showinfo("Remark","Your teacher has published a remark: " + row[0])
    else:
        messagebox.showinfo("Remark","Your teacher has posted no remark on you.")

def create_dark_theme():

    dark_style = ThemedStyle()
    dark_style.set_theme("equilux") 

'''def generate_id():
    system_info = f"{platform.system()}_{platform.node()}_{platform.processor()}"
    device_id = hashlib.sha256(system_info.encode()).hexdigest()
    return device_id
'''
def db_config(cursor):
    query1 = "CREATE DATABASE IF NOT EXISTS LearnSys_users;"
    query2 = "USE LearnSys_users;"

    query3 = "CREATE TABLE IF NOT EXISTS users (ID INT PRIMARY KEY AUTO_INCREMENT,Name VARCHAR(255),Password VARCHAR(255),Class INT,Section CHAR(1),Identity ENUM('Student', 'Admin', 'Teacher'),Remarks TEXT);"
    query4 = "CREATE TABLE IF NOT EXISTS notices (ID INT PRIMARY KEY AUTO_INCREMENT,NoticeText TEXT);"

    query5 = "INSERT IGNORE INTO users (ID, Name, Password, Class, Section, Identity, Remarks) SELECT 0, 'RootAdmin', 'admin', NULL, NULL, 'Admin', NULL FROM dual WHERE NOT EXISTS (SELECT 1 FROM users WHERE Name = 'RootAdmin');"


    print("Loading database...")
    cursor.execute(query1)
    cursor.execute(query2)

    print("Loading tables...")
    cursor.execute(query3)
    cursor.execute(query4)

    print("Configuring users...")
    cursor.execute(query5)


def create_loading_screen():
    try:
        global conn
        conn = sql.connect(
            host="localhost",
            user="root",
            password="HRaa@123",
        )
        print(conn.is_connected())
        db_config(conn.cursor())
        conn.commit()

        create_main_window()
    except Exception as e:
        messagebox.showerror("Connection Error", "Unable to connect to the database.")
        print(e)

def create_main_window():
    # Create the main window
    global root
    root = tk.Tk()
    root.title("Welcome back!")
    root.configure(bg="#333333")  # Set the background color to dark gray (hex code)
    root.iconbitmap("assets/logo.ico")
    # Calculate the window size and position
    window_size = 400  # Set the desired window size (in pixels)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_size) // 2
    y = (screen_height - window_size) // 2
    root.geometry(f"{window_size}x{window_size}+{x}+{y}")

    # Use Verdana Bold for titles and Verdana for other text
    title_font = ("Verdana Bold", 16)
    text_font = ("Verdana", 12)

    # Create a frame to hold the contents with padding
    frame = tk.Frame(root, bg="#333333")
    frame.pack(pady=20)

    # Create and place widgets with customized colors and button width
    title_label = tk.Label(frame, text="LearnSys", font=title_font, bg="#333333", fg="white")
    title_label.pack(pady=10)

    subheading_label = tk.Label(frame, text="Enter your info to get started.", font=text_font, bg="#333333", fg="white")
    subheading_label.pack(pady=5)

    username_label = tk.Label(frame, text="👤 Username:", font=text_font, bg="#333333", fg="white")
    username_label.pack(pady=(10, 5))  # Lower the username label
    global username_entry
    username_entry = tk.Entry(frame, font=text_font, bg="#333333", fg="white", insertbackground="purple", bd=2, relief=tk.GROOVE)
    username_entry.pack(pady=5)  # Lower the username entry field

    password_label = tk.Label(frame, text="🔒 Password:", font=text_font, bg="#333333", fg="white")
    password_label.pack(pady=(10, 5))  # Lower the password label
    global password_entry
    password_entry = tk.Entry(frame, show="*", font=text_font, bg="#333333", fg="white", insertbackground="purple", bd=2, relief=tk.GROOVE)
    password_entry.pack(pady=5)  # Lower the password entry field

    login_button = tk.Button(frame, text="Login", command=login, font=text_font, bg="green", fg="white", width=15, bd=0)
    login_button.pack(pady=10)

    # Rounded corners for the Login button
    login_button.config(relief=tk.RAISED)

    # Start the GUI event loop
    root.mainloop()

def create_admin_frame(master):
    admin_frame = tk.Toplevel(master)
    admin_frame.title("LearnSys - Admin Panel")
    admin_frame.geometry('800x600')
    admin_frame.state('zoomed')

    def add_record():

        add_record_frame = tk.Toplevel(master)
        add_record_frame.title("Add Record")

        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 600) // 2
        add_record_frame.geometry(f"600x600+{x}+{y}")
            
        add_record_frame.configure(bg="#333333")
        text_font = ("Verdana", 12)

        title_label = tk.Label(add_record_frame, text="LearnSys", font=("Verdana Bold",16), bg="#333333", fg="white")
        title_label.pack(pady=10)
        sub_title_label = tk.Label(add_record_frame, text="Create a new account.", font=("Verdana Bold",12), bg="#333333", fg="white")
        sub_title_label.pack(pady=10)      
        name_label = tk.Label(add_record_frame, text="👤 Name:", font=text_font, bg="#333333", fg="white")
        name_label.pack(pady=(10, 5))  # Lower the username label
        global name_entry
        name_entry = tk.Entry(add_record_frame, font=text_font, bg="#333333", fg="white", insertbackground="purple", bd=2, relief=tk.GROOVE)
        name_entry.pack(pady=5)  # Lower the username entry field

        password_label = tk.Label(add_record_frame, text="🔒 Password:", font=text_font, bg="#333333", fg="white")
        password_label.pack(pady=(10, 5))  # Lower the password label
        global pass_entry
        pass_entry = tk.Entry(add_record_frame, font=text_font, bg="#333333", fg="white", insertbackground="purple", bd=2, relief=tk.GROOVE)
        pass_entry.pack(pady=5)  # Lower the password entry field

        class_label = tk.Label(add_record_frame, text="Class:", font=text_font, bg="#333333", fg="white")
        class_label.pack(pady=(10, 5))  # Lower the class label
        global class_entry
        class_entry = tk.Entry(add_record_frame, font=text_font, bg="#333333", fg="white", insertbackground="purple", bd=2, relief=tk.GROOVE)
        class_entry.pack(pady=5)  # Lower the class entry field

        identity_label = tk.Label(add_record_frame,text="🏫 Identity:", font=text_font,bg="#333333", fg="white")
        identity_label.pack(pady=(10, 5))  # Lower the password label
        global identity_entry
        identity_entry = tk.StringVar(master)
        identity_box = tk.OptionMenu(add_record_frame,identity_entry,"Student","Teacher")
        identity_box.pack(pady=5)
        identity_box.config(width=15, bg="#333333", fg="white",font=("Verdana",12))
        
        def send_clicked():
            name_val = name_entry.get()
            pass_val = pass_entry.get()
            class_val = class_entry.get()
            identity_val = identity_entry.get()

            add_record_to_db(name_val,pass_val,class_val,identity_val,conn)

        login_button = tk.Button(add_record_frame, text="Add Record!",command=send_clicked,font=text_font, bg="green", fg="white", width=15, bd=0)
        login_button.pack(pady=15)

    def search_record():
        view_record_frame = tk.Toplevel(master)
        view_record_frame.title("Search Record")

        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 500) // 2
        view_record_frame.geometry(f"500x500+{x}+{y}")
            
        view_record_frame.configure(bg="#333333")

        text_font = ("Verdana",12)

        title_label = tk.Label(view_record_frame, text="LearnSys", font=("Verdana Bold",16), bg="#333333", fg="white")
        title_label.pack(pady=10)
        sub_title_label = tk.Label(view_record_frame, text="Search for an account.", font=("Verdana Bold",12), bg="#333333", fg="white")
        sub_title_label.pack(pady=10)    
        name_label = tk.Label(view_record_frame, text="👤 Name:", font=text_font, bg="#333333", fg="white")
        name_label.pack(pady=(10, 5))  # Lower the username label
        global name_entry2
        name_entry2 = tk.Entry(view_record_frame, font=text_font, bg="#333333", fg="white", insertbackground="purple", bd=2, relief=tk.GROOVE)
        name_entry2.pack(pady=5)  # Lower the username entry field

        treeview_frame2 = tk.Frame(view_record_frame, bg="#333333")
        treeview_frame2.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create columns for the Treeview
        columns = ("ID", "Name", "Password","Class","Identity")
        column_sizes = (10,30,30,10,10)

        style = ttk.Style()
        style.configure("Custom1.Treeview", background="white", foreground="#333333")
        style.configure("Custom1.Treeview.Heading", font=("Verdana Bold", 9))
        treeview2 = ttk.Treeview(treeview_frame2, columns=columns, show="headings", style="Custom1.Treeview")

        # Set column headings
        for col in columns:
            treeview2.heading(col, text=col)

        for col,size in zip(columns,column_sizes):
            treeview2.column(col,width=size,anchor=tk.CENTER)

        # Add a vertical scrollbar
        scrollbar = ttk.Scrollbar(treeview_frame2, orient="vertical", command=treeview.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        treeview2.config(yscrollcommand=scrollbar.set)

        # Pack the Treeview
        treeview2.pack(fill=tk.BOTH, expand=True)

        def on_search_clicked():
            name_val = name_entry2.get()
            res = get_record_from_db(name_val,conn)
            treeview2.delete(*treeview2.get_children())
            if res == []:
                messagebox.showwarning("Warning!","No results found.")
            else:
                for row in res:
                    treeview2.insert("","end",values=row)
        search_button = tk.Button(view_record_frame, text="🔎 Search!", command=on_search_clicked, font=text_font, bg="green", fg="white", width=15, bd=0)
        search_button.pack(pady=10)
        
    def view_record():
        view_record_frame = tk.Toplevel(master)
        view_record_frame.title("View Record")

        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 500) // 2
        view_record_frame.geometry(f"500x500+{x}+{y}")
            
        view_record_frame.configure(bg="#333333")

        text_font = ("Verdana",12)

        title_label = tk.Label(view_record_frame, text="LearnSys", font=("Verdana Bold",16), bg="#333333", fg="white")
        title_label.pack(pady=10)
        sub_title_label = tk.Label(view_record_frame, text="View all Records.", font=("Verdana Bold",12), bg="#333333", fg="white")
        sub_title_label.pack(pady=10)    

        treeview_frame2 = tk.Frame(view_record_frame, bg="#333333")
        treeview_frame2.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create columns for the Treeview
        columns = ("ID", "Name", "Password","Class","Identity")
        column_sizes = (10,30,30,10,10)

        style = ttk.Style()
        style.configure("Custom1.Treeview", background="white", foreground="#333333")
        style.configure("Custom1.Treeview.Heading", font=("Verdana Bold", 9))
        treeview2 = ttk.Treeview(treeview_frame2, columns=columns, show="headings", style="Custom1.Treeview")

        # Set column headings
        for col in columns:
            treeview2.heading(col, text=col)

        for col,size in zip(columns,column_sizes):
            treeview2.column(col,width=size,anchor=tk.CENTER)

        # Add a vertical scrollbar
        scrollbar = ttk.Scrollbar(treeview_frame2, orient="vertical", command=treeview.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        treeview2.config(yscrollcommand=scrollbar.set)

        # Pack the Treeview
        treeview2.pack(fill=tk.BOTH, expand=True)

        res = get_record_from_db('',conn)

        if res == []:
            messagebox.showwarning("Warning!","No results found.")
        else:
            for row in res:
                treeview2.insert("","end",values=row)
        
    def delete_record():
        view_record_frame = tk.Toplevel(master)
        view_record_frame.title("Delete Record")

        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 500) // 2
        view_record_frame.geometry(f"500x500+{x}+{y}")
            
        view_record_frame.configure(bg="#333333")

        text_font = ("Verdana",12)

        title_label = tk.Label(view_record_frame, text="LearnSys", font=("Verdana Bold",16), bg="#333333", fg="white")
        title_label.pack(pady=10)
        sub_title_label = tk.Label(view_record_frame, text="Delete an account.", font=("Verdana Bold",12), bg="#333333", fg="white")
        sub_title_label.pack(pady=10)    
        name_label = tk.Label(view_record_frame, text="👤 Name:", font=text_font, bg="#333333", fg="white")
        name_label.pack(pady=(10, 5))  # Lower the username label
        global name_entry2
        name_entry2 = tk.Entry(view_record_frame, font=text_font, bg="#333333", fg="white", insertbackground="purple", bd=2, relief=tk.GROOVE)
        name_entry2.pack(pady=5)  # Lower the username entry field

        treeview_frame2 = tk.Frame(view_record_frame, bg="#333333")
        treeview_frame2.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create columns for the Treeview
        columns = ("ID", "Name", "Password","Class","Identity")
        column_sizes = (10,30,30,10,10)

        style = ttk.Style()
        style.configure("Custom1.Treeview", background="white", foreground="#333333")
        style.configure("Custom1.Treeview.Heading", font=("Verdana Bold", 9))
        treeview2 = ttk.Treeview(treeview_frame2, columns=columns, show="headings", style="Custom1.Treeview")

        # Set column headings
        for col in columns:
            treeview2.heading(col, text=col)

        for col,size in zip(columns,column_sizes):
            treeview2.column(col,width=size,anchor=tk.CENTER)

        # Add a vertical scrollbar
        scrollbar = ttk.Scrollbar(treeview_frame2, orient="vertical", command=treeview.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        treeview2.config(yscrollcommand=scrollbar.set)

        # Pack the Treeview
        treeview2.pack(fill=tk.X, expand=True)
        def on_search_clicked():
            name_val = name_entry2.get()
            res = get_record_from_db(name_val,conn)

            treeview2.delete(*treeview2.get_children())
            if res == []:
                messagebox.showwarning("Warning!","No results found.")
            else:
                for row in res:
                    treeview2.insert("","end",values=row)

        def on_delete_clicked():
            name_val = name_entry2.get()

            delete_record_from_db(name_val,conn)

        search_button = tk.Button(view_record_frame, text="🔎 Search!",command=on_search_clicked,font=text_font, bg="green", fg="white", width=15, bd=0)
        search_button.pack(side=tk.LEFT,padx=(10,5),pady=10)

        delete_button = tk.Button(view_record_frame, text="Delete 1 Record!",command=on_delete_clicked, font=text_font, bg="#8B0000", fg="white", width=15, bd=0)
        delete_button.pack(side=tk.LEFT,padx=(5,10),pady=10)

    def publish_notice():
        view_record_frame = tk.Toplevel(master)
        view_record_frame.title("Publish Notice")

        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 500) // 2
        view_record_frame.geometry(f"500x500+{x}+{y}")
            
        view_record_frame.configure(bg="#333333")

        text_font = ("Verdana",12)

        title_label = tk.Label(view_record_frame, text="LearnSys", font=("Verdana Bold",16), bg="#333333", fg="white")
        title_label.pack(pady=10)
        sub_title_label = tk.Label(view_record_frame, text="Publish a notice.", font=("Verdana Bold",12), bg="#333333", fg="white")
        sub_title_label.pack(pady=10)    
        name_label = tk.Label(view_record_frame, text="📢 Notice:", font=text_font, bg="#333333", fg="white")
        name_label.pack(pady=(10, 5))  # Lower the username label
        global notice_entry
        notice_entry = tk.Text(view_record_frame, font=text_font, bg="#333333", fg="white", bd=2, relief=tk.GROOVE,height=10,insertbackground="#FFFFFF")
        notice_entry.pack(fill=tk.X,pady=10)  

        def on_publish_clicked():
            notice_entry_text = notice_entry.get("1.0",'end-1c')
            add_notice_to_db(notice_entry_text,conn)

        search_button = tk.Button(view_record_frame, text="Publish!", command=on_publish_clicked,font=text_font, bg="green", fg="white", width=15, bd=0)
        search_button.pack(pady=10)

    admin_frame.configure(bg="#333333")

    title_label = tk.Label(admin_frame, text="LearnSys - Admin Panel", font=("Verdana Bold", 26), bg="#333333", fg="white")
    title_label.pack(side=tk.TOP, pady=10, fill=tk.X)

    
    # Create a frame to hold the buttons on the left
    button_frame = tk.Frame(admin_frame, bg="#333333")
    button_frame.pack(side=tk.LEFT, fill=tk.Y)

    # Define button style
    button_style = {"bg": "green", "fg": "white", "width": 15, "bd": 0, "font": ("Verdana", 12)}
    logout_style = {"bg": "#8B0000", "fg": "white", "width": 15, "bd": 0, "font": ("Verdana", 12)}
    
    # Create a treeview on the right
    treeview_frame = tk.Frame(admin_frame, bg="#333333")
    treeview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    columns = ("Recent Notices",)

    style = ttk.Style()
    style.configure("Custom.Treeview", rowheight=100)
    style.configure("Custom.Treeview.Heading", font=("Verdana Bold", 30))
    treeview = ttk.Treeview(treeview_frame, columns=columns, show="headings", style="Custom.Treeview")

    # Set column headings
    for col in columns:
        treeview.column(col,anchor=tk.CENTER)
        treeview.heading(col, text=col)

    # Increase font size for treeview
    treeview.tag_configure('tag1',font=("Verdana",13))
    
    # Pack the treeview and add a scrollbar
    treeview.pack(fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(treeview_frame, orient="vertical", command=treeview.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    treeview.config(yscrollcommand=scrollbar.set)

    def refresh_notices():
        new_notice_result = get_notice_from_db(conn)
        treeview.delete(*treeview.get_children())
        for row in new_notice_result:
            row = list(row)
            row = tuple(string.replace('\n', ' ') for string in row)
            treeview.insert("","end",values=row,tags="tag1")

    buttons = [
        tk.Button(button_frame, text="Add Record", command=add_record, **button_style),
        tk.Button(button_frame, text="View Record", command=view_record, **button_style),
        tk.Button(button_frame, text="Search Record", command=search_record, **button_style),
        tk.Button(button_frame, text="Delete Record", command=delete_record, **button_style),
        tk.Button(button_frame, text="Publish Notice", command=publish_notice, **button_style),
        tk.Button(button_frame, text="Refresh Notices", command=refresh_notices, **button_style)
    ]

    # Pack buttons with some padding
    for button in buttons:
        button.pack(pady=5, padx=10)


    logout_button = tk.Button(button_frame,text="Logout",command=master.destroy,**logout_style)
    logout_button.pack(side=tk.BOTTOM,pady=20,fill=tk.X)
    notice_result = get_notice_from_db(conn)

    for row in notice_result:
        row = list(row)
        row = tuple(string.replace('\n', ' ') for string in row)
        treeview.insert("","end",values=row,tags="tag1")


    root.mainloop()
    
def create_teacher_frame(master):
    teacher_frame = tk.Toplevel(master)
    teacher_frame.title("LearnSys - Teacher Mode")
    teacher_frame.geometry('800x600')
    teacher_frame.state('zoomed')
        
    def view_class():
        view_class_frame = tk.Toplevel(master)
        view_class_frame.title("View Class")

        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 500) // 2
        view_class_frame.geometry(f"500x500+{x}+{y}")
            
        view_class_frame.configure(bg="#333333")

        text_font = ("Verdana",12)

        title_label = tk.Label(view_class_frame, text="LearnSys", font=("Verdana Bold",16), bg="#333333", fg="white")
        title_label.pack(pady=10)
        sub_title_label = tk.Label(view_class_frame, text="View your class.", font=("Verdana Bold",12), bg="#333333", fg="white")
        sub_title_label.pack(pady=10)    

        treeview_frame2 = tk.Frame(view_class_frame, bg="#333333")
        treeview_frame2.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create columns for the Treeview
        columns = ("ID", "Name", "Password","Class","Identity")
        column_sizes = (10,30,30,10,10)

        style = ttk.Style()
        style.configure("Custom1.Treeview", background="white", foreground="#333333")
        style.configure("Custom1.Treeview.Heading", font=("Verdana Bold", 9))
        treeview2 = ttk.Treeview(treeview_frame2, columns=columns, show="headings", style="Custom1.Treeview")

        # Set column headings
        for col in columns:
            treeview2.heading(col, text=col)

        for col,size in zip(columns,column_sizes):
            treeview2.column(col,width=size,anchor=tk.CENTER)

        # Add a vertical scrollbar
        scrollbar = ttk.Scrollbar(treeview_frame2, orient="vertical", command=treeview.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        treeview2.config(yscrollcommand=scrollbar.set)

        # Pack the Treeview
        treeview2.pack(fill=tk.BOTH, expand=True)

        res = get_class_from_db(currentUser[3],currentUser[4],conn)

        if res == []:
            messagebox.showwarning("Warning!","No results found.")
        else:
            for row in res:
                treeview2.insert("","end",values=row)

    def add_remark():
        add_remark_frame = tk.Toplevel(master)
        add_remark_frame.title("Add Remark")

        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 500) // 2
        add_remark_frame.geometry(f"500x500+{x}+{y}")
            
        add_remark_frame.configure(bg="#333333")

        text_font = ("Verdana",12)

        title_label = tk.Label(add_remark_frame, text="LearnSys", font=("Verdana Bold",16), bg="#333333", fg="white")
        title_label.pack(pady=10)
        sub_title_label = tk.Label(add_remark_frame, text="Update student remark.", font=("Verdana Bold",12), bg="#333333", fg="white")
        sub_title_label.pack(pady=10)
        name_label = tk.Label(add_remark_frame, text="👤 Name:", font=text_font, bg="#333333", fg="white")
        name_label.pack(pady=(10, 5))  # Lower the username label
        name_entry = tk.Entry(add_remark_frame, font=text_font, bg="#333333", fg="white", insertbackground="purple", bd=2, relief=tk.GROOVE)
        name_entry.pack(pady=5)  # Lower the username entry field    
        remark_label = tk.Label(add_remark_frame, text="📢 Remark:", font=text_font, bg="#333333", fg="white")
        remark_label.pack(pady=(10, 5))  # Lower the username label
        remark_entry = tk.Text(add_remark_frame,font=text_font, bg="#333333", fg="white", bd=2, relief=tk.GROOVE,height=5,insertbackground="#FFFFFF")
        remark_entry.pack(fill=tk.X,pady=10)  

        def on_publish_clicked():
            name_entry_text = name_entry.get()
            remark_entry_text = remark_entry.get("1.0",'end-1c')
            add_remark_to_db(name_entry_text,currentUser[3],currentUser[4],remark_entry_text,conn)

        search_button = tk.Button(add_remark_frame, text="Send Remark!", command=on_publish_clicked,font=text_font, bg="green", fg="white", width=15, bd=0)
        search_button.pack(pady=10)

    teacher_frame.configure(bg="#333333")

    title_label = tk.Label(teacher_frame, text="LearnSys - Teacher Panel", font=("Verdana Bold", 26), bg="#333333", fg="white")
    title_label.pack(side=tk.TOP, pady=10, fill=tk.X)

    
    # Create a frame to hold the buttons on the left
    button_frame = tk.Frame(teacher_frame, bg="#333333")
    button_frame.pack(side=tk.LEFT, fill=tk.Y)

    # Define button style
    button_style = {"bg": "green", "fg": "white", "width": 15, "bd": 0, "font": ("Verdana", 12)}
    logout_style = {"bg": "#8B0000", "fg": "white", "width": 15, "bd": 0, "font": ("Verdana", 12)}
    
    # Create a treeview on the right
    treeview_frame = tk.Frame(teacher_frame, bg="#333333")
    treeview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    columns = ("Recent Notices",)

    style = ttk.Style()
    style.configure("Custom.Treeview", rowheight=100)
    style.configure("Custom.Treeview.Heading", font=("Verdana Bold", 30))
    treeview = ttk.Treeview(treeview_frame, columns=columns, show="headings", style="Custom.Treeview")

    # Set column headings
    for col in columns:
        treeview.column(col,anchor=tk.CENTER)
        treeview.heading(col, text=col)

    # Increase font size for treeview
    treeview.tag_configure('tag1',font=("Verdana",13))
    
    # Pack the treeview and add a scrollbar
    treeview.pack(fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(treeview_frame, orient="vertical", command=treeview.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    treeview.config(yscrollcommand=scrollbar.set)

    def refresh_notices():
        new_notice_result = get_notice_from_db(conn)
        treeview.delete(*treeview.get_children())
        for row in new_notice_result:
            row = list(row)
            row = tuple(string.replace('\n', ' ') for string in row)
            treeview.insert("","end",values=row,tags="tag1")

    buttons = [
        tk.Button(button_frame, text="View Class", command=view_class, **button_style),
        tk.Button(button_frame, text="Add Remark", command=add_remark, **button_style),
        tk.Button(button_frame, text="Refresh Notices", command=refresh_notices, **button_style)
    ]

    # Pack buttons with some padding
    for button in buttons:
        button.pack(pady=5, padx=10)


    logout_button = tk.Button(button_frame,text="Logout",command=master.destroy,**logout_style)
    logout_button.pack(side=tk.BOTTOM,pady=20,fill=tk.X)
    notice_result = get_notice_from_db(conn)

    for row in notice_result:
        row = list(row)
        row = tuple(string.replace('\n', ' ') for string in row)
        treeview.insert("","end",values=row,tags="tag1")


    root.mainloop()

def create_student_frame(master):
    student_frame = tk.Toplevel(master)
    student_frame.title("LearnSys - Student Mode")
    student_frame.geometry('800x600')
    student_frame.state('zoomed')

    def view_remark():
        get_remark_from_db(currentUser[1],currentUser[3],currentUser[4],conn)

    student_frame.configure(bg="#333333")

    title_label = tk.Label(student_frame, text="LearnSys - Student Panel", font=("Verdana Bold", 26), bg="#333333", fg="white")
    title_label.pack(side=tk.TOP, pady=10, fill=tk.X)

    
    # Create a frame to hold the buttons on the left
    button_frame = tk.Frame(student_frame, bg="#333333")
    button_frame.pack(side=tk.LEFT, fill=tk.Y)

    # Define button style
    button_style = {"bg": "green", "fg": "white", "width": 15, "bd": 0, "font": ("Verdana", 12)}
    logout_style = {"bg": "#8B0000", "fg": "white", "width": 15, "bd": 0, "font": ("Verdana", 12)}
    
    # Create a treeview on the right
    treeview_frame = tk.Frame(student_frame, bg="#333333")
    treeview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    columns = ("Recent Notices",)

    style = ttk.Style()
    style.configure("Custom.Treeview", rowheight=100)
    style.configure("Custom.Treeview.Heading", font=("Verdana Bold", 30))
    treeview = ttk.Treeview(treeview_frame, columns=columns, show="headings", style="Custom.Treeview")

    # Set column headings
    for col in columns:
        treeview.column(col,anchor=tk.CENTER)
        treeview.heading(col, text=col)

    # Increase font size for treeview
    treeview.tag_configure('tag1',font=("Verdana",13))
    
    # Pack the treeview and add a scrollbar
    treeview.pack(fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(treeview_frame, orient="vertical", command=treeview.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    treeview.config(yscrollcommand=scrollbar.set)

    def refresh_notices():
        new_notice_result = get_notice_from_db(conn)
        treeview.delete(*treeview.get_children())
        for row in new_notice_result:
            row = list(row)
            row = tuple(string.replace('\n', ' ') for string in row)
            treeview.insert("","end",values=row,tags="tag1")

    buttons = [
        tk.Button(button_frame, text="View Remark", command=view_remark, **button_style),
        tk.Button(button_frame, text="Refresh Notices", command=refresh_notices, **button_style)
    ]

    # Pack buttons with some padding
    for button in buttons:
        button.pack(pady=5, padx=10)


    logout_button = tk.Button(button_frame,text="Logout",command=master.destroy,**logout_style)
    logout_button.pack(side=tk.BOTTOM,pady=20,fill=tk.X)
    notice_result = get_notice_from_db(conn)

    for row in notice_result:
        row = list(row)
        row = tuple(string.replace('\n', ' ') for string in row)
        treeview.insert("","end",values=row,tags="tag1")


    root.mainloop()

def login():
    global currentUser

    username = username_entry.get()
    password = password_entry.get()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE Name = %s", (username,))

    info = cursor.fetchall()
    if info == []:
        messagebox.showerror("Login Unsuccessful", "No user found!")
    else:
        correct_pass = info[0][2]
        if password == correct_pass:
            currentUser = (info[0][0], info[0][1], info[0][2],info[0][3],info[0][4],info[0][5])
            messagebox.showinfo("Login Successful", "Successfully logged in!")

            root.withdraw()
            if info[0][1] == 'RootAdmin':
                root.withdraw()  # Hide the main window
                create_admin_frame(root)  # Pass the main window as an argument to the admin frame function
                messagebox.showinfo("Logout Invoked","You have been logged out.")
                currentUser = None
                create_loading_screen()
            elif info[0][5] == "Teacher":
                root.withdraw()
                create_teacher_frame(root)
                messagebox.showinfo("Logout Invoked","You have been logged out.")
                currentUser = None
                create_loading_screen()
            elif info[0][5] == "Student":
                root.withdraw()
                create_student_frame(root)
                messagebox.showinfo("Logout Invoked","You have been logged out.")
                currentUser = None
                create_loading_screen()
        else:
            messagebox.showerror("Login Unsuccessful", "Incorrect Password")

create_loading_screen()