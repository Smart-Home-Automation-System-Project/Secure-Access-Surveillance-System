from flask import Flask, Response
import cv2
import json

app = Flask(__name__)

# Global variables
camera = None
stream_active = False

def init_camera():
    """Initialize the camera"""
    global camera
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return camera.isOpened()

def get_camera_feed():
    """Generator function for camera frames"""
    global camera, stream_active
    
    while stream_active:
        if camera and camera.isOpened():
            success, frame = camera.read()
            if success:
                # Encode the frame
                _, jpeg = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

@app.route('/door_lock/video_feed')
def video_feed():
    """Route for streaming video"""
    return Response(get_camera_feed(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def start_stream(host='0.0.0.0', port=5000):
    """Start the video stream server"""
    global stream_active
    
    if not init_camera():
        print("[ERROR] Could not initialize camera")
        return
    
    stream_active = True
    
    # Load config if exists
    try:
        with open("config/stream_config.json", "r") as f:
            config = json.load(f)
            port = config.get('port', port)
            host = config.get('host', host)
    except:
        print("[STREAM] Configuration file not found, using defaults")
    
    print(f"[STREAM] Starting video stream server at http://{host}:{port}")
    app.run(host=host, port=port, threaded=True)

def stop_stream():
    """Stop the video stream"""
    global stream_active, camera
    stream_active = False
    if camera:
        camera.release()
    print("[STREAM] Video stream stopped")

