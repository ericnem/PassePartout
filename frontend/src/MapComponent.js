import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Import leaflet icons directly (CRA fix)
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix default Leaflet marker paths for CRA
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

function FitMapToBounds({ points }) {
  const map = useMap();

  useEffect(() => {
    if (points.length > 0) {
      const bounds = points.map(p => [p.lat, p.lng]);
      map.fitBounds(bounds, { padding: [50, 50] });  // add some nice padding
    }
  }, [points, map]);

  return null;
}

// Create custom icon for currentLocation marker
const currentLocationIcon = new L.Icon({
  iconUrl: 'https://maps.gstatic.com/mapfiles/ms2/micons/blue-dot.png',
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

export default function MapComponent({ pathData, currentLocation }) {
  const [points, setPoints] = useState([]);
  const [pathCoordinates, setPathCoordinates] = useState([]);

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
        newPath = feature.geometry.coordinates.map(
          (coord) => [coord[1], coord[0]]  // GeoJSON [lng, lat] -> Leaflet [lat, lng]
        );
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

  if (!pathData) {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>
        Please submit a request to generate a route.
      </div>
    );
  }

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <MapContainer center={[43.6426, -79.3871]} zoom={13} style={{ height: '100%', width: '100%', borderRadius: '8px' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />

          <FitMapToBounds points={points} />

        {pathCoordinates.length > 0 && (
          <Polyline positions={pathCoordinates} color="blue" weight={5} />
        )}

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

        {currentLocation && (
          <Marker position={currentLocation} icon={currentLocationIcon}>
            <Popup>You are here</Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}
