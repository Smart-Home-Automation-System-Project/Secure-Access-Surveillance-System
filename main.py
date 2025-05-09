import sys
import time
import subprocess
from handlers.door_lock_handler import DoorLockHandler
from camera.video_stream import start_stream_thread, stop_stream
from db.firebase_service import FirebaseService
import tkinter as tk

# Global variables to track services
door_lock_handler = None
firebase = None
video_stream_thread = None
services_running = False

def start_services():
    """Start all background security services"""
    global door_lock_handler, firebase, video_stream_thread, services_running
    
    if services_running:
        print("Services already running")
        return
    
    print("Starting security services...")
    
    # Initialize Firebase service
    firebase = FirebaseService()

    # Initialize door lock handler
    door_lock_handler = DoorLockHandler()
    
    # Start the video stream in a thread
    video_stream_thread = start_stream_thread()
    
    # Start the door lock handler
    door_lock_handler.start()
    
    services_running = True

def stop_services():
    """Stop all running services"""
    global door_lock_handler, firebase, services_running
    
    if not services_running:
        return
    
    print("Stopping security services...")
    
    # Stop door lock handler
    if door_lock_handler:
        door_lock_handler.stop()
    
    # Stop video stream
    stop_stream()
    
    # Clean up Firebase
    if firebase:
        firebase.cleanup()
    
    services_running = False

def start_ui():
    """Launch the UI - first login, then homepage if login succeeds"""
    print("Starting User interface...")
    try:
        # Start the login UI and wait for it to finish
        login_process = subprocess.Popen([sys.executable, "gui/login.py"])
        login_process.wait()
        
        # If login was successful (returned 0), start homepage
        if login_process.returncode == 0:
            
            # Start homepage and wait for it to finish
            homepage_process = subprocess.Popen([sys.executable, "gui/homepage.py"])
            homepage_process.wait()
            
            # Process homepage exit code
            if homepage_process.returncode == 0:
                print("User interface closed successfully")
            else:
                print(f"User interface closed with exit code {homepage_process.returncode}")
        else:
            print(f"Login failed with exit code {login_process.returncode}")
            
        return True
    except Exception as e:
        print(f"Error in UI flow: {e}")
        return False
    
def main():
    """Main entry point for the application"""
    print("Secure Access Surveillance System starting...")
    
    try:
        while True:
            # Ask the user what to start
            print("\nSelect an option:")
            print("1. Open User Interface")
            print("2. Start Security Services")
            print("3. Exit")
            choice = input("Enter your choice (1/2/3): ").strip()
            
            if choice == "1":
                # Start the login UI
                if start_ui():
                    print("Login completed.")
            elif choice == "2":
                # Start security services
                print("Starting security services...")
                start_services()
                
                # Keep the main thread running to maintain background services
                try:
                    while services_running:
                        break
                except KeyboardInterrupt:
                    stop_services()
                finally:
                    stop_services()
                    print("Security services stopped")
            elif choice == "3":
                print("Exiting the application...")
                break
            else:
                print("Invalid choice. Please try again.")
    except KeyboardInterrupt:
        print("\nShutting down by user request...")
    finally:
        # Make sure to clean up all services
        stop_services()
        print("System shutdown complete")

if __name__ == "__main__":
    main()