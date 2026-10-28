# Smart Plant Monitoring and Automated Irrigation System

An IoT project that monitors soil moisture, air temperature and humidity, and waters a plant automatically. An Arduino Uno handles the sensors and the pump, a Python edge server logs readings to MariaDB, and a Flask dashboard shows live data and simple analytics.

Built as an individual practical assignment for an IoT programming unit at Swinburne University of Technology. The full write-up is in [`docs/report.pdf`](docs/report.pdf).

## How it works

```
Soil sensor (A0) ─┐
                  ├─> Arduino Uno ──> Relay ──> Water pump (external 5V supply)
DHT22 (D2) ───────┘      │  └───────> Status LED (D8)
                         │ USB serial (9600 baud, CSV)
                         v
              Python edge server (edgeServer.py)
                         │
                         v
              MariaDB (iot_project.sensor_data)
                         │
                         v
              Flask dashboard (app.py)
```

1. The Arduino averages 10 soil readings to smooth out noise from the external power supply, reads the DHT22, and prints `temperature,humidity,soil` over serial every ~0.5 s.
2. The Arduino switches the pump on when soil moisture is below the dry threshold **or** humidity is below 30%. It switches the pump off after 3 seconds, or earlier once the soil is wet and humidity has recovered.
3. The edge server reads each line, validates it, prints a warning above 30 °C, tracks a running average soil moisture, and stores every reading with a pump status in MariaDB.
4. The Flask app shows the latest reading, auto-refreshes every 2 seconds, and has buttons for average, minimum and maximum soil moisture.

## Hardware

| Part | Notes |
|---|---|
| Arduino Uno | Sensor hub and local pump control |
| Analog soil moisture sensor | Pin A0 |
| DHT22 temperature/humidity sensor | Pin D2 |
| 5V single-channel relay module | Pin D7 (HIGH = pump on) |
| 5V submersible mini pump | Powered from a separate 5V supply through the relay |
| Status LED + 220 Ω resistor | Pin D8 |
| Mac (edge server) | Connected to the Arduino by USB |

## Thresholds

| Setting | Value |
|---|---|
| Dry soil (pump on) | soil < 250 |
| Wet soil (pump may stop) | soil > 400 |
| Low humidity (pump on) | humidity < 30% |
| Humidity recovery for early stop | humidity > 35% |
| Max pump run time | 3 seconds |

Soil values are raw 10-bit ADC readings (0–1023). Lower means drier.

## Repository layout

```
.
├── README.md
├── arduino/
│   └── plant_monitor/
│       └── plant_monitor.ino
├── edge-server/
│   ├── edgeServer.py
│   └── schema.sql
├── dashboard/
│   ├── app.py
│   └── templates/
│       └── index.html
└── docs/
    └── report.pdf
```

## Setup

### 1. Database

```sql
CREATE DATABASE iot_project;
USE iot_project;

CREATE TABLE sensor_data (
  id INT AUTO_INCREMENT PRIMARY KEY,
  temperature FLOAT,
  humidity FLOAT,
  soil_moisture INT,
  pump_status VARCHAR(10),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Arduino

1. Install the **DHT sensor library** by Adafruit (and its Adafruit Unified Sensor dependency) from the Arduino Library Manager.
2. Open `arduino/plant_monitor/plant_monitor.ino`, select **Arduino Uno** and your port, and upload.
3. Close the Serial Monitor before starting the edge server, because only one program can use the port at a time.

### 3. Edge server and dashboard

```bash
python3 -m venv venv
source venv/bin/activate
pip install pyserial mysql-connector-python flask
```

Edit the serial port in `edge-server/edgeServer.py` to match your machine (find it with `ls /dev/tty.usb*`), and set your own database credentials in both Python files.

Run the edge server, then the dashboard in a second terminal:

```bash
python3 edge-server/edgeServer.py
python3 dashboard/app.py
```

Open http://127.0.0.1:5000 in a browser.

## Known limitations

- The Arduino sketch controls the pump on its own. The edge server also sends `PUMP_ON` / `PUMP_OFF` over serial, but the sketch does not currently read incoming serial commands, so the Python side acts as a logger and decision mirror rather than a second control layer.
- The `pump_status` stored in the database reflects the edge server's rule (soil < 250), which can differ from the Arduino's actual pump state, since the Arduino also reacts to low humidity and uses a 3-second timer.
- Database credentials in the code are placeholders for local development (`root`, empty password). Use a dedicated user and keep credentials out of version control.
- `app.py` runs with `debug=True`, which is for local use only.

## Possible improvements

- Read serial commands on the Arduino, or remove them from the edge server to keep a single source of truth.
- Move credentials and the serial port into a config file or environment variables.
- Log the Arduino's real pump state (it already prints `Pump ON` / `Pump OFF`).
- Add charts of soil moisture over time to the dashboard.
- Support multiple plants and sensors.

## Libraries

- [Adafruit DHT sensor library](https://github.com/adafruit/DHT-sensor-library)
- [pyserial](https://pyserial.readthedocs.io/)
- [mysql-connector-python](https://dev.mysql.com/doc/connector-python/en/)
- [Flask](https://flask.palletsprojects.com/)
