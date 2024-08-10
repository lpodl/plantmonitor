# Plantmonitoring
Photos, temperature and humidity monitored as Flask app hosted on AWS. 
Data is sent through AWS IoT Core and then saved in DynamoDB.

# Prerequisites
* RaspberryPi 5
* DHT22 Sensor
* (Your own AWS Setup if you also want to run this on AWS) 

# Setup
create conda env with all dependencies
```
conda env create -f environment.yml
```
activate it
```
conda activate plantmon
```
install plantmon as package
```
cd plantmon && pip install -e .
```

To check if your sensor is picking up data, run
```
python  sensor.py
```

