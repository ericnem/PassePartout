import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline} from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix Leaflet's default icon issue with CRA
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
import pathData from './test_response.json';

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

export default function MapComponent() {
  const points = [];
  let pathCoordinates = [];

  pathData.geojson.features.forEach((feature) => {
    if (feature.geometry.type === 'LineString') {
      pathCoordinates = feature.geometry.coordinates.map(
        (coord) => [coord[1], coord[0]]  // reverse for Leaflet
      );
    }
    if (feature.geometry.type === 'Point') {
      const [lng, lat] = feature.geometry.coordinates;
      points.push({
        lat,
        lng,
        name: feature.properties.name
      });
    }
  });

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <MapContainer center={[43.6426, -79.3871]} zoom={13} style={{ height: '100%', width: '100%', borderRadius: '8px' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />

        {pathCoordinates.length > 0 && (
          <Polyline positions={pathCoordinates} color="blue" weight={5} />
        )}

        {points.map((point, idx) => (
          <Marker key={idx} position={[point.lat, point.lng]}>
            <Popup>{point.name}</Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
