import React, { useState } from "react";

export default function VoiceWindow({audioEnabled, setAudioEnabled, roamEnabled, setRoamEnabled}) {

  const toggleAudio = () => {
    setAudioEnabled(prev => !prev);
  };

  const toggleRoam = () => {
    setRoamEnabled(prev => !prev);
  }

  return (
    <div style={{
      border: '2px solid red',
      borderRadius: '10px',
      padding: '1rem',
      backgroundColor: '#fafafa',
      boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      <h3 style={{ margin: 0 }}>Voice Options</h3>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <label htmlFor="audioToggle" style={{ fontSize: '1rem' }}>Enable Audio Guide:</label>
        <input
          id="audioToggle"
          type="checkbox"
          checked={audioEnabled}
          onChange={toggleAudio}
          style={{ transform: 'scale(1.5)' }}
        />
      </div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <label htmlFor="roamToggle" style={{ fontSize: '1rem' }}>Enable Roaming:</label>
        <input
          id="audioToggle"
          type="checkbox"
          checked={roamEnabled}
          onChange={toggleRoam}
          style={{ transform: 'scale(1.5)' }}
        />
      </div>
    </div>
  );
}
