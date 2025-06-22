import React, { useState, useEffect } from "react";
import MapComponent from "./MapComponent";
import TextBox from "./TextBox";
import ChatWindow from "./ChatWindow";

export default function MainPage({ currentLocation }) {
  const [useCurrentLocation, setUseCurrentLocation] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [routeData, setRouteData] = useState(null);

  useEffect(() => {
    if (routeData) {
      console.log("Route data updated!", routeData);
    }
  }, [routeData]);

  const handleAIRequest = async (inputText) => {
    const updatedHistory = [...chatHistory, { role: "user", content: inputText }];
    setChatHistory(updatedHistory);

    console.log("Submitting to AI:", inputText);

    try {
      const response = await fetch("http://localhost:8000/generate-route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_text: inputText })
      });
      const data = await response.json();
      setRouteData(data);
      setChatHistory(prev => [
        ...updatedHistory,
        { role: "assistant", content: data.reply }
      ]);
    } catch (error) {
      console.error("Error calling AI:", error);
    }
  };

  const calculateETA = (durationMinutes) => {
    if (!durationMinutes || isNaN(durationMinutes)) return "N/A";
    const now = new Date();
    const eta = new Date(now.getTime() + durationMinutes * 60000);
    return eta.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
  };

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", background: "#f9fafb" }}>
      <header style={{ background: "white", borderBottom: "1px solid #ddd", padding: "0.5rem 1rem", textAlign: "center" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: "bold" }}>Name</h1>
      </header>

      <div style={{ flex: 1, display: "flex", gap: "1rem", padding: "1rem"}}>
        <div style={{ width: "250px", display: "flex", flexDirection: "column", gap: "1rem"}}>

          {/* Trip Info */}
          <div style={{ border: "1px solid orange", borderRadius: "8px", padding: "1rem", boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)'}}>
            <h3>Trip Info</h3>
            {routeData?.route ? (
              <>
                <p>Distance: {routeData.route.total_distance_km?.toFixed(1) ?? 'N/A'} km</p>
                <p>ETA: {calculateETA(routeData.route.estimated_duration_minutes)}</p>
                <p>Calories: 500 Kcal</p>
              </>
            ) : (
              <p>No route generated yet.</p>
            )}
          </div>

          {/* Route Points */}
          <div style={{ border: "1px solid orange", borderRadius: "8px", padding: "1rem", boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)' }}>
            <h3>Route</h3>
            <div style={{ position: 'relative', maxHeight: '400px', overflowY: 'auto', paddingRight: '8px' }}>
              {routeData?.points?.length > 0 ? (
                routeData.points.map((point, index) => {
                  const durationMinutes = index > 0 && point.duration_from_prev !== null
                    ? Math.round(point.duration_from_prev)
                    : null;

                  return (
                    <div key={index} style={{ position: 'relative' }}>
                      {index > 0 && (
                        <div style={{
                          position: 'absolute',
                          left: '10px',
                          top: '-20px',
                          width: '2px',
                          height: '20px',
                          background: 'linear-gradient(to bottom, #ff6b6b, #ee5a24)',
                          zIndex: 1
                        }}></div>
                      )}

                      {index > 0 && durationMinutes && (
                        <div style={{
                          position: 'absolute',
                          left: '25px',
                          top: '-15px',
                          background: 'white',
                          padding: '2px 6px',
                          borderRadius: '10px',
                          fontSize: '11px',
                          color: '#666',
                          fontWeight: 'bold',
                          border: '1px solid #ddd',
                          zIndex: 2,
                          whiteSpace: 'nowrap'
                        }}>
                          {durationMinutes} min
                        </div>
                      )}

                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        marginBottom: index < routeData.points.length - 1 ? '30px' : '0',
                        padding: '4px 0',
                        position: 'relative',
                        paddingLeft: '30px'
                      }}>
                        <div style={{
                          position: 'absolute',
                          left: 0,
                          top: '50%',
                          transform: 'translateY(-50%)',
                          width: '20px',
                          height: '20px',
                          background: 'linear-gradient(135deg, #ff6b6b, #ee5a24)',
                          borderRadius: '50% 50% 50% 0',
                          transform: 'translateY(-50%) rotate(-45deg)',
                          boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          zIndex: 3
                        }}>
                          <div style={{
                            width: '8px',
                            height: '8px',
                            background: 'white',
                            borderRadius: '50%',
                            transform: 'rotate(45deg)'
                          }}></div>
                        </div>
                        <span style={{ fontSize: '14px', color: '#333' }}>{point.name}</span>
                      </div>
                    </div>
                  );
                })
              ) : (
                <p>No route yet.</p>
              )}
            </div>
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

        {/* Map */}
        <div style={{ flex: 1, border: "2px solid #ccc", borderRadius: "8px", position: "relative" }}>
          <MapComponent 
            key={routeData?.route?.id ?? "empty"}
            pathData={routeData}
            currentLocation={currentLocation}
          />
        </div>

        {/* Chat */}
        <div style={{ width: "300px", border: "1px solid #ccc", borderRadius: "8px", padding: "1rem" }}>
          <ChatWindow chatHistory={chatHistory}/>
          <TextBox onSubmit={handleAIRequest} />
        </div>
      </div>
    </div>
  );
}
