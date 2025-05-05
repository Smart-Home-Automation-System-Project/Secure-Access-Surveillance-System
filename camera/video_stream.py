from flask import Flask, Response
import cv2
import os
from camera.camera_manager import CameraManager
from dotenv import load_dotenv
import threading

app = Flask(__name__)

# Global variables
camera_manager = None
stream_active = False

def init_camera(camera_index=0):
    """Initialize the camera"""
    global camera_manager
    camera_manager = CameraManager.get_instance(camera_index)
    camera_manager.acquire()  # Register this component
    return camera_manager.is_frame_available()

def get_camera_feed():
    """Generator function for camera frames"""
    global camera_manager, stream_active
    
    while stream_active:
        frame = camera_manager.get_frame()
        if frame is not None:
            # Encode the frame
            _, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        else:
            # Brief pause if no frame is available
            import time
            time.sleep(0.05)

@app.route('/video_feed')
def video_feed():
    """Route for streaming video"""
    return Response(get_camera_feed(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def start_stream(host='0.0.0.0', port=5000):
    """Start the video stream server"""
    global stream_active

    # Load environment variables
    load_dotenv()
    
    if not init_camera():
        print("[ERROR] Could not initialize camera")
        return
    
    stream_active = True
    
    # Load config from environment variables
    port = int(os.getenv('STREAM_PORT', 5000))
    host = os.getenv('STREAM_HOST', '0.0.0.0')
    
    print(f"[STREAM] Starting video stream server at http://{host}:{port}")
    app.run(host=host, port=port, threaded=True)

def stop_stream():
    """Stop the video stream"""
    global stream_active, camera_manager
    stream_active = False
    if camera_manager:
        camera_manager.release()  # Unregister this component
    print("[STREAM] Video stream stopped")

def start_stream_thread():
    """Thread to run the video stream server"""
    thread = threading.Thread(target=start_stream)
    thread.daemon = True  # Daemonize thread
    thread.start()
    return thread