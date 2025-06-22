import React, { useEffect } from "react";

export default function Simulator({ currentLocation, setCurrentLocation }) {

  const move = (deltaLat, deltaLng) => {
    setCurrentLocation(([lat, lng]) => [lat + deltaLat, lng + deltaLng]);
  };

  useEffect(() => {
    const handleKeyDown = (e) => {
      switch (e.key) {
        case "ArrowUp":
          move(0.0001, 0);
          break;
        case "ArrowDown":
          move(-0.0001, 0);
          break;
        case "ArrowLeft":
          move(0, -0.0001);
          break;
        case "ArrowRight":
          move(0, 0.0001);
          break;
        default:
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [currentLocation]);

  return (
    <div style={{ textAlign: "center", margin: "2rem" }}>
      <h3>Location Simulator (Use Arrow Keys)</h3>
      <p>
        Lat: {typeof currentLocation?.[0] === 'number' 
            ? currentLocation[0].toFixed(6) 
            : 'N/A'}, 
        Lng: {typeof currentLocation?.[1] === 'number' 
            ? currentLocation[1].toFixed(6) 
            : 'N/A'}
      </p>
    </div>
  );
}
