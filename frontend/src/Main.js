import React, { useState } from "react";
import MapComponent from "./MapComponent";
import routeData from './test_response.json';

export default function MainPage({currentLocation}) {
  const [useCurrentLocation, setUseCurrentLocation] = useState(false);

  // Read from JSON file - replace with actual API response
  const allRouteData = routeData;
  const routeInfo = allRouteData.route;
  const pointInfo = allRouteData.points;
  
  // Calculate ETA based on current time + duration
  const calculateETA = (durationMinutes) => {
    const now = new Date();
    const eta = new Date(now.getTime() + durationMinutes * 60000);
    return eta.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", background: "#f9fafb" }}>
      <header style={{ background: "white", borderBottom: "1px solid #ddd", padding: "1.5rem", textAlign: "center" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: "bold" }}>Name</h1>
        <p style={{ color: "#777" }}>Tagline</p>
      </header>

      <div style={{ flex: 1, display: "flex", gap: "1rem", padding: "1rem" }}>
        <div style={{ width: "250px", display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div style={{ border: "1px solid orange", borderRadius: "8px", padding: "1rem" }}>
            <h3>Trip Info</h3>
            <p>Distance: {routeInfo.total_distance_km.toFixed(1)}km</p>
            <p>ETA: {calculateETA(routeInfo.estimated_duration_minutes)}</p>
            <p>Calories: 500 Kcal</p>
          </div>

          <div style={{ border: "1px solid orange", borderRadius: "8px", padding: "1rem" }}>
            <h3>Route</h3>
            <ul>
              {pointInfo.map((point, index) => {
                // Use duration_from_prev field for timing (except first point)
                let timeDisplay = "";
                if (index > 0 && point.duration_from_prev !== null) {
                  const durationMinutes = Math.round(point.duration_from_prev);
                  timeDisplay = ` (${durationMinutes} min)`;
                }
                
                return (
                  <li key={index}>
                    {point.name}{timeDisplay}
                  </li>
                );
              })}
            </ul>
          </div>

          <div style={{ border: "1px solid #ccc", borderRadius: "8px", padding: "1rem" }}>
            <label>
              <input
                type="checkbox"
                checked={useCurrentLocation}
                onChange={(e) => setUseCurrentLocation(e.target.checked)}
              />{" "}
              Use Current Location
            </label>
          </div>
        </div>

        <div style={{ flex: 1, border: "2px solid #ccc", borderRadius: "8px", position: "relative" }}>
          <MapComponent currentLocation = {currentLocation}/>
        </div>

        <div style={{ width: "300px", border: "1px solid #ccc", borderRadius: "8px", padding: "1rem" }}>
          <h3>Script Perimeter</h3>
          <p>Welcome to the Perimeter Institute for Theoretical Physics...</p>
        </div>
      </div>
    </div>
  );
}