from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

@app.get("/version")
def read_version():
    return {"version": "v0.0.1"}

@app.get("/temperature")
def read_temperature():
    box_ids = [
        "5eba5fbad46fb8001b799786",
        "5e02b67d475fc6001a132e31",
        "5eba5fbad46fb8001b799786"
    ]
    temperatures = []

    for box_id in box_ids:
        response = requests.get(f'https://api.opensensemap.org/boxes/{box_id}?format=json')
        data = response.json()

        for sensor in data['sensors']:
            if sensor['title'] == 'Temperatur' and 'lastMeasurement' in sensor:
                last_measurement = sensor['lastMeasurement']
                if last_measurement is not None and 'value' in last_measurement:
                    temperature = float(last_measurement['value'])
                    temperatures.append(temperature)
                    break
        else:
            # If temperature data is not found for a box, continue to the next box
            continue
    
    if not temperatures:
        raise HTTPException(status_code=404, detail="Temperature data not found")

    average_temperature = sum(temperatures) / len(temperatures)
    return {"average_temperature": average_temperature}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
