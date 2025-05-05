import paho.mqtt.client as mqtt
import os
import json
from dotenv import load_dotenv

class MQTTService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MQTTService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Load environment variables
        load_dotenv()

        # Create MQTT client
        self.client = mqtt.Client()

        # Get broker details from .env or use defaults
        self.broker_ip = os.getenv('MQTT_BROKER_IP', '192.168.1.100')
        self.broker_port = int(os.getenv('MQTT_BROKER_PORT', 1883))

        # Setup callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        # Connect to the MQTT broker
        self._connect_to_broker()

    def _connect_to_broker(self):
        """Establish connection with the MQTT broker."""
        try:
            self.client.connect(self.broker_ip, self.broker_port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            print(f"[MQTT] Failed to connect: {str(e)}")

    def _on_connect(self, client, userdata, flags, rc):
        """Handle successful MQTT connection."""
        if rc == 0:
            print("[MQTT] Successfully connected to broker.")
        else:
            print(f"[MQTT] Connection error with code {rc}.")

    def _on_disconnect(self, client, userdata, rc):
        """Handle MQTT disconnection."""
        print("[MQTT] Disconnected from broker.")

    def publish_door_state(self, state):
        """Publish a command to control the door."""
        try:
            payload = {
                "name": "Front Door",
                "state": state
            }
            self.client.publish("central_main/control", json.dumps(payload))
            print(f"[MQTT] Door command '{state}' sent.")
            return True
        except Exception as e:
            print(f"[MQTT] Failed to publish door command: {str(e)}")
            return False

    def disconnect(self):
        """Stop the MQTT loop and disconnect from broker."""
        self.client.loop_stop()
        self.client.disconnect()
