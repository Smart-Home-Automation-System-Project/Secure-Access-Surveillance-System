import subprocess
import os
import sys
from tkinter import *
import customtkinter
import shutil
from tkinter import messagebox

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.db_service import DatabaseService

db_service = DatabaseService()

# #######################################
# # Popup for user confirmation successfully completed

def open_popup(txt): #popup window function
    popup_window = customtkinter.CTkToplevel(root)
    popup_window.title("Notification")  # Changed from "Error" to "Notification" since it's not actually an error
    popup_window.resizable(False, False)
    popup_window.geometry("300x150")  # Set a fixed size
    
    # Center the popup on the screen
    popup_window.update_idletasks()  # Update to get correct window dimensions
    width = popup_window.winfo_width()
    height = popup_window.winfo_height()
    x = (popup_window.winfo_screenwidth() // 2) - (width // 2)
    y = (popup_window.winfo_screenheight() // 2) - (height // 2)
    popup_window.geometry(f'{width}x{height}+{x}+{y}')
    
    label = customtkinter.CTkLabel(popup_window, text=txt)
    label.pack(padx=20, pady=20)
    close_button = customtkinter.CTkButton(popup_window, text="Ok", command=popup_window.destroy)
    close_button.pack(pady=10)
    
    # Make sure the window is ready before setting grab
    popup_window.update()
    
    # Try-except block to handle the grab_set error
    try:
        popup_window.grab_set()  # Make the popup modal
    except Exception as e:
        print(f"Warning: Could not set window grab: {e}")
    
    # Keep the popup on top
    popup_window.lift()
    popup_window.attributes('-topmost', True)
    popup_window.after(10, lambda: popup_window.attributes('-topmost', False))

# #######################################


def StartNow():
    
    """Starts the gui_capture_face.py script and closes the current window."""
    try:
        # Construct the full path to gui_capture_face.py
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "gui",
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
    """
    Trains the face recognition model and adds user to the database as authorized.
    """
    try:
        # Get list of folders in face_rec_dataset directory (each folder is a user)
        dataset_folder = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "face_rec_dataset"
        )
        
        if not os.path.exists(dataset_folder):
            open_popup("No users found. Please add a user first.")
            return
            
        # Get the most recently modified folder (newest user)
        user_folders = [os.path.join(dataset_folder, d) for d in os.listdir(dataset_folder) 
                        if os.path.isdir(os.path.join(dataset_folder, d))]
        
        if not user_folders:
            open_popup("No users found. Please add a user first.")
            return
            
        # Sort by modification time (newest first)
        latest_user_folder = max(user_folders, key=os.path.getmtime)
        username = os.path.basename(latest_user_folder)
        
        # Add user to database
        db_service = DatabaseService()
        try:
            db_service.add_user(username, authorized=True)
            print(f"User {username} added to database as authorized.")
        except Exception as e:
            print(f"Failed to add user to database: {str(e)}")
            # If there's an error adding user (like duplicate), continue anyway
        
        # Start face recognition model training
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "util",
            "face_rec_model_training.py"
        )
        print(f"Attempting to run: {script_path}")
        subprocess.Popen([sys.executable, script_path])
        print("face_rec_model_training.py started.")
        
        # Show confirmation popup
        open_popup(f"User {username} has been confirmed and added as authorized.")
        
    except FileNotFoundError:
        print(f"Error: Script or directory not found")
        open_popup("Error: Could not find necessary files or directories.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        open_popup(f"An error occurred: {str(e)}")
        return
    
def load_users():
    """Load all users from the database"""
    users_list = db_service.get_all_users()  # You'll need to add this method to db_service
    return users_list

def remove_user():
    """Delete selected user from the database and remove their images"""
    if not user_listbox.curselection():
        open_popup("Please select a user to delete")
        return
    
    selected_index = user_listbox.curselection()[0]
    selected_user = user_listbox.get(selected_index)
    
    # Confirm before deleting
    confirm = messagebox.askyesno("Confirm Deletion", 
                                  f"Are you sure you want to delete user '{selected_user}'?\n\n"
                                  "This will permanently remove:\n"
                                  "1. User's database record\n"
                                  "2. All captured facial images\n\n"
                                  "This action cannot be undone.")
    
    if not confirm:
        return
        
    try:
        # 1. Delete from database
        db_service.remove_user(selected_user)
        
        # 2. Delete user's images folder
        dataset_folder = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "face_rec_dataset", 
            selected_user
        )
        if os.path.exists(dataset_folder):
            shutil.rmtree(dataset_folder)
            
        # 3. Retrain the model (after deleting a user)
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "util",
            "face_rec_model_training.py"
        )
        subprocess.Popen([sys.executable, script_path])
        
        # 4. Update the listbox
        refresh_user_list()
        
        open_popup(f"User '{selected_user}' has been deleted successfully")
        
    except Exception as e:
        open_popup(f"Error deleting user: {str(e)}")
        print(f"Error deleting user: {e}")

def refresh_user_list():
    """Refresh the user list in the listbox"""
    user_listbox.delete(0, END)  # Clear current list
    users = load_users()
    for user in users:
        user_listbox.insert(END, user)

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

root = customtkinter.CTk()
root.geometry("1200x700")
root.title("Login Interface")
root.resizable(False, False)  # 🔒 Disable resizing

