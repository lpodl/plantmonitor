"""
read temperature and humidity from DHT22 sensor
publish to AWS IoT
"""
from iot_connection import connect_mqtt, publish_sensor_data
import emoji

from plantmon.sensor import read_sensor
INTERVAL_LENGTH = 2 * 60  # reading interval (s)


mqtt_connection = connect_mqtt()
while True:
    try:
        temperature, humidity, timestamp = read_sensor(INTERVAL_LENGTH)
        publish_sensor_data(mqtt_connection, timestamp, humidity, temperature)
        print(
            emoji.emojize(
                f" :incoming_envelope: msg sent [{timestamp}] | Temperature (°C) {temperature:.2f} | Humidity (%) {humidity:.2f}"  # noqa: E501
            )
        )
    except KeyboardInterrupt:
        print("Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")
        raise KeyboardInterrupt
