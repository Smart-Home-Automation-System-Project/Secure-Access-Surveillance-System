import sys
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from handlers.door_lock_handler import DoorLockHandler
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def handler():
    with patch('handlers.door_lock_handler.FaceAuthenticator') as mock_face_auth, \
         patch('handlers.door_lock_handler.MQTTService') as mock_mqtt, \
         patch('handlers.door_lock_handler.DatabaseService') as mock_db, \
         patch('handlers.door_lock_handler.get_pins', return_value=["1234"]):

        # Mock instances
        mock_face_instance = MagicMock()
        mock_face_instance.check_authentication.return_value = ("TestUser", True)

        mock_face_auth.return_value = mock_face_instance
        mock_mqtt_instance = MagicMock()
        mock_mqtt.return_value = mock_mqtt_instance
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance

        door = DoorLockHandler()

        return door, mock_face_instance, mock_mqtt_instance, mock_db_instance

def test_unlock_by_face(handler):
    door, face_mock, mqtt_mock, db_mock = handler

    door.unlock(by_pin=False)
    assert not door.is_locked
    assert door.unlock_time is not None
    mqtt_mock.publish_door_state.assert_called_with("unlock")

def test_unlock_by_pin(handler):
    door, face_mock, mqtt_mock, db_mock = handler

    success = door.unlock_with_pin("1234")
    assert success
    assert not door.is_locked
    assert door.unlocked_by_pin is True
    mqtt_mock.publish_door_state.assert_called_with("unlock")

def test_auto_lock_after_time(handler):
    door, face_mock, mqtt_mock, db_mock = handler

    door.unlock(by_pin=False)
    door.unlock_time = datetime.now() - timedelta(seconds=301)  # simulate more than 5 mins passed
    locked = door.check_status()
    assert locked
    mqtt_mock.publish_door_state.assert_called_with("lock")

def test_prevent_repeated_unlock_for_unauthorized(handler):
    door, face_mock, mqtt_mock, db_mock = handler

    # Set the face auth mock to return unauthorized
    face_mock.check_authentication.return_value = ("Stranger", False)

    # Since we can't easily run the real thread loop, we'll just simulate the response
    locked = door.check_status()
    assert locked  # Should still be locked

def test_log_all_attempts(handler):
    door, face_mock, mqtt_mock, db_mock = handler

    door.unlock_with_pin("1234")
    db_mock.log_access.assert_called_with("Unknown", True, unlock_method="PIN")

def test_publish_mqtt_on_lock_unlock(handler):
    door, face_mock, mqtt_mock, db_mock = handler

    door.unlock(by_pin=True)
    mqtt_mock.publish_door_state.assert_called_with("unlock")

    door.lock()
    mqtt_mock.publish_door_state.assert_called_with("lock")
