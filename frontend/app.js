document.getElementById("fetchTempBtn").addEventListener("click", async () => {
  const temperatureUrl = "http://192.168.1.12:8000/temperature"; 
  console.log("Button clicked. Fetching temperature from:", temperatureUrl); // Add this log
  try {
    const response = await fetch(temperatureUrl);
    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }
    const data = await response.json();
    console.log("Fetched data:", data); // Log the data received
    document.getElementById("averageTemperature").textContent =
      `Average Temperature: ${data.average_temperature.toFixed(2)}°C`;
    document.getElementById("status").textContent = `Status: ${data.status}`;
  } catch (error) {
    console.error(error); // Log any errors
    alert("Failed to fetch temperature data. Please try again later.");
  }
});
