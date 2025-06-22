import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Import and fix default Leaflet icons (for CRA compatibility)
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Override Leaflet's default icon URLs
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// Fit map bounds to route points
function FitMapToBounds({ points }) {
  const map = useMap();

  useEffect(() => {
    if (points.length > 0) {
      const bounds = points.map(p => [p.lat, p.lng]);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [points, map]);

  return null;
}

// Custom icon for current location marker
const currentLocationIcon = new L.Icon({
  iconUrl: 'https://maps.gstatic.com/mapfiles/ms2/micons/blue-dot.png',
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

export default function MapComponent({ pathData, currentLocation }) {
  const [points, setPoints] = useState([]);
  const [pathCoordinates, setPathCoordinates] = useState([]);

  // Parse GeoJSON data into points and path coordinates
  useEffect(() => {
    if (!pathData) {
      setPoints([]);
      setPathCoordinates([]);
      return;
    }

    const newPoints = [];
    let newPath = [];

    pathData.geojson.features.forEach((feature) => {
      if (feature.geometry.type === 'LineString') {
        newPath = feature.geometry.coordinates.map(([lng, lat]) => [lat, lng]);
      }
      if (feature.geometry.type === 'Point') {
        const [lng, lat] = feature.geometry.coordinates;
        newPoints.push({
          lat,
          lng,
          name: feature.properties.name,
          script: feature.properties.script,
        });
      }
    });

    setPoints(newPoints);
    setPathCoordinates(newPath);
  }, [pathData]);

  // Render default empty map when no pathData exists
  if (!pathData) {
    return (
      <div style={{ height: '100%', width: '100%' }}>
        <MapContainer center={[43.466752, -80.537190]} zoom={13} style={{ height: '100%', width: '100%', borderRadius: '8px' }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; OpenStreetMap contributors'
          />
          {currentLocation && (
            <Marker position={currentLocation} icon={currentLocationIcon}>
              <Popup>You are here</Popup>
            </Marker>
          )}
        </MapContainer>
      </div>
    );
  }

  // Render full map with route
  return (
    <div style={{ height: '100%', width: '100%' }}>
      <MapContainer center={currentLocation ?? [43.466752, -80.537190]} zoom={13} style={{ height: '100%', width: '100%', borderRadius: '8px' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />

        {/* Fit bounds to points */}
        <FitMapToBounds points={points} />

        {/* Draw path line */}
        {pathCoordinates.length > 0 && (
          <Polyline positions={pathCoordinates} color="blue" weight={5} />
        )}

        {/* Place markers for each point */}
        {points.map((point, idx) => (
          <Marker key={idx} position={[point.lat, point.lng]}>
            <Popup>
              <strong>{point.name}</strong><br />
              {point.script && point.script.length > 200
                ? point.script.slice(0, 200) + '...'
                : point.script}
            </Popup>
          </Marker>
        ))}

        {/* Current location marker */}
        {currentLocation && (
          <Marker position={currentLocation} icon={currentLocationIcon}>
            <Popup>You are here</Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}