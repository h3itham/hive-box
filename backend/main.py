from fastapi import FastAPI, HTTPException
import requests
import os
import redis
import json
import urllib.parse
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Redis Configuration with robust parsing
def parse_redis_url(redis_url):
    # If it looks like a full URL, parse it
    if redis_url.startswith('tcp://') or redis_url.startswith('redis://'):
        parsed = urllib.parse.urlparse(redis_url)
        return {
            'host': parsed.hostname,
            'port': parsed.port or 6379
        }
    
    # If it's just a hostname or IP
    return {
        'host': redis_url,
        'port': 6379
    }

# Parse Redis connection details
redis_config = parse_redis_url(os.getenv('REDIS_HOST', 'localhost'))
REDIS_HOST = redis_config['host']
REDIS_PORT = redis_config['port']
CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 300))  # Default 5 minutes

# Create Redis client
redis_client = redis.Redis(
    host=REDIS_HOST, 
    port=REDIS_PORT, 
    decode_responses=True,
    # Optional: Add these for production
    # ssl=True,
    # ssl_cert_reqs=None
)


@app.get("/")
async def read_root():
    return FileResponse("frontend/index.html")

# READ SENSEBOX IDS FROM ENVIRONMENT VARIABLES, OR PROVIDE A DEFAULT LIST
SENSEBOX_IDS = os.getenv(
    "SENSEBOX_IDS",
    (
        "5eba5fbad46fb8001b799786,5eb99cacd46fb8001b2ce04c,"
        "5e60cf5557703e001bdae7f8"
    ),
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
    # Try to get cached data first
    cached_data = redis_client.get('temperature_data')
    if cached_data:
        return json.loads(cached_data)

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
            else:
                # IF TEMPERATURE DATA IS NOT FOUND FOR A BOX
                continue

    if not temperatures:
        raise HTTPException(status_code=404, detail="No temperature data found")

    average_temperature = sum(temperatures) / len(temperatures)

    # Determine status based on the average temperature
    if average_temperature < 10:
        status = "Too Cold"
    elif 10 <= average_temperature <= 36:
        status = "Good"
    else:
        status = "Too Hot"

    # Prepare response
    response_data = {
        "average_temperature": average_temperature,
        "status": status,
    }

    # Cache the response
    redis_client.setex(
        'temperature_data', 
        CACHE_TIMEOUT, 
        json.dumps(response_data)
    )

    return response_data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
