import sys
import pytest
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mqtt.mqtt_service import MQTTService

@pytest.fixture(autouse=True)
def reset_singleton():
    # Reset the singleton before each test so it gets recreated with the mock
    MQTTService._instance = None

def test_singleton_instance():
    instance1 = MQTTService()
    instance2 = MQTTService()
    assert instance1 is instance2  # Should be the same object

@patch("mqtt.mqtt_service.mqtt.Client")
def test_publish_door_state_success(mock_mqtt_client):
    mock_client_instance = MagicMock()
    mock_mqtt_client.return_value = mock_client_instance

    mqtt_service = MQTTService()
    success = mqtt_service.publish_door_state("unlock")
    assert success
    mock_client_instance.publish.assert_called_with(
        "central_main/control",
        '{"name": "Front Door", "state": "unlock"}'
    )

@patch("mqtt.mqtt_service.mqtt.Client")
def test_publish_door_state_failure(mock_mqtt_client):
    mock_client_instance = MagicMock()
    mock_client_instance.publish.side_effect = Exception("Test failure")
    mock_mqtt_client.return_value = mock_client_instance

    mqtt_service = MQTTService()
    success = mqtt_service.publish_door_state("lock")
    assert not success

@patch("mqtt.mqtt_service.mqtt.Client")
def test_connect_to_broker(mock_mqtt_client):
    mock_client_instance = MagicMock()
    mock_mqtt_client.return_value = mock_client_instance

    mqtt_service = MQTTService()
    mock_client_instance.connect.assert_called()

@patch("mqtt.mqtt_service.mqtt.Client")
def test_disconnect(mock_mqtt_client):
    mock_client_instance = MagicMock()
    mock_mqtt_client.return_value = mock_client_instance

    mqtt_service = MQTTService()
    mqtt_service.disconnect()
    mock_client_instance.loop_stop.assert_called()
    mock_client_instance.disconnect.assert_called()
