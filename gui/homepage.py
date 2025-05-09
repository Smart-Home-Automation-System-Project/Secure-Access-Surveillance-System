import subprocess
import os
import sys
from tkinter import *
import customtkinter
import shutil
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import threading
import requests
from io import BytesIO
from tkinter import ttk

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.db_service import DatabaseService
from camera.camera_manager import CameraManager

db_service = DatabaseService()

# Global variables for cameras
gate_camera = None
door_camera = None
camera_running = True

def open_popup(txt):
    popup_window = customtkinter.CTkToplevel(root)
    popup_window.title("Notification")
    popup_window.resizable(False, False)
    popup_window.geometry("300x150")
    
    # Center the popup on the screen
    popup_window.update_idletasks()
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
    
    try:
        popup_window.grab_set()
    except Exception as e:
        print(f"Warning: Could not set window grab: {e}")
    
    popup_window.lift()
    popup_window.attributes('-topmost', True)
    popup_window.after(10, lambda: popup_window.attributes('-topmost', False))

def open_logs_window():
    """Open a window to display access logs and intruder images"""
    logs_window = customtkinter.CTkToplevel(root)
    logs_window.title("Access Logs & Intruder Images")
    logs_window.geometry("1000x700")
    logs_window.resizable(True, True)
    
    # Create a tabview for different types of logs
    tab_view = customtkinter.CTkTabview(logs_window)
    tab_view.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create tabs
    tab1 = tab_view.add("Recent Access")
    tab2 = tab_view.add("Unauthorized Access")
    tab3 = tab_view.add("Intruder Images")
    
    # Recent Access Logs Tab
    frame_recent = customtkinter.CTkFrame(tab1)
    frame_recent.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create a style for the treeview
    style = ttk.Style()
    style.configure("Treeview", 
                    background="#2b2b2b",
                    foreground="white",
                    fieldbackground="#2b2b2b")
    style.map('Treeview', background=[('selected', '#1f538d')])
    
    # Create a treeview for recent access logs
    recent_tree = ttk.Treeview(frame_recent, columns=("Timestamp", "Name", "Status", "Method"), show="headings")
    recent_tree.heading("Timestamp", text="Timestamp")
    recent_tree.heading("Name", text="Name")
    recent_tree.heading("Status", text="Status")
    recent_tree.heading("Method", text="Method")
    
    # Set column widths
    recent_tree.column("Timestamp", width=180)
    recent_tree.column("Name", width=150)
    recent_tree.column("Status", width=100)
    recent_tree.column("Method", width=100)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(frame_recent, orient="vertical", command=recent_tree.yview)
    recent_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    recent_tree.pack(fill="both", expand=True)
    
    # Unauthorized Access Tab
    frame_unauth = customtkinter.CTkFrame(tab2)
    frame_unauth.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create a treeview for unauthorized access
    unauth_tree = ttk.Treeview(frame_unauth, columns=("Timestamp", "Name", "Method"), show="headings")
    unauth_tree.heading("Timestamp", text="Timestamp")
    unauth_tree.heading("Name", text="Name")
    unauth_tree.heading("Method", text="Method")
    
    # Set column widths
    unauth_tree.column("Timestamp", width=180)
    unauth_tree.column("Name", width=150)
    unauth_tree.column("Method", width=100)
    
    # Add scrollbar
    scrollbar2 = ttk.Scrollbar(frame_unauth, orient="vertical", command=unauth_tree.yview)
    unauth_tree.configure(yscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="right", fill="y")
    unauth_tree.pack(fill="both", expand=True)
    
    # Intruder Images Tab
    frame_images = customtkinter.CTkFrame(tab3)
    frame_images.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create a frame for image display
    image_display_frame = customtkinter.CTkFrame(frame_images)
    image_display_frame.pack(fill="both", expand=True, side="left")
    
    # Create a canvas for displaying the image
    image_canvas = Canvas(image_display_frame, bg="#2b2b2b", highlightthickness=0)
    image_canvas.pack(fill="both", expand=True, side="left")
    
    # Create a sidebar for image list
    list_frame = customtkinter.CTkFrame(frame_images, width=250)
    list_frame.pack(fill="y", side="right", padx=(5, 0))
    
    # Create a listbox for images
    image_listbox_frame = Frame(list_frame, bg="#2b2b2b")
    image_listbox_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Add scrollbar to listbox
    list_scrollbar = Scrollbar(image_listbox_frame)
    list_scrollbar.pack(side="right", fill="y")
    
    # Create listbox
    image_listbox = Listbox(image_listbox_frame, 
                          bg="#2b2b2b", fg="white", 
                          selectbackground="#1f538d",
                          yscrollcommand=list_scrollbar.set,
                          font=('', 10))
    image_listbox.pack(fill="both", expand=True, side="left")
    list_scrollbar.config(command=image_listbox.yview)
    
    # Function to load image from URL
    def load_image(url):
        try:
            # Download image from URL
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Convert to PIL Image
            image = Image.open(BytesIO(response.content))
            
            # Resize image to fit in canvas
            canvas_width = image_canvas.winfo_width()
            canvas_height = image_canvas.winfo_height()
            
            # Calculate scaling factor while preserving aspect ratio
            img_width, img_height = image.size
            scale = min(canvas_width/img_width, canvas_height/img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize the image
            image = image.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Clear previous image
            image_canvas.delete("all")
            
            # Display the image
            image_canvas.create_image(canvas_width//2, canvas_height//2, image=photo, anchor="center")
            image_canvas.image = photo  # Keep a reference
            
        except Exception as e:
            print(f"Error loading image: {e}")
            # Display error message on canvas
            image_canvas.delete("all")
            image_canvas.create_text(image_canvas.winfo_width()//2, 
                                   image_canvas.winfo_height()//2,
                                   text=f"Error loading image:\n{str(e)}",
                                   fill="white",
                                   font=('', 12))
    
    # Handle listbox selection
    def on_image_select(event):
        if image_listbox.curselection():
            index = image_listbox.curselection()[0]
            image_data = image_list[index]
            url = image_data[2]  # URL is stored in the third position
            load_image(url)
            
            # Display timestamp and name
            status_label.configure(text=f"Timestamp: {image_data[0]}\nName: {image_data[1]}")
    
    image_listbox.bind("<<ListboxSelect>>", on_image_select)
    
    # Status label
    status_label = customtkinter.CTkLabel(list_frame, text="Select an image", height=40,
                                        wraplength=240, justify="left")
    status_label.pack(fill="x", padx=5, pady=(0, 5))
    
    # Refresh button for each tab
    refresh_button1 = customtkinter.CTkButton(tab1, text="Refresh", 
                                           command=lambda: load_recent_logs())
    refresh_button1.pack(pady=10)
    
    refresh_button2 = customtkinter.CTkButton(tab2, text="Refresh", 
                                           command=lambda: load_unauthorized_logs())
    refresh_button2.pack(pady=10)
    
    refresh_button3 = customtkinter.CTkButton(tab3, text="Refresh", 
                                           command=lambda: load_images())
    refresh_button3.pack(pady=10)
    
    # Data loading functions
    def load_recent_logs():
        recent_tree.delete(*recent_tree.get_children())
        logs = db_service.get_recent_access_logs(30)  # Get 30 most recent logs
        for log in logs:
            timestamp, name, authorized, unlock_method = log
            status = "AUTHORIZED" if authorized else "UNAUTHORIZED"
            recent_tree.insert("", "end", values=(timestamp, name, status, unlock_method))
    
    def load_unauthorized_logs():
        unauth_tree.delete(*unauth_tree.get_children())
        logs = db_service.get_unauthorized_attempts()
        for log in logs:
            timestamp, name, unlock_method = log
            unauth_tree.insert("", "end", values=(timestamp, name, unlock_method))
    
    image_list = []  # Global to store image data
    
    def load_images():
        image_listbox.delete(0, END)
        nonlocal image_list
        image_list = db_service.get_unauthorized_attempts_with_images(20)  # Get 20 most recent
        
        for i, (timestamp, name, url) in enumerate(image_list):
            image_listbox.insert(END, f"{timestamp} - {name}")
    
    # Load data initially
    load_recent_logs()
    load_unauthorized_logs()
    load_images()
    
    # Resize handler for image canvas
    def on_canvas_configure(event):
        # When canvas is resized, reload current image if any
        if image_listbox.curselection():
            on_image_select(None)
    
    image_canvas.bind("<Configure>", on_canvas_configure)

def update_gate_camera():
    """Update gate camera feed using CameraManager"""
    global gate_camera, camera_running
    
    if not camera_running:
        return
    
    try:
        # Get frame from camera manager
        frame = gate_camera.get_frame()
        
        if frame is not None:
            # Resize frame to fit in the UI
            frame = cv2.resize(frame, (550, 400))
            
            # Convert to RGB for tkinter display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            img = Image.fromarray(frame_rgb)
            
            # Convert to Tkinter PhotoImage
            img_tk = ImageTk.PhotoImage(image=img)
            
            # Update label with new image
            camera_label1.imgtk = img_tk
            camera_label1.configure(image=img_tk)
        else:
            camera_label1.configure(text="No frame available")
    except Exception as e:
        print(f"Error updating gate camera: {e}")
        camera_label1.configure(text=f"Camera error: {str(e)}")
    
    # Schedule next update
    if camera_running:
        camera_label1.after(33, update_gate_camera)  # ~30 FPS

def update_door_camera():
    """Update door camera feed using CameraManager"""
    global door_camera, camera_running
    
    if not camera_running:
        return
    
    try:
        # Get frame from camera manager
        frame = door_camera.get_frame()
        
        if frame is not None:
            # Resize frame to fit in the UI
            frame = cv2.resize(frame, (550, 400))
            
            # Convert to RGB for tkinter display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            img = Image.fromarray(frame_rgb)
            
            # Convert to Tkinter PhotoImage
            img_tk = ImageTk.PhotoImage(image=img)
            
            # Update label with new image
            camera_label2.imgtk = img_tk
            camera_label2.configure(image=img_tk)
        else:
            camera_label2.configure(text="No frame available")
    except Exception as e:
        print(f"Error updating door camera: {e}")
        camera_label2.configure(text=f"Camera error: {str(e)}")
    
    # Schedule next update
    if camera_running:
        camera_label2.after(33, update_door_camera)  # ~30 FPS

def initialize_cameras():
    """Initialize camera managers"""
    global gate_camera, door_camera
    
    try:
        # Initialize gate camera (index 1)
        gate_camera = CameraManager.get_instance(1)
        gate_camera.acquire()
        
        # Try to initialize door camera (index 2)
        try:
            door_camera = CameraManager.get_instance(2)
            door_camera.acquire()
        except Exception as e:
            print(f"Door camera initialization failed: {e}")
            # Use same camera for both feeds if door camera fails
            door_camera = gate_camera
        
        # Start camera update loops
        update_gate_camera()
        update_door_camera()
        
        print("Cameras initialized successfully")
    except Exception as e:
        print(f"Error initializing cameras: {e}")
        open_popup(f"Camera initialization error: {str(e)}")

def release_cameras():
    """Release camera managers"""
    global gate_camera, door_camera, camera_running
    
    camera_running = False
    
    if gate_camera:
        gate_camera.release()
    
    if door_camera and door_camera != gate_camera:
        door_camera.release()
    
    print("Camera resources released")

def StartNow():
    """Starts the gui_capture_face.py script and closes the current window."""
    try:
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "gui",
            "gui_capture_face.py"
        )
        print(f"Attempting to run: {script_path}")
        subprocess.Popen([sys.executable, script_path])
        print("gui_capture_face.py started.")
    except FileNotFoundError:
        print(f"Error: Script not found at {script_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def Confirm():
    """Trains the face recognition model and adds user to the database as authorized."""
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
    except Exception as e:
        print(f"An error occurred: {e}")
        open_popup(f"An error occurred: {str(e)}")
    
def load_users():
    """Load all users from the database"""
    users_list = db_service.get_all_users()
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

def on_closing():
    """Handle window closing event"""
    global camera_running
    camera_running = False
    release_cameras()
    root.destroy()
    sys.exit(0)  # Exit with success code

# Set up UI appearance
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

# Create main window
root = customtkinter.CTk()
root.geometry("1200x700")
root.title("Security System Dashboard")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", on_closing)  # Handle window closing

# Main frames
Mainframe1 = customtkinter.CTkFrame(root, width=1200, height=600)
Mainframe1.pack(fill="both", expand=True)

frame1 = customtkinter.CTkFrame(Mainframe1, width=600, height=600)
frame1.pack(side='left', fill='both', padx=(20,10), pady=20, expand=True)

frame2 = customtkinter.CTkFrame(Mainframe1, width=600, height=600)
frame2.pack(side='right', fill='both', padx=(10,20), pady=20, expand=True)

# Tab section for cameras
tab = customtkinter.CTkTabview(frame2)
tab.pack(fill="both", expand=True)

tab1 = tab.add("Gate Camera")
tab2 = tab.add("Door Camera")

Title1 = customtkinter.CTkLabel(tab1, text='Gate Camera | LIVE', font=('', 25, 'bold'))
Title1.pack(pady=25, padx=40)

Title2 = customtkinter.CTkLabel(tab2, text='Door Camera | LIVE', font=('', 25, 'bold'))
Title2.pack(pady=25, padx=40)

# Camera frames
frame3 = customtkinter.CTkFrame(tab1, width=550, height=450)
frame3.pack(fill='both', padx=(10,10), pady=(0, 20), expand=True)

camera_label1 = customtkinter.CTkLabel(frame3, text="Initializing camera...")
camera_label1.pack(fill="both", expand=True)

frame3_1 = customtkinter.CTkFrame(tab2, width=550, height=450)
frame3_1.pack(fill='both', padx=(10,10), pady=(0, 20), expand=True)

camera_label2 = customtkinter.CTkLabel(frame3_1, text="Initializing camera...")
camera_label2.pack(fill="both", expand=True)

# Dashboard section
Dash = customtkinter.CTkLabel(frame1, text='Dashboard', font=('', 30, 'bold'))
Dash.pack(pady=25, padx=50)

frame4 = customtkinter.CTkFrame(frame1, width=600, height=300)
frame4.pack(fill="both", padx=(10,10), pady=(10,5), expand=True)

frame5 = customtkinter.CTkFrame(frame1, width=600, height=200)
frame5.pack(fill="both", padx=(10,10), pady=(5,10), expand=True)

frame5.grid_columnconfigure((0, 1, 2, 3), weight=1)

SetUp = customtkinter.CTkLabel(frame5, text='Add User', font=('', 20, 'bold'))
SetUp.grid(column=0, row=0, pady=(20, 5), padx=5)

Button_Start = customtkinter.CTkButton(frame5, text='Start Now', command=StartNow)
Button_Start.grid(column=0, row=1, pady=(5, 10), padx=5)

SetUp = customtkinter.CTkLabel(frame5, text='Confirm User', font=('', 20, 'bold'))
SetUp.grid(column=3, row=0, pady=(20, 5), padx=5)

Button_Start = customtkinter.CTkButton(frame5, text='Confirm', command=Confirm)
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
listbox_frame = Frame(user_list_frame, bg="#2b2b2b")
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
                                       fg_color="#E74C3C")
delete_button.pack(padx=10, pady=10)

refresh_button = customtkinter.CTkButton(button_frame, text="Refresh List", 
                                        command=refresh_user_list)
refresh_button.pack(padx=10, pady=10)

# Add Access Logs button
logs_button = customtkinter.CTkButton(button_frame, text="Access Logs", 
                                     command=open_logs_window)
logs_button.pack(padx=10, pady=10)

# Load users initially
refresh_user_list()

# Initialize cameras after UI setup
# initialize_cameras()

# Start the main loop
root.mainloop()