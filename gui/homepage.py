import subprocess
import cv2
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
from PIL import Image as PIL_Image, ImageTk  # Alias Image to PIL_Image

from tkinter import *
import customtkinter
import sys



# #######################################
# # Popup for user confirmation successfully completed

def open_popup(txt): #popup window function
    popup_window = customtkinter.CTkToplevel(root)
    popup_window.title("Error")
    popup_window.resizable(False, False)
    label = customtkinter.CTkLabel(popup_window, text=txt)
    label.pack(padx=20, pady=20)
    close_button = customtkinter.CTkButton(popup_window, text="Ok", command=popup_window.destroy)
    close_button.pack(pady=10)
    popup_window.grab_set()  # Make the popup modal


# #######################################


def StartNow():
    
    """Starts the gui_capture_face.py script and closes the current window."""
    try:
        # Construct the full path to gui_capture_face.py
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "src",
            "gui_capture_face.py"
        )
        print(f"Attempting to run: {script_path}")
        subprocess.Popen([sys.executable, script_path])
        print("gui_capture_face.py started.")
        # Close the current homepage window
    except FileNotFoundError:
        print(f"Error: Script not found at {script_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def Confirm():
    
    #############################
    # Temp Popup for user confirmation successfully completed
    open_popup("User confirmation successfully completed.")
    #############################

    """Starts the face_rec_model_training.py script and closes the current window."""
    try:
        # Construct the full path to face_rec_model_training.py
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "src",
            "face_rec_model_training.py"
        )
        print(f"Attempting to run: {script_path}")
        subprocess.Popen([sys.executable, script_path])
        print("face_rec_model_training.py started.")
        # Close the current homepage window
        
    except FileNotFoundError:
        print(f"Error: Script not found at {script_path}")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

root = customtkinter.CTk()
root.geometry("1200x600")
root.title("Login Interface")
root.resizable(False, False)  # 🔒 Disable resizing

Mainframe1 = customtkinter.CTkFrame(root, width=1200, height=600)
Mainframe1.pack(fill="both", expand=True)

frame1 = customtkinter.CTkFrame(Mainframe1, width=600, height=600) # main left frame
frame1.pack(side='left', fill='both',  padx=(20,10), pady=20, expand=True)

frame2 = customtkinter.CTkFrame(Mainframe1, width=600, height=600) # main right frame
frame2.pack(side='right', fill='both', padx=(10,20), pady=20, expand=True)

tab = customtkinter.CTkTabview(frame2) # Moved tabview to frame1
tab.pack(fill="both", expand=True)

tab1 = tab.add("Web Camera")
tab2 = tab.add("Door Camera")

Title1 = customtkinter.CTkLabel(tab1 , text='Web Camera | LIVE', font=('', 25, 'bold'))
Title1.pack(pady=25, padx=40)

Title2 = customtkinter.CTkLabel(tab2 , text='Door Camera | LIVE', font=('', 25, 'bold'))
Title2.pack(pady=25, padx=40)

frame3 = customtkinter.CTkFrame(tab1 , width=550, height=450) # Frame for web camera feed
frame3.pack(fill='both', padx=(10,10), pady=(0, 20), expand=True)

camera_label1 = customtkinter.CTkLabel(frame3, text="")  # Label to display web camera feed
camera_label1.pack(fill="both", expand=True)

frame3_1 = customtkinter.CTkFrame(tab2 , width=550, height=450) # Frame for door camera feed
frame3_1.pack(fill='both', padx=(10,10), pady=(0, 20), expand=True)

camera_label2 = customtkinter.CTkLabel(frame3_1, text="")  # Label to display door camera feed
camera_label2.pack(fill="both", expand=True)

cam1 = cv2.VideoCapture(0)  # Use 0 for the default web camera
#cam2 = cv2.VideoCapture(1)  # Try 1 for the secondary/door camera

def update_frame(cam, camera_label):
    ret, frame = cam.read()
    if ret:
        # Convert the OpenCV frame (BGR) to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert to PIL Image
        img = PIL_Image.fromarray(frame_rgb)  # Use the aliased name
        # Convert to Tkinter PhotoImage
        img_tk = ImageTk.PhotoImage(image=img)
        camera_label.imgtk = img_tk  # Keep a reference to prevent garbage collection
        camera_label.configure(image=img_tk)
    camera_label.after(10, lambda: update_frame(cam, camera_label)) # Use lambda for correct parameter passing

def start_web_camera():
    update_frame(cam1, camera_label1)

# def start_door_camera():
#     update_frame(cam2, camera_label2)

# Start the camera updates
start_web_camera()
# start_door_camera()

Dash = customtkinter.CTkLabel(frame1 , text='Dashboard', font=('', 30, 'bold'))
Dash.pack(pady=25, padx=50)

frame4 = customtkinter.CTkFrame(frame1, width=600, height=300) # Frame left upper
frame4.pack(fill="both", padx=(10,10), pady=(10,5), expand=True)

frame5 = customtkinter.CTkFrame(frame1, width=600, height=200) # Frame right lower
frame5.pack(fill="both" ,padx=(10,10), pady=(5,10), expand=True)



frame5.grid_columnconfigure((0, 1, 2, 3), weight=1)

SetUp = customtkinter.CTkLabel(frame5, text='Add User', font=('', 20, 'bold'))
SetUp.grid(column=0, row=0, pady=(20, 5), padx=5 )

# SetUp1 = customtkinter.CTkLabel(frame5, text='1. Add user name.', font=('', 15))
# SetUp1.grid(column=1, row=1, pady=0, padx=(50,0), sticky="w")

# SetUp2 = customtkinter.CTkLabel(frame5, text='2. Capture 8 images of user.', font=('', 15))
# SetUp2.grid(column=1, row=2, pady=0, padx=(50,0), sticky="w")

# SetUp3 = customtkinter.CTkLabel(frame5, text='3. Press "Space" to capture image.', font=('', 15))
# SetUp3.grid(column=1, row=3,  pady=0, padx=(50,0), sticky="w")

# SetUp4 = customtkinter.CTkLabel(frame5, text='4. Press "Q" to exit.', font=('', 15))
# SetUp4.grid(column=1, row=4, pady=0, padx=(50,0), sticky="w")

# SetUp5 = customtkinter.CTkLabel(frame5, text='5. Click "Submit" button to save images.', font=('', 15))
# SetUp5.grid(column=1, row=5,  pady=0, padx=(50,0), sticky="w")

Button_Start = customtkinter.CTkButton(frame5, text='Stat Now', command= StartNow)
Button_Start.grid(column=0, row=1, pady=(5, 10), padx=5)

SetUp = customtkinter.CTkLabel(frame5, text='Confirm User', font=('', 20, 'bold'))
SetUp.grid(column=3, row=0, pady=(20, 5), padx=5 )

Button_Start = customtkinter.CTkButton(frame5, text='Confirm', command= Confirm)
Button_Start.grid(column=3, row=1, pady=(5, 10), padx=5)

root.mainloop()

# Release camera resources after the main loop
if cam1.isOpened():
    cam1.release()
# if cam2.isOpened():
#     cam2.release()
cv2.destroyAllWindows()


