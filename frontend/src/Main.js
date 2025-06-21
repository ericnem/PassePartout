import React, { useState } from "react";

export default function Component() {
  const [useCurrentLocation, setUseCurrentLocation] = useState(false);

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", background: "#f9fafb" }}>
      {/* Header */}
      <header style={{ background: "white", borderBottom: "1px solid #ddd", padding: "1.5rem", textAlign: "center" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: "bold" }}>Name</h1>
        <p style={{ color: "#777" }}>Tagline</p>
      </header>

      {/* Main Content */}
      <div style={{ flex: 1, display: "flex", gap: "1rem", padding: "1rem" }}>
        {/* Left Sidebar */}
        <div style={{ width: "250px", display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div style={{ border: "1px solid orange", borderRadius: "8px", padding: "1rem" }}>
            <h3>Trip Info</h3>
            <p>Distance: 21km</p>
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

        {/* Map Area */}
        <div style={{ flex: 1, border: "2px solid #ccc", borderRadius: "8px", background: "#f3f4f6", position: "relative" }}>
          <div style={{ padding: "2rem", textAlign: "center" }}>Map Placeholder</div>
        </div>

        {/* Right Sidebar */}
        <div style={{ width: "300px", border: "1px solid #ccc", borderRadius: "8px", padding: "1rem" }}>
          <h3>Script Perimeter</h3>
          <p>Welcome to the Perimeter Institute for Theoretical Physics, one of the world's leading hubs for cutting-edge research into the very fabric of reality.</p>
          <p>Beyond those trees? That’s Waterloo Park — a perfect spot for physicists to refresh after debating quantum gravity all morning.</p>
          <p>Perimeter regularly holds public lectures open to the community — a wonderful chance to engage.</p>
        </div>
      </div>

      {/* Bottom Input Area */}
      <div style={{ background: "white", borderTop: "1px solid #ddd", padding: "1rem" }}>
        <div style={{ maxWidth: "800px", margin: "0 auto", display: "flex", gap: "1rem" }}>
          <button style={{ padding: "0.5rem 1rem" }}>+</button>
          <button style={{ padding: "0.5rem 1rem" }}>⚙</button>
          <span>Tools</span>
          <input type="text" placeholder="Ask anything..." style={{ flex: 1, padding: "0.5rem" }} />
          <button style={{ padding: "0.5rem 1rem" }}>→</button>
        </div>
      </div>
    </div>
  );
}
