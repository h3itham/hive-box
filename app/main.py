from fastapi import FastAPI, HTTPException
import requests
import os
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# READ SENSEBOX IDS FROM ENVIRONMENT VARIABLES, OR PROVIDE A DEFAULT LIST
SENSEBOX_IDS = os.getenv(
    "SENSEBOX_IDS",
    "5eba5fbad46fb8001b799786,5eb99cacd46fb8001b2ce04c,5e60cf5557703e001bdae7f8"
).split(",")

# INITIALIZE THE PROMETHEUS INSTRUMENTATOR
instrumentator = Instrumentator()

# ATTACH PROMETHEUS METRICS COLLECTION TO THE APP
instrumentator.instrument(app).expose(app, endpoint="/metrics")


@app.get("/version")
def read_version():
    return {"version": "v0.0.1"}


@app.get("/temperature")
def read_temperature():
    temperatures = []

    for box_id in SENSEBOX_IDS:
        response = requests.get(
            f'https://api.opensensemap.org/boxes/{box_id}?format=json'
        )
        if response.status_code != 200:
            continue

        data = response.json()

        for sensor in data['sensors']:
            if sensor['title'] == 'Temperatur' and 'lastMeasurement' in sensor:
                last_measure = sensor['lastMeasurement']
                if last_measure is not None and 'value' in last_measure:
                    temperature = float(last_measure['value'])
                    temperatures.append(temperature)
                    break
        else:
            # IF TEMPERATURE DATA IS NOT FOUND FOR A BOX
            continue

    if not temperatures:
        raise HTTPException(status_code=404, detail="No temperature data found")

    average_temperature = sum(temperatures) / len(temperatures)
    return {"average_temperature": average_temperature}


    # DETERMINE STATUS BASED ON THE AVERAGE TEMPERATURE
    if average_temperature < 10:
        status = "Too Cold"
    elif 11 <= average_temperature <= 36:
        status = "Good"
    else: 
        status = "Too Hot"

    return {
        "average_temperature": average_temperature,
        "status": status
    }

    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
