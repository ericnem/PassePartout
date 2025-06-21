import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Import leaflet icons directly (CRA fix)
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Import your local GeoJSON file
import pathData from './test_response.json';

// Fix default Leaflet marker paths for CRA
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// Create custom icon for currentLocation marker
const currentLocationIcon = new L.Icon({
  iconUrl: 'https://maps.gstatic.com/mapfiles/ms2/micons/blue-dot.png',
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

export default function MapComponent({ currentLocation }) {
  const points = [];
  let pathCoordinates = [];

  // Parse the GeoJSON data
  pathData.geojson.features.forEach((feature) => {
    if (feature.geometry.type === 'LineString') {
      pathCoordinates = feature.geometry.coordinates.map(
        (coord) => [coord[1], coord[0]]  // GeoJSON [lng, lat] -> Leaflet [lat, lng]
      );
    }
    if (feature.geometry.type === 'Point') {
      const [lng, lat] = feature.geometry.coordinates;
      points.push({
        lat,
        lng,
        name: feature.properties.name,
        script: feature.properties.script,
      });
    }
  });

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <MapContainer
        center={[43.6426, -79.3871]} 
        zoom={13} 
        style={{ height: '100%', width: '100%', borderRadius: '8px' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />

        {/* Draw route polyline */}
        {pathCoordinates.length > 0 && (
          <Polyline positions={pathCoordinates} color="blue" weight={5} />
        )}

        {/* Draw point markers */}
        {points.map((point, idx) => (
          <Marker key={idx} position={[point.lat, point.lng]}>
            <Popup>
              <strong>{point.name}</strong><br />
              {point.script}
            </Popup>
          </Marker>
        ))}

        {/* Draw current location marker */}
        {currentLocation && (
          <Marker position={currentLocation} icon={currentLocationIcon}>
            <Popup>You are here</Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}
