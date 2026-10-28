from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="iot_project",
    )


@app.route("/")
def index():
    db = get_db_connection()
    cursor = db.cursor()

    # Latest sensor data
    cursor.execute(
        """
        SELECT temperature, humidity, soil_moisture, pump_status
        FROM sensor_data
        ORDER BY id DESC
        LIMIT 1
        """
    )
    latest = cursor.fetchone()

    result = ""
    analysis = request.args.get("analysis")

    # Soil moisture analytics
    if analysis == "avg":
        cursor.execute(
            """
            SELECT AVG(soil_moisture)
            FROM sensor_data
            """
        )
        avg = cursor.fetchone()[0]
        result = f"Average Soil Moisture: {avg}"

    elif analysis == "min":
        cursor.execute(
            """
            SELECT MIN(soil_moisture)
            FROM sensor_data
            """
        )
        minimum = cursor.fetchone()[0]
        result = f"Minimum Soil Moisture: {minimum}"

    elif analysis == "max":
        cursor.execute(
            """
            SELECT MAX(soil_moisture)
            FROM sensor_data
            """
        )
        maximum = cursor.fetchone()[0]
        result = f"Maximum Soil Moisture: {maximum}"

    db.close()

    return render_template(
        "index.html",
        data=latest,
        result=result,
    )


if __name__ == "__main__":
    app.run(debug=True)

