from awscrt import mqtt
from awsiot import mqtt_connection_builder
import json
from datetime import datetime

# Hardcoded configuration variables
endpoint = "a1rqeucab7scyn-ats.iot.eu-central-1.amazonaws.com"
ca_file = "root-CA.crt"
cert_file = "/home/justin/.ssh/RaspberryPi5.cert.pem"
key_file = "/home/justin/.ssh/RaspberryPi5.private.key"
client_id = "basicPubSub"
topic = "plantmonitor/data/sensor"


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


def publish_sensor_data(mqtt_connection, timestamp, humidity, temperature):
    msg = {"timestamp": timestamp, "humidity": humidity, "temperature": temperature}
    message_json = json.dumps(msg)
    mqtt_connection.publish(
        topic=topic, payload=message_json, qos=mqtt.QoS.AT_LEAST_ONCE
    )
    print("Published message to topic '{}': {}".format(topic, message_json))


def connect_mqtt():
    # Create a MQTT connection
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=endpoint,
        cert_filepath=cert_file,
        pri_key_filepath=key_file,
        ca_filepath=ca_file,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=client_id,
        clean_session=True,
        keep_alive_secs=30,
    )

    print(f"Connecting to {endpoint} with client ID '{client_id}'...")
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
