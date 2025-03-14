from awscrt import mqtt
from awsiot import mqtt_connection_builder
import json
from datetime import datetime
from plantmon.config import config

# configuration variables
ENDPOINT = config["AWS_IOT_ENDPOINT"]
CA_FILE = config["AWS_IOT_CA_FILE"]
CERT_FILE = config["AWS_IOT_CERT_FILE"]
KEY_FILE = config["AWS_IOT_KEY_FILE"]
CLIENT_ID = config["AWS_IOT_CLIENT_ID"]
TOPIC = config["AWS_IOT_TOPIC"]


# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(
        "Connection resumed. return_code: {} session_present: {}".format(
            return_code, session_present
        )
    )


def publish_sensor_data(mqtt_connection, msg_id, timestamp, humidity, temperature):
    msg = {
        "msg_id": msg_id,
        "msg_time": timestamp,
        "humidity": humidity,
        "temperature": temperature,
    }
    message_json = json.dumps(msg)
    mqtt_connection.publish(
        topic=TOPIC, payload=message_json, qos=mqtt.QoS.AT_LEAST_ONCE
    )


def connect_mqtt():
    # Create a MQTT connection
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=CERT_FILE,
        pri_key_filepath=KEY_FILE,
        ca_filepath=CA_FILE,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=CLIENT_ID,
        clean_session=True,
        keep_alive_secs=30,
    )

    print(f"Connecting to {ENDPOINT} with client ID '{CLIENT_ID}'...")
    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    return mqtt_connection


if __name__ == "__main__":
    mqtt_connection = connect_mqtt()

    # Publish sample data
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    humidity = 50.0
    temperature = 25.0
    publish_sensor_data(mqtt_connection, timestamp, humidity, temperature)

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")
