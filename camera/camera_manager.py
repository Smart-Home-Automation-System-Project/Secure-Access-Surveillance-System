import cv2
import threading
import time

class CameraManager:
    _instances = {}
    _locks = {}

    @classmethod
    def get_instance(cls, camera_index=0):
        """ Get a singleton instance of the camera manager for the specified camera index."""
        if camera_index not in cls._locks:
            cls._locks[camera_index] = threading.Lock()
            
        with cls._locks[camera_index]:
            if camera_index not in cls._instances or cls._instances[camera_index] is None:
                cls._instances[camera_index] = cls(camera_index)
            return cls._instances[camera_index]

    def __init__(self, camera_index=0):
        """Initialize the camera manager with the specified camera index."""
        # Camera properties
        self.camera_index = camera_index
        self.width = 640
        self.height = 480
        self.fps = 30
        
        # Initialize camera
        self.camera = None
        self.frame = None
        self.last_frame_time = 0
        self.is_running = False
        self.thread = None
        self.lock = threading.Lock()
        
        # Reference counter for tracking how many components are using this camera
        self.ref_count = 0
        
        # Initialize camera
        self.initialize()
        
    def initialize(self):
        """Initialize the camera and start the capture thread."""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Check if camera opened successfully
            if not self.camera.isOpened():
                print(f"[CAMERA] Failed to open camera with index {self.camera_index}")
                return False
            
            # Start camera thread
            self.is_running = True
            self.thread = threading.Thread(target=self._update_frame)
            self.thread.daemon = True
            self.thread.start()
            
            print(f"[CAMERA] Camera {self.camera_index} initialized successfully")
            return True
        except Exception as e:
            print(f"[CAMERA] Error initializing camera {self.camera_index}: {str(e)}")
            return False
    
    def _update_frame(self):
        """Continuously update the frame in a background thread."""
        while self.is_running:
            if self.camera and self.camera.isOpened():
                ret, frame = self.camera.read()
                if ret:
                    with self.lock:
                        self.frame = frame
                        self.last_frame_time = time.time()
                else:
                    time.sleep(0.01)  # Small delay if frame capture failed
            else:
                time.sleep(0.1)  # Larger delay if camera not available
    
    def get_frame(self):
        """Get the current frame from the camera."""
        with self.lock:
            if self.frame is not None:
                return self.frame.copy()
            return None
    
    def acquire(self):
        """Register a component using this camera."""
        with self.lock:
            self.ref_count += 1
            return self.ref_count
    
    def release(self):
        """Unregister a component using this camera."""
        with self.lock:
            if self.ref_count > 0:
                self.ref_count -= 1
            
            # If no more references, release resources
            if self.ref_count == 0:
                self._release_resources()
            
            return self.ref_count
    
    def _release_resources(self):
        """Release camera resources."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        
        if self.camera:
            self.camera.release()
            self.camera = None
            
        print(f"[CAMERA] Camera {self.camera_index} resources released")
    
    def is_frame_available(self):
        """Check if the latest frame is available."""
        with self.lock:
            frame_age = time.time() - self.last_frame_time
            return self.frame is not None and frame_age < 1.0  # Frame less than 1 second old
    
    def __del__(self):
        """Destructor to ensure resources are properly released."""
        self._release_resources()