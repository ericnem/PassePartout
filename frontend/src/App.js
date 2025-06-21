import React, { useState } from 'react';
import { generateNarration } from './api';

function App() {
  const [poi, setPoi] = useState('');
  const [narration, setNarration] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const result = await generateNarration(poi);
      setNarration(result);
    } catch (error) {
      console.error(error);
      setNarration("Error generating narration.");
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h1>AI Tour Guide</h1>
      <input
        type="text"
        placeholder="Enter Point of Interest"
        value={poi}
        onChange={(e) => setPoi(e.target.value)}
        style={{ width: '300px', marginRight: '1rem' }}
      />
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Narration'}
      </button>

      <div style={{ marginTop: '2rem' }}>
        <h2>Narration:</h2>
        <p>{narration}</p>
      </div>
    </div>
  );
}

export default App;