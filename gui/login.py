from tkinter import *
import customtkinter

def open_popup(txt): #popup window function
    popup_window = customtkinter.CTkToplevel(root)
    popup_window.title("Error")
    popup_window.resizable(False, False)
    label = customtkinter.CTkLabel(popup_window, text=txt)
    label.pack(padx=20, pady=20)
    close_button = customtkinter.CTkButton(popup_window, text="Close", command=popup_window.destroy)
    close_button.pack(pady=10)
    popup_window.grab_set()  # Make the popup modal

def Login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "admin" and password == "1234":
        print("Login successful")
        root.destroy()  # Close the login window
        import gui.homepage  # Import the homepage module (make sure it's in the same directory)
    else:
        print("Invalid credentials")
        open_popup("Invalid username or password")




customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

root = customtkinter.CTk()
root.geometry("350x300")
root.title("Login Interface")
root.resizable(False, False)  # 🔒 Disable resizing

Mainframe1 = customtkinter.CTkFrame(root, width=350, height=300)
Mainframe1.pack(fill="both", expand=True)

Frame1 = customtkinter.CTkFrame(Mainframe1, width=350, height=200)
Frame1.pack(fill='both', expand=True, padx=20, pady=20)

Frame2 = customtkinter.CTkFrame(Mainframe1, width=350, height=100)
Frame2.pack(fill='both', padx=20, pady=(0, 20))

# Configure grid layout
Frame1.grid_columnconfigure(0, weight=1)
Frame1.grid_columnconfigure(1, weight=1)

# Title
Title = customtkinter.CTkLabel(Frame1, text='Login', font=('', 25, 'bold'))
Title.grid(column=0, row=0, columnspan=2, pady=25, padx=40)

# Username
username_label = customtkinter.CTkLabel(Frame1, text="Username:")
username_label.grid(column=0, row=1, sticky="w", pady=5, padx=10)

username_entry = customtkinter.CTkEntry(Frame1, width=200, placeholder_text="Enter username")
username_entry.grid(column=1, row=1, pady=5, padx=10)

# Password
password_label = customtkinter.CTkLabel(Frame1, text="Password:")
password_label.grid(column=0, row=2, sticky="w", pady=5, padx=10)

password_entry = customtkinter.CTkEntry(Frame1, width=200, show="*", placeholder_text="Enter password")
password_entry.grid(column=1, row=2, pady=5, padx=10)

# Configure Frame2 grid layout for centering buttons
Frame2.grid_columnconfigure((0, 1, 2, 3), weight=1)  # 3 columns for spacing

# Buttons centered in Frame2
button_login = customtkinter.CTkButton(master=Frame2, text=" Login ", width=100, command=Login)
button_login.grid(column=1, row=0, pady=(10, 10), padx=5, sticky="e")

button_register = customtkinter.CTkButton(master=Frame2, text="Register", width=100,  command=lambda: print("Register clicked"))
button_register.grid(column=2, row=0, pady=(10, 10), padx=5, sticky="w")

root.mainloop()
