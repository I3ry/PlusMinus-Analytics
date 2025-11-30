import React from 'react';

// Component to visualize basketball shot locations on a court
const ShotChart = ({ shots = [] }) => {
  // Court dimensions and styling
  const courtStyle = {
    position: 'relative',
    width: '500px',
    height: '470px',
    backgroundColor: '#f5f5f5',
    border: '2px solid #333',
    margin: '20px auto'
  };

  // Function to render individual shot markers
  const renderShot = (shot, index) => {
    // Determine shot color based on make/miss
    const shotColor = shot.made ? '#00ff00' : '#ff0000';
    // Calculate position on court (scaling coordinates)
    const left = `${shot.x_coord * 2}%`;
    const top = `${shot.y_coord * 2}%`;

    return (
      <div
        key={index}
        style={{
          position: 'absolute',
          left: left,
          top: top,
          width: '12px',
          height: '12px',
          backgroundColor: shotColor,
          borderRadius: '50%',
          border: '1px solid #333',
          transform: 'translate(-50%, -50%)'
        }}
        title={`${shot.made ? 'Made' : 'Missed'} ${shot.shot_type}`}
      />
    );
  };

  return (
    <div className="shot-chart-container">
      <h3>Shot Chart</h3>
      <p>Green = Made, Red = Missed</p>
      {/* Court visualization container */}
      <div style={courtStyle}>
        {/* Render all shot markers */}
        {shots.map(renderShot)}
        
        {/* Court lines (simplified) */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '0',
          width: '100%',
          height: '2px',
          backgroundColor: '#333'
        }}></div>
      </div>
    </div>
  );
};

export default ShotChart;