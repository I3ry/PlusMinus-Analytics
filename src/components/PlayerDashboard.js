import React, { useState, useEffect } from 'react';

// Main dashboard component that displays player analytics
const PlayerDashboard = () => {
  // State to store player data - useState hook manages component state
  const [playerData, setPlayerData] = useState(null);
  // State to track loading status
  const [loading, setLoading] = useState(true);

  // useEffect hook runs after component mounts - similar to componentDidMount
  useEffect(() => {
    // Simulate API call to fetch player data
    const fetchPlayerData = async () => {
      try {
        // In real app, this would be: await fetch('/api/players/1')
        const mockPlayer = {
          id: 1,
          name: "Jordan Mitchell",
          position: "SG",
          skill_rating: 84,
          recent_performance: {
            points: 22.5,
            rebounds: 4.2,
            assists: 5.1,
            shooting_pct: 47.8
          }
        };
        
        // Update state with fetched data - triggers re-render
        setPlayerData(mockPlayer);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching player data:', error);
        setLoading(false);
      }
    };

    fetchPlayerData();
  }, []); // Empty dependency array means this runs once on mount

  // Show loading spinner while data is being fetched
  if (loading) {
    return <div className="loading">Loading player data...</div>;
  }

  // Main component render
  return (
    <div className="dashboard">
      {/* Player header section */}
      <div className="player-header">
        <h1>{playerData.name}</h1>
        <div className="player-info">
          <span>Position: {playerData.position}</span>
          <span>Overall: {playerData.skill_rating}</span>
        </div>
      </div>

      {/* Performance metrics grid */}
      <div className="metrics-grid">
        {/* Individual metric cards */}
        <div className="metric-card">
          <h3>PPG</h3>
          <p className="metric-value">{playerData.recent_performance.points}</p>
        </div>
        <div className="metric-card">
          <h3>RPG</h3>
          <p className="metric-value">{playerData.recent_performance.rebounds}</p>
        </div>
        <div className="metric-card">
          <h3>APG</h3>
          <p className="metric-value">{playerData.recent_performance.assists}</p>
        </div>
        <div className="metric-card">
          <h3>FG%</h3>
          <p className="metric-value">{playerData.recent_performance.shooting_pct}%</p>
        </div>
      </div>
    </div>
  );
};

// Export component for use in other files
export default PlayerDashboard;