# File: main.py
from fastapi import FastAPI, HTTPException
import requests
import os
import redis
import json
import urllib.parse
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from minio import Minio
from minio.error import S3Error
import datetime
import io

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REDIS CONFIGURATION WITH ROBUST PARSING
def parse_redis_url(redis_url):
    # IF IT LOOKS LIKE A FULL URL, PARSE IT
    if redis_url.startswith('tcp://') or redis_url.startswith('redis://'):
        parsed = urllib.parse.urlparse(redis_url)
        return {
            'host': parsed.hostname,
            'port': parsed.port or 6379
        }
    
    # IF IT'S JUST A HOSTNAME OR IP
    return {
        'host': redis_url,
        'port': 6379
    }

# PARSE REDIS CONNECTION DETAILS
redis_config = parse_redis_url(os.getenv('REDIS_HOST', 'localhost'))
REDIS_HOST = redis_config['host']
REDIS_PORT = redis_config['port']
CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 300))  # Default 5 minutes

# CREATE REDIS CLIENT
redis_client = redis.Redis(
    host=REDIS_HOST, 
    port=REDIS_PORT, 
    decode_responses=True,
)

# MinIO Configuration from Environment Variables
MINIO_URL = os.getenv('MINIO_URL', 'http://localhost:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', 'hive-box')
MINIO_SECURE = os.getenv('MINIO_SECURE', 'false').lower() == 'true'

# Initialize MinIO client
minio_client = Minio(
    MINIO_URL.replace('http://', '').replace('https://', ''),
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE,
)

# Check if the bucket exists, create if not
if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
    minio_client.make_bucket(MINIO_BUCKET_NAME)

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

@app.get("/store")
async def store_temperature_data():
    try:
        # First, get the temperature data
        temperature_data = read_temperature()
        
        # Generate a unique filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"temperature_{timestamp}.json"
        
        # Convert the data to a JSON-formatted bytes object
        data_bytes = json.dumps(temperature_data).encode('utf-8')
        data_stream = io.BytesIO(data_bytes)
        
        # Store the file in MinIO
        minio_client.put_object(
            bucket_name=MINIO_BUCKET_NAME,
            object_name=filename,
            data=data_stream,
            length=len(data_bytes),
            content_type='application/json'
        )
        
        return {
            "message": "Temperature data stored successfully",
            "filename": filename,
            "data": temperature_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing temperature data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)