import React, { useState } from 'react';
import { AiOutlineArrowUp } from 'react-icons/ai';

export default function TextBox({ onSubmit }) {
  const [input, setInput] = useState('');
  const [isHovered, setIsHovered] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() === '') return;
    onSubmit(input);
    setInput('');
  };

  const baseColor = '#FFA500';
  const hoverColor = '#e59400';  // slightly darker orange

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      padding: '1rem',
      background: '#f9fafb',
      borderRadius: '12px',
      boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
      maxWidth: '600px',
      margin: '0 auto'
    }}>
      <form onSubmit={handleSubmit} style={{ display: 'flex', width: '100%', display: 'flex', alignItems: 'center', topPadding: '0.5rem'  }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the AI..."
          style={{
            flex: 1,
            padding: '0.75rem 1rem',
            border: '1px solid #ccc',
            borderRadius: '8px',
            fontSize: '1rem',
            marginRight: '0.5rem',
          }}
        />
        <button
          type="submit"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          style={{
            height: '30px',
            width: '30px',
            backgroundColor: isHovered ? hoverColor : baseColor,
            color: 'white',
            border: 'none',
            borderRadius: '50%',
            fontSize: '1.5rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'background-color 0.3s'
          }}
        >
          <AiOutlineArrowUp />
        </button>
      </form>
    </div>
  );
}
