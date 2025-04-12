import cv2
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
from PIL import Image as PIL_Image, ImageTk
import customtkinter
import tkinter as tk
from tkinter import simpledialog, messagebox

def create_folder(name):
    dataset_folder = "face_rec_dataset"
    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)

    person_folder = os.path.join(dataset_folder, name)
    if not os.path.exists(person_folder):
        os.makedirs(person_folder)
    return person_folder

def capture_photos_gui(name_entry, preview_label):
    name = name_entry.get()
    if not name.isalpha():
        messagebox.showerror("Error", "Invalid name. Please use only alphabetic characters.")
        return

    folder = create_folder(name)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        messagebox.showerror("Error", "Could not access the webcam.")
        return

    photo_count = 0
    messagebox.showinfo("Info", f"Taking photos for {name}. Press SPACE to capture, 'q' to quit the capture window.")

    def update_frame():
        nonlocal photo_count
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = PIL_Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)
            preview_label.imgtk = img_tk
            preview_label.configure(image=img_tk)
        preview_label.after(10, update_frame)

    def on_key(event):
        nonlocal photo_count
        if event.char == ' ':  # Space key to capture photo
            ret, frame = cap.read()
            if ret:
                photo_count += 1
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}.jpg"
                filepath = os.path.join(folder, filename)
                cv2.imwrite(filepath, frame)
                messagebox.showinfo("Capture", f"Photo {photo_count} saved: {filename}")
        elif event.char == 'q':  # 'q' key to quit
            cap.release()
            capture_window.destroy()
            messagebox.showinfo("Info", f"Photo capture completed. {photo_count} photos saved for {name}.")

    capture_window = customtkinter.CTkToplevel(root)
    capture_window.title("Capture Photos")
    capture_window.geometry("600x500")
    capture_window.bind('<Key>', on_key)

    preview_label = customtkinter.CTkLabel(capture_window, text="")
    preview_label.pack(fill="both", expand=True, padx=10, pady=10)

    update_frame()

def open_capture_window():
    name_dialog = simpledialog.askstring("Input", "Enter the name of the person:", parent=root)
    if name_dialog:
        capture_window = customtkinter.CTkToplevel(root)
        capture_window.title(f"Capture Photos for {name_dialog}")
        capture_window.geometry("600x500")

        preview_label = customtkinter.CTkLabel(capture_window, text="Webcam Feed")
        preview_label.pack(fill="both", expand=True, padx=10, pady=10)

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            messagebox.showerror("Error", "Could not access the webcam.")
            return

        def update_preview():
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = PIL_Image.fromarray(frame_rgb)
                img_tk = ImageTk.PhotoImage(image=img)
                preview_label.imgtk = img_tk
                preview_label.configure(image=img_tk)
            preview_label.after(10, update_preview)

        def capture_and_save(event):
            nonlocal photo_count
            folder = create_folder(name_dialog)
            ret, frame = cap.read()
            if ret:
                photo_count += 1
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name_dialog}_{timestamp}.jpg"
                filepath = os.path.join(folder, filename)
                cv2.imwrite(filepath, frame)
                messagebox.showinfo("Capture", f"Photo {photo_count} saved: {filename}")

        def close_capture():
            cap.release()
            capture_window.destroy()
            messagebox.showinfo("Info", f"Photo capture completed. {photo_count} photos saved for {name_dialog}.")

        photo_count = 0
        capture_window.bind('<space>', capture_and_save)
        capture_window.protocol("WM_DELETE_WINDOW", close_capture) # Handle window close button

        update_preview()

print("Face Data Collection GUI")

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

root = customtkinter.CTk() 
root.geometry("400x300")
root.title("Face Data Collection")

frame5 = customtkinter.CTkFrame(root, width=500, height=300) # Frame right lower
frame5.pack(fill="both" ,padx=(10,10), pady=(5,10), expand=True)



frame5.grid_columnconfigure((0, 1, 2), weight=1)

SetUp = customtkinter.CTkLabel(frame5, text='Instructions', font=('', 20, 'bold'))
SetUp.grid(column=0, row=0, columnspan=3, pady=10, padx=10 )

SetUp1 = customtkinter.CTkLabel(frame5, text='1. Add user name.', font=('', 15))
SetUp1.grid(column=1, row=1, pady=0, padx=(50,0), sticky="w")

SetUp2 = customtkinter.CTkLabel(frame5, text='2. Capture 8 images of user.', font=('', 15))
SetUp2.grid(column=1, row=2, pady=0, padx=(50,0), sticky="w")

SetUp3 = customtkinter.CTkLabel(frame5, text='3. Press "Space" to capture image.', font=('', 15))
SetUp3.grid(column=1, row=3,  pady=0, padx=(50,0), sticky="w")

SetUp4 = customtkinter.CTkLabel(frame5, text='4. Press "Q" to exit.', font=('', 15))
SetUp4.grid(column=1, row=4, pady=0, padx=(50,0), sticky="w")

SetUp5 = customtkinter.CTkLabel(frame5, text='5. Close this Window & Confirm User.', font=('', 15))
SetUp5.grid(column=1, row=5,  pady=0, padx=(50,0), sticky="w")


Button_Start = customtkinter.CTkButton(frame5, text="Start Data Collection", command=open_capture_window)
Button_Start.grid(column=0, row=6,columnspan=3, pady=(20, 10), padx=5)

root.mainloop()