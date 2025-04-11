import paho.mqtt.client as mqtt
import json
import base64
import cv2
from datetime import datetime
import threading

class MQTTService:
    def __init__(self):
        # MQTT client setup
        self.client = mqtt.Client()
        self.broker_ip = "192.168.1.100"
        self.broker_port = 1883
        
        # Topics
        self.topics = {
            "alert": "home/security/door/alert",
            "status": "home/security/door/status",
            "command": "home/security/door/command"
        }
        
        # Command callback
        self.command_callback = None
        
        # Setup MQTT callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        # Connection management
        self._connect()
        
    def _connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(self.broker_ip, self.broker_port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"[MQTT] Connection failed: {str(e)}")

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected"""
        if rc == 0:
            print("[MQTT] Connected to broker")
            self.client.subscribe(self.topics["command"])
        else:
            print(f"[MQTT] Connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected"""
        print("[MQTT] Disconnected from broker")
        if rc != 0:
            print("[MQTT] Unexpected disconnection. Attempting to reconnect...")
            threading.Timer(5.0, self._connect).start()

    def _on_message(self, client, userdata, msg):
        """Handle incoming messages"""
        try:
            payload = json.loads(msg.payload.decode())
            if msg.topic == self.topics["command"] and self.command_callback:
                self.command_callback(payload)
        except Exception as e:
            print(f"[MQTT] Message processing error: {str(e)}")

    def set_command_callback(self, callback):
        """Set callback for incoming commands"""
        self.command_callback = callback

    def send_alert(self, name, frame, alert_type="unauthorized_access"):
        """Send unauthorized access alert with image"""
        try:
            # Compress and encode frame
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
            _, img_encoded = cv2.imencode('.jpg', frame, encode_param)
            img_base64 = base64.b64encode(img_encoded.tobytes()).decode('utf-8')

            # Create alert payload
            payload = {
                "type": alert_type,
                "timestamp": datetime.now().isoformat(),
                "person_name": name,
                "image": img_base64
            }

            # Publish alert
            self.client.publish(self.topics["alert"], json.dumps(payload))
            print(f"[MQTT] Alert sent: {alert_type} for {name}")
            print(f"[MQTT] payload: {payload}")
            return True
        except Exception as e:
            print(f"[MQTT] Failed to send alert: {str(e)}")
            return False
        
    def update_log (self, name, unlock_method=None):
        """Update log with unlock method"""
        try:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "person_name": name,
                "unlock_method": unlock_method
            }
            self.client.publish(self.topics["status"], json.dumps(payload))
            return True
        except Exception as e:
            print(f"[MQTT] Failed to update log: {str(e)}")
            return False

    def send_status(self, is_locked, unlock_method=None):
        """Send door status update"""
        try:
            payload = {
                "status": "locked" if is_locked else "unlocked",
                "timestamp": datetime.now().isoformat()
            }
            if not is_locked and unlock_method:
                payload["unlock_method"] = unlock_method

            self.client.publish(self.topics["status"], json.dumps(payload))
            return True
        except Exception as e:
            print(f"[MQTT] Failed to send status: {str(e)}")
            return False

    def cleanup(self):
        """Clean up MQTT client"""
        self.client.loop_stop()
        self.client.disconnect()
