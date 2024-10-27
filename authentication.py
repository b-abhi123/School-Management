import tkinter as tk
from tkinter import messagebox
import mysql.connector as sql
global currentUser
currentUser = None

def create_loading_screen():
    loading_screen = tk.Tk()
    loading_screen.title("Loading...")
    loading_screen.geometry("300x100")

    loading_screen.withdraw()
    messagebox.showinfo("LearnSys", "Please wait while the program connects to the database.")

    try:
        global conn
        conn = sql.connect(
            host="",
            user="",
            password="",
            database="")
        print(conn.is_connected())
        loading_screen.destroy()
        create_main_window()

    except Exception as e:
        messagebox.showerror("Connection Error", "Unable to connect to the database.")
        print(e)
        loading_screen.destroy()

def create_main_window():
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


def login():
    global currentUser

    username = username_entry.get()
    password = password_entry.get()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))

    info = cursor.fetchall()
    if info == []:
        messagebox.showerror("Login Unsuccessful", "No user found!")
    else:
        correct_pass = info[0][2]
        if password == correct_pass:
            currentUser = (info[0][0], info[0][1], info[0][2])
            messagebox.showinfo("Login Successful", "Successfully logged in!")
            messagebox.showinfo("Note","UI is currently under development.\nPlease check your shell.")

            root.withdraw()
            #run your function after this
            '''if info[0][1] == 'RootAdmin':
                root.withdraw()  # Hide the main window
                create_admin_frame(root)  # Pass the main window as an argument to the admin frame function
                root.destroy()'''
        else:
            messagebox.showerror("Login Unsuccessful", "Incorrect Password")


create_loading_screen()
