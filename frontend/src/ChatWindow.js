import React from 'react';

export default function ChatWindow({ chatHistory }) {
  return (
    <div style={{
      maxHeight: '300px',
      overflowY: 'auto',
      padding: '1rem',
      margin: '1rem 0',
      maxWidth: '90%',
      backgroundColor: '#f1f1f1',
      borderRadius: '8px',
      wordBreak: 'break-word'
    }}>
      {chatHistory.map((message, idx) => (
        <div key={idx} style={{
          marginBottom: '1rem',
          textAlign: message.role === 'user' ? 'right' : 'left'
        }}>
          <div style={{
            display: 'inline-block',
            maxWidth: '100%',
            padding: '0.5rem 1rem',
            borderRadius: '12px',
            backgroundColor: message.role === 'user' ? '#FFA500' : '#e0e0e0',
            color: message.role === 'user' ? 'white' : 'black',
            wordBreak: 'break-word',
          }}>
            {message.content ? message.content : "Generating path..."}
          </div>
        </div>
      ))}
    </div>
  );
}
