import React from 'react';

export default function WeatherComponent({ weatherData, weatherLoading, currentLocation }) {

  const getWeatherIcon = (iconCode) => {
    return `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
  };

  if (weatherLoading) {
    return (
      <div style={{ marginTop: '10px', textAlign: 'center' }}>
        <p>Loading weather...</p>
      </div>
    );
  }

  if (weatherData) {
    return (
      <div style={{
        marginTop: '15px',
        padding: '10px',
        background: 'linear-gradient(135deg, #74b9ff, #0984e3)',
        borderRadius: '8px',
        color: 'white'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h4 style={{ margin: '0 0 5px 0', fontSize: '16px' }}>
              {weatherData.name || 'Current Location'}
            </h4>
            <p style={{ margin: '0', fontSize: '24px', fontWeight: 'bold' }}>
              {Math.round(weatherData.main.temp)}°C
            </p>
            <p style={{ margin: '5px 0 0 0', fontSize: '14px' }}>
              {weatherData.weather[0].description}
            </p>
            <p style={{ margin: '5px 0 0 0', fontSize: '12px' }}>
              Feels like: {Math.round(weatherData.main.feels_like)}°C
            </p>
          </div>
          <div>
            <img
              src={getWeatherIcon(weatherData.weather[0].icon)}
              alt={weatherData.weather[0].description}
              style={{ width: '50px', height: '50px' }}
            />
          </div>
        </div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginTop: '10px',
          fontSize: '12px'
        }}>
          <span>Humidity: {weatherData.main.humidity}%</span>
          <span>Wind: {Math.round(weatherData.wind.speed)} m/s</span>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      marginTop: '10px',
      padding: '10px',
      background: '#f8f9fa',
      borderRadius: '8px',
      textAlign: 'center',
      fontSize: '14px',
      color: '#666'
    }}>
      <p>Weather data not available</p>
      <p style={{ fontSize: '12px', margin: '5px 0 0 0' }}>
        Add OpenWeatherMap API key to enable weather
      </p>
    </div>
  );
}
