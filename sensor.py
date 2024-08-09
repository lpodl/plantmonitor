"""
read temperature and humidity from DHT22 sensor
save data as df in pre-defined intervals
"""

import time
import RPi.GPIO as GPIO
import pandas as pd
from datetime import datetime
import numpy as np
from halo import Halo
import emoji


class DHT22:
    def __init__(self, pin=12):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)

    def read(self):
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(self.pin, GPIO.LOW)
        time.sleep(0.02)
        GPIO.setup(self.pin, GPIO.IN, GPIO.PUD_UP)

        data = []
        count = 0
        while GPIO.input(self.pin) == GPIO.LOW:
            count += 1
            if count > 100:
                raise ValueError("Timeout waiting for low pulse")
        count = 0
        while GPIO.input(self.pin) == GPIO.HIGH:
            count += 1
            if count > 100:
                raise ValueError("Timeout waiting for high pulse")

        for _ in range(40):
            count = 0
            while GPIO.input(self.pin) == GPIO.LOW:
                count += 1
                if count > 100:
                    raise ValueError("Timeout waiting for low pulse")
            count = 0
            t0 = time.time()
            while GPIO.input(self.pin) == GPIO.HIGH:
                count += 1
                if count > 100:
                    raise ValueError("Timeout waiting for high pulse")
            t1 = time.time()
            data.append(t1 - t0 > 0.00005)

        binary_string = "".join("1" if bit else "0" for bit in data)
        bytes_data = [
            int(binary_string[i : i + 8], 2) for i in range(0, len(binary_string), 8)
        ]

        if len(bytes_data) != 5:
            raise ValueError(
                f"Data length error. Got {len(bytes_data)} bytes instead of 5."
            )

        humidity = (bytes_data[0] * 256 + bytes_data[1]) / 10
        temperature = (bytes_data[2] * 256 + bytes_data[3]) / 10

        return round(temperature, 2), round(humidity, 2)


def read_sensor(sensor):
    temperature = None
    humidity = None
    for attempt in range(MAX_RETRIES):
        try:
            temperature, humidity = sensor.read()
            break
        except Exception as e:
            if attempt > 5:
                print(f"Error reading sensor (attempt {attempt + 1}): {str(e)}")
            time.sleep(1)
    if not temperature:
        raise Warning("Reading from sensor did not succeed")
    return temperature, humidity


def remove_outliers(data, m=1.5):
    # IQR method used for boxplots
    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1
    lower_bound = q1 - (m * iqr)
    upper_bound = q3 + (m * iqr)
    return [x for x in data if lower_bound <= x <= upper_bound]


MAX_RETRIES = 10
READING_DELAY = 1  # sensor pulling rate
INTERVAL_LENGTH = 2 * 60  # reading interval (s) over which we sum
TIMEFRAME = 1 * 60 * 60  # ~ batch length (s) for one dataframe

data = []
temperature_readings = []
humidity_readings = []

while True:
    for i in range(TIMEFRAME // INTERVAL_LENGTH):
        dht22 = DHT22()
        start_time = time.time()
        now = time.time()
        spinner = Halo(text="Loading", spinner="clock")
        while now - start_time < INTERVAL_LENGTH:
            spinner.start()
            temperature, humidity = read_sensor(dht22)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            spinner.text = emoji.emojize(
                f"[{timestamp}] reading :thermometer: {temperature}°C :sweat_droplets: {humidity}%"
            )
            if temperature is not None and humidity is not None:
                temperature_readings.append(temperature)
                humidity_readings.append(humidity)
            time.sleep(READING_DELAY)
            now = time.time()
        spinner.stop()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        assert len(temperature_readings) > 0
        assert len(temperature_readings) == len(humidity_readings)
        # clean data and calculate avg
        cleaned_temperature = remove_outliers(temperature_readings)
        cleaned_humidity = remove_outliers(humidity_readings)
        avg_temperature = round(sum(cleaned_temperature) / len(cleaned_temperature), 2)
        avg_humidity = round(sum(cleaned_humidity) / len(cleaned_humidity), 2)
        print(
            emoji.emojize(
                f" :clipboard: [{timestamp}] {len(temperature_readings)} readings | Avg Temperature (°C) {avg_temperature:.2f} | Avg Humidity (%) {avg_humidity:.2f}"
            )
        )
        data.append(
            {
                "Timestamp": timestamp,
                "Temperature (°C)": avg_temperature,
                "Humidity (%)": avg_humidity,
            }
        )

        start_time = time.time()
        temperature_readings.clear()
        humidity_readings.clear()

    df = pd.DataFrame(data)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    filename = f"./sensor_data/{timestamp}.csv"
    df.to_csv(
        filename, index=False
    )
    print(
        emoji.emojize(
            f" :file_folder: [{timestamp}] saved dataframe under {filename}"
        )
    )
    data.clear()
    GPIO.cleanup()
