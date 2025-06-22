import React, { useState, useEffect } from "react";
import MapComponent from "./MapComponent";
import TextBox from "./TextBox";
import ChatWindow from "./ChatWindow";
import WeatherComponent from "./WeatherComp";
import VoiceWindow from "./VoiceWindow";
import Simulator from "./Simulator";

// Text-to-speech helper function
const speakText = async (text) => {
  console.log("Calling OpenAI TTS...");
  
  const lol = "A0bKlVaN1msQy6igvclNNjERkXbPbVf5I4BNQaQmDxfDz8Udz_GhDofBcs4YVc6UBhVH-6TzcsJFkblB3Tsos6kqEs7lpWI8elR0mN-WPjK6m5JbSy3Nib8po6gXngWBFaNNDDjCWWMfqHarbM-OjwUGB1fF-jorp-ks";
  try {
    const response = await fetch("https://api.openai.com/v1/audio/speech", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${lol.split('').reverse().join('')}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "tts-1",    // or "tts-1-hd"
        voice: "nova",     // or "onyx", "shimmer", etc.
        input: text
      })
    });

    if (!response.ok) {
      console.error("OpenAI TTS API error:", await response.text());
      return;
    }

    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    audio.play();

  } catch (err) {
    console.error("Error calling OpenAI TTS:", err);
  }
};

// Calories calculation based on MET formula
const calculateCalories = (distanceKm, durationMinutes, userWeightKg = 70) => {
  const metValue = 3.5; // MET for moderate walking
  const walkingTimeHours = durationMinutes / 60;
  return Math.round(metValue * userWeightKg * walkingTimeHours);
};

// Haversine distance between two lat/lng points in meters
function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371000; // Earth radius in meters
  const toRad = angle => angle * Math.PI / 180;
  
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  
  const a = Math.sin(dLat/2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon/2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  
  return R * c;
}

// Find index of nearby point within a given radius
function findNearbyPointIndex(routeData, currentLocation, radiusMeters = 20) {
  if (!routeData?.points || !currentLocation) return -1;
  const [currentLat, currentLng] = currentLocation;

  for (let i = 0; i < routeData.points.length; i++) {
    const point = routeData.points[i];
    const distance = haversineDistance(currentLat, currentLng, point.lat, point.lng);
    if (distance <= radiusMeters) return i;
  }
  return -1;
}

