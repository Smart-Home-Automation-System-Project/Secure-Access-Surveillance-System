import cv2
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime

def create_folder(name):
    dataset_folder = "face_rec_dataset"
    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)
    
    person_folder = os.path.join(dataset_folder, name)
    if not os.path.exists(person_folder):
        os.makedirs(person_folder)
    return person_folder

def capture_photos(name):
    folder = create_folder(name)
    
    # Initialize the webcam (index 0)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Could not access the webcam.")
        return
    
    photo_count = 0
    print(f"Taking photos for {name}. Press SPACE to capture, 'q' to quit.")
    
    # Create the figure for displaying the webcam feed using Matplotlib
    fig, ax = plt.subplots()
    ax.axis('off')  # Hide axes
    
    # Create an empty image for updating in the animation
    im = ax.imshow([[0]], interpolation='nearest')

    def update_frame(frame):
        nonlocal photo_count
        
        # Capture frame from webcam
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to grab frame.")
            return frame
        
        # Convert the frame to RGB (OpenCV uses BGR by default)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Update the image in Matplotlib
        im.set_data(frame_rgb)
        
        # Return the updated frame
        return frame_rgb

    def on_key(event):
        nonlocal photo_count
        
        if event.key == ' ' and cap.isOpened():  # Space key to capture photo
            ret, frame = cap.read()
            if ret:
                photo_count += 1
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}.jpg"
                filepath = os.path.join(folder, filename)
                
                # Save the image
                cv2.imwrite(filepath, frame)
                print(f"Photo {photo_count} saved: {filepath}")
        
        elif event.key == 'q':  # 'q' key to quit
            print("Exiting...")
            cap.release()
            plt.close(fig)

    # Connect the key press event to capture photos
    fig.canvas.mpl_connect('key_press_event', on_key)

    # Animation function to update the webcam feed in real-time
    def animate(i):
        update_frame(i)
        return [im]

    # Start the animation
    ani = animation.FuncAnimation(fig, animate, interval=50, blit=True)

    # Display the window
    plt.show()

    # Clean up
    cap.release()
    print(f"Photo capture completed. {photo_count} photos saved for {name}.")

if __name__ == "__main__":
    PERSON_NAME = input("Enter the name of the person: ")
    if not PERSON_NAME.isalpha():
        print("Invalid name. Please use only alphabetic characters. Exiting.")
        exit(1)
    else:
        capture_photos(PERSON_NAME)
