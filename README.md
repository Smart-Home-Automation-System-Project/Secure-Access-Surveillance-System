# Secure Access Surveillance System

A smart security system using facial recognition, running on Raspberry Pi with cloud integration and MQTT communication.

## Features

- Real-time facial recognition for authentication
- Multiple authentication methods (Face, PIN)
- Cloud storage for unauthorized access images using Cloudinary
- MQTT integration for remote monitoring and control
- SQLite database for access logs and user management
- Automated door lock/unlock mechanism
- Intruder detection and alerting system

## Prerequisites

- Raspberry Pi (3 or newer recommended)
- Webcam or camera module
- Python 3.7+
- Internet connection for cloud features
- MQTT broker (optional for remote monitoring)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Home_Security_IoT.git
cd Home_Security_IoT
```

2. Set up a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

Install dependencies in Raspberry Pi:
- Run the commands in `commands.txt` to install the required packages

### References

- https://core-electronics.com.au/guides/raspberry-pi/face-recognition-with-raspberry-pi-and-opencv/
- https://www.youtube.com/watch?v=3TUlJrRJUeM&t=432s

## Configuration

### Adding Authorized Users
1. Capture face images:
```bash
python src/image_capture.py
```

2. Train the recognition model:
```bash
python src/face_rec_model_training.py
```

### MQTT Configuration
Add `mqtt_config.json` in the `config/` directory with the following structure:
```json
{
  "broker_ip": "your_mqtt_broker_ip",
  "broker_port": 1883
}
```

### Configure Cloudinary
- Create a Cloudinary account at https://cloudinary.com/
- Add `cloudinary_config.json` in the `config/` directory with the following structure:
```json
{
  "cloud_name": "your_cloud_name",
  "api_key": "your_api_key",
  "api_secret": "your_api_secret"
}
```

## Usage

1. Start the main system:
```bash
python src/main.py
```

2. Available commands: 
- `status`: Check door lock status
- `lock`: Manually lock the door
- `pin XXXX`: Unlock using PIN
- `exit`: Stop the system

## Project Structure

```
Home_Security_IoT/
├── src/
│   ├── cloud/              # Cloud service integration
│   ├── db/                 # Database operations
│   ├── mqtt/               # MQTT communication
│   ├── face_authenticator.py
│   ├── door_lock_handler.py
│   └── main.py
├── config/                 # Configuration files
├── models/                 # Trained models
└── face_rec_dataset/      # Training images
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Adding New Features
1. Create feature branch
2. Implement changes
3. Submit pull request

## Security Considerations

- Store sensitive configuration separately
- Use secure MQTT communication (TLS)
- Regularly update authorized users list
- Monitor access logs for unauthorized attempts
- Back up the database regularly

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Submit pull request


## Acknowledgments

- Face recognition using [face_recognition](https://github.com/ageitgey/face_recognition)
- MQTT implementation with [paho-mqtt](https://github.com/eclipse/paho.mqtt.python)
- Cloud storage using [Cloudinary](https://cloudinary.com/)
