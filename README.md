<p align="center">
  <img src="https://justin-pauckert.com/static/img/plantmonitor-logo-flat.jpg" alt="PlantMonitor Logo" style="max-width: 50%; border-radius: 8px;" />
</p>



A Raspberry Pi-based plant monitoring system that tracks temperature, humidity, and plant images, with data hosted on AWS and displayed via a Flask web application.

## Table of Contents
1. [Description](#description)
2. [Tech Stack](#Tech-Stack)
3. [System Architecture](#System-Architecture)
4. [Repository Structure](#repository-structure)
5. [Installation](#installation)
6. [Usage](#usage)
7. [License](#license)

## Description

PlantMonitor is a project designed to monitor environmental conditions for indoor plants using a Raspberry Pi, a DHT22 sensor, and a webcam for photos. Data is processed locally and sent to AWS IoT Core, with storage in DynamoDB (sensor data) and S3 (plant images). A Flask web application hosted on an VPS displays this data. Additionally, there's a Jenkins pipeline that pushes static content to [github.com/lpodl/plantmonitor-static](https://github.com/lpodl/plantmonitor-static) to host a static version of PlantMonitor using github pages.

This repository contains the code for:
1. What happens on my RaspberryPi:
    - DHT22 sensor data collection, upload to AWS IoT
    - Taking Photos, upload to S3
2. What happens on my Hetzner Server:
    - Flask-based web application for Plantmonitor and homepage
    - Jenkins pipeline to update static website


## Tech Stack

- **Hardware**: Raspberry Pi 5, DHT22 Sensor, Webcam.
- **Cloud Services**:
  - AWS IoT Core (data ingestion).
  - Amazon DynamoDB (sensor data storage).
  - Amazon S3 (image storage).
  - Hetzner VPS (web hosting).
- **Frameworks/Libraries**: Flask, nginx, gunicorn, matplotlib, conda, Jenkins


## System Architecture

### Dynamic Website

Live Demo: 🔗 [justin-pauckert.com/plantmonitor-dynamic](https://justin-pauckert.com/plantmonitor-dynamic)
| <img src="https://justin-pauckert.com/static/img/plantmon-dynamic.png" alt="Dynamic Data Flow Diagram" width="70%"/> | <ul><li><strong>Data Collection</strong>: The Raspberry Pi collects temperature, humidity, and plant images via a sensor and webcam.</li><li><strong>Cloud Integration</strong>:<ul><li>Sensor data is sent to AWS IoT Core and forwarded to DynamoDB.</li><li>Images are uploaded to AWS S3.</li></ul></li><li><strong>Web Application</strong>:<ul><li>A Flask app hosted on VPS, fetches data from DynamoDB and S3.</li><li>The app uses Gunicorn as a WSGI server and Nginx as a reverse proxy to serve the web interface.</li></ul></li><li><strong>Client</strong>: Users access the real-time data and images through the dynamic web interface.</li></ul> |
|---|:---|



### Static Website

Live Demo: 🔗[lpodl.github.io/plantmonitor-static/](https://lpodl.github.io/plantmonitor-static/)

| <img src="https://justin-pauckert.com/static/img/plantmon-static.png" alt="Static Data Flow Diagram" width="100%"> | <div align="left"><ul><li><strong>Data Collection</strong>: The Raspberry Pi collects temperature, humidity, and plant images via a sensor and webcam.</li><li><strong>Cloud Integration</strong>:<ul><li>Sensor data is sent to AWS IoT Core and forwarded to DynamoDB.</li><li>Images are uploaded to AWS S3.</li></ul></li><li><strong>Static Site Generation on VPS</strong>:<ul><li>Jenkins pipeline runs periodically (e.g., hourly), or whenever this repo changes, to fetch the latest data from DynamoDB and S3.</li><li>The pipeline generates a static site using Frozen-Flask</li><li>Only the PlantMonitor HTML and CSS are kept and committed to the static repository.</li></ul></li><li><strong>Deployment</strong>:<ul><li>The static site is hosted on GitHub Pages. Contents are updated automatically with every commit.</li></ul></li><li><strong>Client</strong>: Users view pre-generated, static snapshots of the data.</li></ul></div> |
|--|:--|


## Repository Structure

```
📦plantmonitor
 ┣ 📂plantmon
 ┃ ┣ 📂iot              # AWS and upload files
 ┃ ┣ 📂website          # Flask app
 ┃ ┣ 📜__init__.py
 ┃ ┣ 📜sensor.py
 ┃ ┣ 📜take_photo.sh
 ┣ 📜.gitignore
 ┣ 📜Jenkinsfile
 ┣ 📜LICENSE
 ┣ 📜README.md
 ┣ 📜environment.yml
 ┗ 📜setup.py
```

## Installation

create a conda env with all dependencies
```
conda env create -f environment.yml
```
activate it
```
conda activate plantmon
```
install plantmon as package
```
cd plantmon && pip install -e . && cd ..
```
## Usage

Assuming you have your DHT22 sensor connected to your GPIO pins as described in the manual, run
```
python  ./plantmon/sensor.py
```
by default, the data will be saved as csv files every few minutes.

To take photos, edit to adjust the target directory and then run
```
./plantmon/take_photo.sh
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
