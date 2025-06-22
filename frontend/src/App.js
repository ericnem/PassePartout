import React, { useState, useEffect } from 'react';
import MainPage from "./Main"; // Import the MainPage component

function App() {
  // State to hold the user's current location as [latitude, longitude]
  const [currentLocation, setCurrentLocation] = useState(null);

  // Runs once when the component mounts to get user's geolocation
  useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = [
            position.coords.latitude, 
            position.coords.longitude
          ];
          console.log("Got location:", coords); // Debug log
          setCurrentLocation(coords);
        },
        (error) => {
          console.error("Error retrieving location:", error);
        }
      );
    } else {
      console.warn("Geolocation not available in this browser.");
    }
  }, []);

  return ( 
    <div>
      {/* Pass currentLocation and setter to MainPage */}
      <MainPage 
        currentLocation={currentLocation} 
        setCurrentLocation={setCurrentLocation}
      />
    </div>
  );
}

export default App;
