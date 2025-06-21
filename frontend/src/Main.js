import React, { useState } from "react";
import MapComponent from "./MapComponent";

export default function Component() {
  const [useCurrentLocation, setUseCurrentLocation] = useState(false);

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
            <p>Distance: 18km</p>
            <p>ETA: 3:54 PM</p>
            <p>Calories: 500 Kcal</p>
          </div>

          <div style={{ border: "1px solid orange", borderRadius: "8px", padding: "1rem" }}>
            <h3>Route</h3>
            <ul>
              <li>Times Square (10 min)</li>
              <li>Central Park (23 min)</li>
              <li>NYU</li>
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
          <MapComponent />
        </div>

        <div style={{ width: "300px", border: "1px solid #ccc", borderRadius: "8px", padding: "1rem" }}>
          <h3>Script Perimeter</h3>
          <p>Welcome to the Perimeter Institute for Theoretical Physics...</p>
        </div>
      </div>
    </div>
  );
}