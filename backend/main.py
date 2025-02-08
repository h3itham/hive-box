from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

# Hardcoded sensebox IDs
SENSEBOX_IDS = [
    "5eba5fbad46fb8001b799786",
    "5eb99cacd46fb8001b2ce04c",
    "5e60cf5557703e001bdae7f8"
]

@app.get("/version")
def read_version():
    return {"version": "v0.0.1"}

@app.get("/temperature")
def read_temperature():
    temperatures = []
    for box_id in SENSEBOX_IDS:
        response = requests.get(
            f"https://api.opensensemap.org/boxes/{box_id}?format=json"
        )
        if response.status_code != 200:
            continue
        
        data = response.json()
        for sensor in data["sensors"]:
            if (
                sensor["title"] == "Temperatur"
                and "lastMeasurement" in sensor
            ):
                last_measure = sensor["lastMeasurement"]
                if last_measure is not None and "value" in last_measure:
                    temperature = float(last_measure["value"])
                    temperatures.append(temperature)
                    break

    if not temperatures:
        raise HTTPException(status_code=404, detail="No temperature data found")

    average_temperature = sum(temperatures) / len(temperatures)

    return {
        "average_temperature": average_temperature
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)