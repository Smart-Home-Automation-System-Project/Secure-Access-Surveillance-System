import paho.mqtt.client as mqtt
import json
from datetime import datetime
import threading

class MQTTService:
    def __init__(self):
        # MQTT client setup
        self.client = mqtt.Client()
        
        # Load config
        try:
            with open("config/mqtt_config.json", "r") as f:
                config = json.load(f)
                self.broker_ip = config['broker_ip']
                self.broker_port = config['broker_port']
        except:
            print("[MQTT] Configuration file not found.")
        
        # Topics
        self.topics = {
            "unauthorized": "home/security/unauthorized",
            "door": "home/security/door/command",
        }
        
        # Setup MQTT callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        
        # Connect to broker
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
        else:
            print(f"[MQTT] Connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected"""
        if rc != 0:
            print("[MQTT] Unexpected disconnection. Attempting to reconnect...")
            threading.Timer(5.0, self._connect).start()

    def send_unauthorized_alert(self, name):
        """Send unauthorized access alert with image"""
        try:
            payload = {
                "name": name,
                "timestamp": datetime.now().isoformat()
            }
            self.client.publish(self.topics["unauthorized"], json.dumps(payload))
            print(f"[MQTT] Unauthorized access alert sent for: {name}")
            return True
        except Exception as e:
            print(f"[MQTT] Failed to send alert: {str(e)}")
            return False

    def send_door_command(self, command):
        """Send command to lock or unlock the door"""
        try:
            payload = {
                "command": command,
                "timestamp": datetime.now().isoformat()
            }
            self.client.publish(self.topics["door"], json.dumps(payload))
            print(f"[MQTT] Door command '{command}' sent successfully.")
            return True
        except Exception as e:
            print(f"[MQTT] Failed to send command: {str(e)}")
            return False

    def cleanup(self):
        """Clean up MQTT client"""
        self.client.loop_stop()
        self.client.disconnect()