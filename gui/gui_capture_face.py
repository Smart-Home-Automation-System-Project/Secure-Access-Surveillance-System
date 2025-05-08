import cv2
import os
from datetime import datetime
from PIL import Image as PIL_Image, ImageTk
import customtkinter
import tkinter as tk
from tkinter import messagebox

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.db_service import DatabaseService

# Global root
preview_loop_id = None
db_service = DatabaseService()

def create_folder(name):
    dataset_folder = "face_rec_dataset"
    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)

    person_folder = os.path.join(dataset_folder, name)
    if not os.path.exists(person_folder):
        os.makedirs(person_folder)
    return person_folder

def capture_photos_gui(name):
    global preview_loop_id

    folder = create_folder(name)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        messagebox.showerror("Error", "Could not access the webcam.")
        return

    photo_count = 0

    capture_window = customtkinter.CTkToplevel(root)
    capture_window.title(f"Capture Photos for {name}")
    capture_window.geometry("600x500")

    preview_label = customtkinter.CTkLabel(capture_window, text="")
    preview_label.pack(fill="both", expand=True, padx=10, pady=10)

    def update_frame():
        global preview_loop_id
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = PIL_Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)
            preview_label.imgtk = img_tk
            preview_label.configure(image=img_tk)
        preview_loop_id = preview_label.after(10, update_frame)

    def on_key(event):
        nonlocal photo_count
        if event.char == ' ':
            ret, frame = cap.read()
            if ret:
                photo_count += 1
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}.jpg"
                filepath = os.path.join(folder, filename)
                cv2.imwrite(filepath, frame)
                messagebox.showinfo("Capture", f"Photo {photo_count} saved: {filename}")
        elif event.char == 'q':
            close_window()

    def close_window():
        if preview_loop_id:
            preview_label.after_cancel(preview_loop_id)
        cap.release()
        capture_window.destroy()
        
        # # Add user to database as authorized
        # if photo_count > 0:
        #     try:
        #         # Add user to the database with authorized=True
        #         db_service.add_user(name, authorized=True)
        #         messagebox.showinfo("Success", f"{name} has been added as an authorized user.")
        #     except Exception as e:
        #         messagebox.showerror("Database Error", f"Failed to add user to database: {str(e)}")
        
        messagebox.showinfo("Info", f"Photo capture completed. {photo_count} photos saved for {name}.")

    capture_window.bind("<Key>", on_key)
    capture_window.protocol("WM_DELETE_WINDOW", close_window)

    update_frame()

def open_capture_window():
    def on_submit():
        name = entry1.get() # Get the name of the user
        if not name.isalpha():
            messagebox.showerror("Invalid Name", "Please enter only alphabetic characters.")
        else:
            root1.destroy()
            capture_photos_gui(name)

    root1 = customtkinter.CTk()
    root1.title("Enter Your Name")
    root1.geometry('300x150')
    root1.resizable(0, 0)

    frame = customtkinter.CTkFrame(root1 , width=300 , height=150)
    frame.pack(fill="both", expand=True)

    customtkinter.CTkLabel(frame, text='Enter Your Name', font=('', 20)).pack(pady=5)
    entry1 = customtkinter.CTkEntry(frame, placeholder_text="First Name", width=200)
    entry1.pack(pady=10)
    customtkinter.CTkButton(frame, text="Submit", command=on_submit).pack(pady=10)

    root1.mainloop()

# Main GUI
print("Face Data Collection GUI")

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

root = customtkinter.CTk()
root.geometry("400x400")  # Made slightly taller for additional notes
root.title("Face Data Collection")

frame5 = customtkinter.CTkFrame(root)
frame5.pack(fill="both", expand=True, padx=10, pady=10)

frame5.grid_columnconfigure((0, 1, 2), weight=1)

SetUp = customtkinter.CTkLabel(frame5, text='Instructions', font=('', 20, 'bold'))
SetUp.grid(column=0, row=0, columnspan=3, pady=10, padx=10)

instructions = [
    "1. Enter User Name.",
    "2. Prepare for Capture.",
    "3. Don't close this window before capturing all.",
    "4. Capture Images (Press \"Space\").",
    "5. Capture 8 Images.",
    "6. Close Camera Window.",
    "7. Confirm User and Close."
]

for idx, text in enumerate(instructions, start=1):
    lbl = customtkinter.CTkLabel(frame5, text=text, font=('', 15))
    lbl.grid(column=1, row=idx, pady=0, padx=(50, 0), sticky="w")

note_label = customtkinter.CTkLabel(frame5, text="Note: User will be added as authorized automatically", 
                                    font=('', 12), text_color="#FFD700")
note_label.grid(column=0, row=8, columnspan=3, pady=(5, 0), padx=5)

Button_Start = customtkinter.CTkButton(frame5, text="Start Data Collection", command=open_capture_window)
Button_Start.grid(column=0, row=9, columnspan=3, pady=(10, 10), padx=5)

root.mainloop()