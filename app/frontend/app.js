document.getElementById("fetchTempBtn").addEventListener("click", async () => {
    const temperatureUrl = "http://192.168.1.12:8000/temperature"; 
    try {
      const response = await fetch(temperatureUrl);
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const data = await response.json();
      document.getElementById("averageTemperature").textContent =
        `Average Temperature: ${data.average_temperature.toFixed(2)}°C`;
      document.getElementById("status").textContent = `Status: ${data.status}`;
    } catch (error) {
      console.error(error);
      alert("Failed to fetch temperature data. Please try again later.");
    }
  });
  