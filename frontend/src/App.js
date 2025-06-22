import React, { useState, useEffect } from 'react';
import MainPage from "./Main"; // adjust the path if needed

function App() {
  const [currentLocation, setCurrentLocation] = useState(null);

  useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition((position) => {
        const coords = [position.coords.latitude, position.coords.longitude];
        console.log("Got location:", coords);  // <-- debug print here
        setCurrentLocation([position.coords.latitude, position.coords.longitude]);
      });
    }
  }, []);

  return ( 
    <div>
      <MainPage currentLocation={currentLocation}/>
    </div>
  );
}

export default App;