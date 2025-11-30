import React, { useState, useEffect } from 'react';
import PlayerDashboard from './components/PlayerDashboard';
import ShotChart from './components/ShotChart';
import AIAnalysis from './components/AIAnalysis';
import TrainingPlan from './components/TrainingPlan';
import { fetchPlayer, fetchShootingSessions } from './services/api';
import './styles/App.css';

// Main application component - orchestrates all features
function App() {
  // State for player data
  const [player, setPlayer] = useState(null);
  // State for shot data
  const [shots, setShots] = useState([]);
  // State for loading status
  const [loading, setLoading] = useState(true);

  // useEffect hook to load initial data when component mounts
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);
        
        // Fetch player data and shots in parallel
        const [playerData, shotsData] = await Promise.all([
          fetchPlayer(1),
          fetchShootingSessions(1)
        ]);
        
        // Update state with fetched data
        setPlayer(playerData);
        setShots(shotsData);
        setLoading(false);
      } catch (error) {
        console.error('Error loading initial data:', error);
        setLoading(false);
      }
    };

    loadInitialData();
  }, []); // Empty dependency array = run once on mount

  // Show loading state while data is being fetched
  if (loading) {
    return (
      <div className="app-loading">
        <h1>PlusMinus Analytics</h1>
        <div>Loading your performance data...</div>
      </div>
    );
  }

  // Mock weaknesses for training plan - in real app, derived from AI analysis
  const mockWeaknesses = [
    "Left-hand finishing",
    "Perimeter defense", 
    "Three-point consistency"
  ];

  // Main application render
  return (
    <div className="App">
      {/* Application header */}
      <header className="app-header">
        <h1>PlusMinus Analytics</h1>
        <p>Basketball Performance Intelligence Platform</p>
      </header>

      {/* Main content grid */}
      <main className="main-content">
        {/* Player dashboard section */}
        <section className="dashboard-section">
          <PlayerDashboard />
        </section>

        {/* Shot visualization section */}
        <section className="shot-section">
          <ShotChart shots={shots} />
        </section>

        {/* AI insights section */}
        <section className="ai-section">
          <AIAnalysis playerId={player?.id} />
        </section>

        {/* Training plan section */}
        <section className="training-section">
          <TrainingPlan 
            playerId={player?.id} 
            weaknesses={mockWeaknesses}
          />
        </section>
      </main>

      {/* Application footer */}
      <footer className="app-footer">
        <p>Built with React & JSON Server | PlusMinus Analytics © 2024</p>
      </footer>
    </div>
  );
}

export default App;