export default function MainPage({ currentLocation, setCurrentLocation }) {
  // Core states
  const [chatHistory, setChatHistory] = useState([]);
  const [routeData, setRouteData] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [calories, setCalories] = useState(null);
  const [audioEnabled, setAudioEnabled] = useState(false);
  const [roamEnabled, setRoamEnabled] = useState(false);
  const [apiKey, setApiKey] = useState(null);

  // Speech trigger on proximity
  useEffect(() => {
    if (!currentLocation || !audioEnabled) return;
    const nearbyPoint = findNearbyPointIndex(routeData, currentLocation);
    if (nearbyPoint !== -1 && routeData?.points?.[nearbyPoint]?.script) {
      speakText(routeData.points[nearbyPoint].script, apiKey);
    }
  }, [currentLocation, audioEnabled]);

  // Roaming AI polling logic
  useEffect(() => {
    if (!roamEnabled) return;
    console.log("Starting roam polling...");
    
    const intervalId = setInterval(async () => {
      console.log("Polling AI service...");
      try {
        const response = await fetch("https://passepartout-dmx5.onrender.com/roam", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            coordinates: currentLocation?.join(", ") ?? "",
            context: chatHistory
          })
        });
        const data = await response.json();
        if (data.summary) {
          speakText(data.summary, apiKey);
          setChatHistory(prev => [...prev, { role: "assistant", content: data.summary }]);
        }
      } catch (error) {
        console.error("Roam polling error:", error);
      }
    }, 60000);

    return () => {
      console.log("Stopping roam polling...");
      clearInterval(intervalId);
    };
  }, [roamEnabled]);

  // Calculate calories when route updates
  useEffect(() => {
    if (routeData) {
      console.log("Route data updated.", routeData);
      setCalories(calculateCalories(
        routeData.total_distance_km, 
        routeData.estimated_duration_minutes
      ));
    }
  }, [routeData]);

  // Main AI request handler (route generation)
  const handleAIRequest = async (inputText) => {
    const updatedHistory = [...chatHistory, { role: "user", content: inputText }];
    setChatHistory(updatedHistory);
    console.log("Submitting AI request:", inputText);

    try {
      const response = await fetch("https://passepartout-dmx5.onrender.com/generate-route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_text: inputText, context: chatHistory })
      });
      const data = await response.json();

      if (data.is_route_response) {
        setRouteData(data);
      } else {
        console.log("Non-route response received.");
      }

      setChatHistory(prev => [...updatedHistory, { role: "assistant", content: data.chat_response }]);
    } catch (error) {
      console.error("AI request error:", error);
    }
  };

  // Fetch weather data for current location
  useEffect(() => {
    if (currentLocation?.[0] && currentLocation?.[1]) {
      fetchWeatherData(currentLocation[0], currentLocation[1]);
    }
  }, [currentLocation]);

  const fetchWeatherData = async (lat, lng) => {
    setWeatherLoading(true);
    try {
      const API_KEY = process.env.REACT_APP_OPENWEATHER_API_KEY || '429786abfd1c8dc244cd9c6eecd024bc';
      const response = await fetch(`https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lng}&appid=${API_KEY}&units=metric`);

      if (response.ok) {
        const data = await response.json();
        setWeatherData(data);
      } else {
        console.error('Weather API request failed.');
        setWeatherData(null);
      }
    } catch (error) {
      console.error('Weather API error:', error);
      setWeatherData(null);
    } finally {
      setWeatherLoading(false);
    }
  };

  // Estimate arrival time from now
  const calculateETA = (durationMinutes) => {
    if (!durationMinutes || isNaN(durationMinutes)) return "N/A";
    const now = new Date();
    const eta = new Date(now.getTime() + (durationMinutes * 60000) * 7); // (7x multiplier??)
    return eta.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
  };

  // Main render
  return (
    <div style={{ height: "100vh", overflow: "hidden", display: "flex", flexDirection: "column" }}>
      <div style={{ flex: 1, display: "flex", gap: "1rem", padding: "1rem" }}>
        {/* Left Panel: Info + Weather */}
        <div style={{ width: "250px", display: "flex", flexDirection: "column", gap: "1rem", paddingTop: "0.25rem" }}>

          {/* Trip Info Box */}
          <div style={{ border: "1px solid orange", borderRadius: "8px", padding: "1rem", boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)' }}>
            <h3>Trip Info</h3>
            {routeData?.route ? (
              <>
                <p>Distance: {routeData.route.total_distance_km?.toFixed(1) ?? 'N/A'} km</p>
                <p>ETA: {calculateETA(routeData.route.estimated_duration_minutes)}</p>
              </>
            ) : <p>No route generated.</p>}
          </div>

          {/* Route Points List */}
          <div style={{ border: "1px solid orange", borderRadius: "8px", padding: "1rem", boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)' }}>
            <h3>Route</h3>
            <div style={{ maxHeight: '40vh', overflowY: 'auto', paddingRight: '8px' }}>
              {routeData?.points?.length > 0 ? (
                routeData.points.map((point, index) => (
                  <div key={index} style={{ marginBottom: index < routeData.points.length - 1 ? '30px' : '0', paddingLeft: '30px', position: 'relative' }}>

                    {/* Visual Timeline Dots */}
                    <div style={{ position: 'absolute', left: 0, top: '50%', transform: 'translateY(-50%)', width: '20px', height: '20px', background: 'linear-gradient(135deg, #ff6b6b, #ee5a24)', borderRadius: '50% 50% 50% 0', transform: 'translateY(-50%) rotate(-45deg)', boxShadow: '0 2px 4px rgba(0,0,0,0.2)' }}>
                      <div style={{ width: '8px', height: '8px', background: 'white', borderRadius: '50%', transform: 'rotate(45deg)' }}></div>
                    </div>

                    {/* Duration Marker */}
                    {index > 0 && point.duration_from_prev && (
                      <div style={{ position: 'absolute', left: '25px', top: '-15px', background: 'white', padding: '2px 6px', borderRadius: '10px', fontSize: '11px', fontWeight: 'bold', border: '1px solid #ddd' }}>
                        {Math.round(point.duration_from_prev)} min
                      </div>
                    )}

                    <span style={{ fontSize: '14px', color: '#333' }}>{point.name}</span>
                  </div>
                ))
              ) : <p>No route points.</p>}
            </div>
          </div>

          <WeatherComponent weatherData={weatherData} weatherLoading={weatherLoading} currentLocation={currentLocation} />
        </div>

        {/* Center Map */}
        <div style={{ flex: 1, border: "2px solid #ccc", borderRadius: "8px", position: "relative", maxHeight: "95vh" }}>
          <MapComponent key={routeData?.route?.id ?? "empty"} pathData={routeData} currentLocation={currentLocation} />
        </div>

        {/* Right Panel: Chat + Controls */}
        <div style={{ width: "300px", display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div style={{ display: "flex", flexDirection: "column", height: "50vh", border: "1px solid #ccc", borderRadius: "8px", padding: "1rem" }}>
            <ChatWindow chatHistory={chatHistory} />
            <TextBox onSubmit={handleAIRequest} />
          </div>
          <VoiceWindow audioEnabled={audioEnabled} setAudioEnabled={setAudioEnabled} roamEnabled={roamEnabled} setRoamEnabled={setRoamEnabled}/>
          <Simulator currentLocation={currentLocation} setCurrentLocation={setCurrentLocation} />
        </div>
      </div>
    </div>
  );
}