import time

import mysql.connector
import serial

# Serial setup
ser = serial.Serial("/dev/tty.usbserial-A5069RR4", 9600)
time.sleep(2)

# Database setup
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="iot_project",
)

cursor = db.cursor()

# Variables for analytics
total_soil = 0
count = 0

# Main loop
while True:
    try:
        ser.reset_input_buffer()
        line = ser.readline().decode().strip()

        if not line:
            continue

        print("Received:", line)

        if line.count(",") != 2:
            print("Skipping:", line)
            continue

        temp, hum, soil = line.split(",")

        temp = float(temp)
        hum = float(hum)
        soil = int(soil)

        print(f"Temp: {temp}°C | Humidity: {hum}% | Soil: {soil}")

        if temp > 30:
            print("Warning: High Temperature Detected")

        total_soil += soil
        count += 1
        avg_soil = total_soil / count
        print(f"Avg Soil Moisture: {avg_soil:.1f}")

        if soil < 250:
            pump_status = "ON"
            ser.write(b"PUMP_ON\n")
        else:
            pump_status = "OFF"
            ser.write(b"PUMP_OFF\n")

        print(f"Pump: {pump_status}")

        sql = """
            INSERT INTO sensor_data (
                temperature,
                humidity,
                soil_moisture,
                pump_status
            )
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (temp, hum, soil, pump_status))
        db.commit()

        print("Saved to DB\n")
        time.sleep(2)

    except ValueError as e:
        print(f"Parse error on line '{line}': {e}")
    except mysql.connector.Error as e:
        print(f"DB error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")