Mainframe1 = customtkinter.CTkFrame(root, width=1200, height=600)
Mainframe1.pack(fill="both", expand=True)

frame1 = customtkinter.CTkFrame(Mainframe1, width=600, height=600) # main left frame
frame1.pack(side='left', fill='both',  padx=(20,10), pady=20, expand=True)

frame2 = customtkinter.CTkFrame(Mainframe1, width=600, height=600) # main right frame
frame2.pack(side='right', fill='both', padx=(10,20), pady=20, expand=True)

# Tab section is kept, but without camera functionality
tab = customtkinter.CTkTabview(frame2) # Moved tabview to frame1
tab.pack(fill="both", expand=True)

tab1 = tab.add("Gate Camera")
tab2 = tab.add("Door Camera")

Title1 = customtkinter.CTkLabel(tab1 , text='Gate Camera | LIVE', font=('', 25, 'bold'))
Title1.pack(pady=25, padx=40)

Title2 = customtkinter.CTkLabel(tab2 , text='Door Camera | LIVE', font=('', 25, 'bold'))
Title2.pack(pady=25, padx=40)

frame3 = customtkinter.CTkFrame(tab1 , width=550, height=450) # Frame for gate camera feed
frame3.pack(fill='both', padx=(10,10), pady=(0, 20), expand=True)

camera_label1 = customtkinter.CTkLabel(frame3, text="Camera feed not available")  # Label to display message instead of camera feed
camera_label1.pack(fill="both", expand=True)

frame3_1 = customtkinter.CTkFrame(tab2 , width=550, height=450) # Frame for door camera feed
frame3_1.pack(fill='both', padx=(10,10), pady=(0, 20), expand=True)

camera_label2 = customtkinter.CTkLabel(frame3_1, text="Camera feed not available")  # Label to display message instead of camera feed
camera_label2.pack(fill="both", expand=True)

# Camera capture code removed but commented sections kept
#cam1 = cv2.VideoCapture(0)  # Use 0 for the default web camera
#cam2 = cv2.VideoCapture(1)  # Try 1 for the secondary/door camera

# def update_frame(cam, camera_label):
#     ret, frame = cam.read()
#     if ret:
#         # Convert the OpenCV frame (BGR) to RGB
#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         # Convert to PIL Image
#         img = PIL_Image.fromarray(frame_rgb)  # Use the aliased name
#         # Convert to Tkinter PhotoImage
#         img_tk = ImageTk.PhotoImage(image=img)
#         camera_label.imgtk = img_tk  # Keep a reference to prevent garbage collection
#         camera_label.configure(image=img_tk)
#     camera_label.after(10, lambda: update_frame(cam, camera_label)) # Use lambda for correct parameter passing

# def start_web_camera():
#     update_frame(cam1, camera_label1)

# def start_door_camera():
#     update_frame(cam2, camera_label2)

# Start the camera updates
# start_web_camera()
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

Button_Start = customtkinter.CTkButton(frame5, text='Stat Now', command= StartNow)
Button_Start.grid(column=0, row=1, pady=(5, 10), padx=5)

SetUp = customtkinter.CTkLabel(frame5, text='Confirm User', font=('', 20, 'bold'))
SetUp.grid(column=3, row=0, pady=(20, 5), padx=5 )

Button_Start = customtkinter.CTkButton(frame5, text='Confirm', command= Confirm)
Button_Start.grid(column=3, row=1, pady=(5, 10), padx=5)

# User Management Section in frame4
user_management_label = customtkinter.CTkLabel(frame4, text="User Management", font=('', 20, 'bold'))
user_management_label.pack(pady=(15, 10))

user_frame = customtkinter.CTkFrame(frame4)
user_frame.pack(fill="both", padx=20, pady=10, expand=True)

# Create a scrollable listbox for users
user_list_frame = customtkinter.CTkFrame(user_frame)
user_list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

user_list_label = customtkinter.CTkLabel(user_list_frame, text="Registered Users:", font=('', 16))
user_list_label.pack(pady=(5, 5), anchor="w")

# Create a special scrollable frame for the listbox since CTk doesn't have a listbox
listbox_frame = Frame(user_list_frame, bg="#2b2b2b")  # Match dark theme
listbox_frame.pack(fill="both", expand=True)

scrollbar = Scrollbar(listbox_frame)
scrollbar.pack(side=RIGHT, fill=Y)

user_listbox = Listbox(listbox_frame, yscrollcommand=scrollbar.set, 
                       bg="#2b2b2b", fg="white", selectbackground="#1f538d",
                       font=('', 12), relief="flat", borderwidth=0)
user_listbox.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.config(command=user_listbox.yview)

# Buttons for user management
button_frame = customtkinter.CTkFrame(user_frame)
button_frame.pack(side="right", fill="y", padx=10, pady=10)

delete_button = customtkinter.CTkButton(button_frame, text="Delete User", 
                                        command=remove_user, 
                                        fg_color="#E74C3C")  # Red color for delete
delete_button.pack(padx=10, pady=10)

refresh_button = customtkinter.CTkButton(button_frame, text="Refresh List", 
                                         command=refresh_user_list)
refresh_button.pack(padx=10, pady=10)

# Load users initially
refresh_user_list()

root.mainloop()

# Release camera resources after the main loop - removed but kept as comments
# if cam1.isOpened():
#     cam1.release()
# if cam2.isOpened():
#     cam2.release()
# cv2.destroyAllWindows()