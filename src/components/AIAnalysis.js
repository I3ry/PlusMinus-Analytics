import React, { useState } from 'react';

// Component that simulates AI-powered basketball analysis
const AIAnalysis = ({ playerId }) => {
  // State to store AI insights
  const [insights, setInsights] = useState(null);
  // State to track analysis loading status
  const [analyzing, setAnalyzing] = useState(false);

  // Function to simulate AI analysis - in real app, this would call an API
  const runAIAnalysis = () => {
    setAnalyzing(true);
    
    // Simulate API processing delay
    setTimeout(() => {
      // Mock AI insights based on player data
      const mockInsights = {
        strengths: [
          "Elite mid-range shooter (48% from 15-20 feet)",
          "Excellent court vision in transition",
          "Strong defensive positioning in paint"
        ],
        weaknesses: [
          "Left-hand finishing needs improvement (32% on left-handed layups)",
          "Defensive closeouts on perimeter shooters",
          "Turnover rate high in pick-and-roll situations"
        ],
        recommendations: [
          "Focus on left-hand Mikan drill daily",
          "Add off-dribble 3-point shooting to workout routine",
          "Study film on defensive rotations"
        ],
        comparable_players: ["DeMar DeRozan", "Khris Middleton", "CJ McCollum"]
      };
      
      setInsights(mockInsights);
      setAnalyzing(false);
    }, 2000);
  };

  return (
    <div className="ai-analysis">
      <h3>AI Performance Analysis</h3>
      
      {/* Analysis trigger button */}
      <button 
        onClick={runAIAnalysis} 
        disabled={analyzing}
        className="analyze-btn"
      >
        {analyzing ? 'Analyzing...' : 'Generate AI Insights'}
      </button>

      {/* Display insights when available */}
      {insights && (
        <div className="insights-container">
          {/* Strengths section */}
          <div className="insight-section strengths">
            <h4>🏆 Strengths</h4>
            <ul>
              {insights.strengths.map((strength, index) => (
                <li key={index}>{strength}</li>
              ))}
            </ul>
          </div>

          {/* Weaknesses section */}
          <div className="insight-section weaknesses">
            <h4>🎯 Areas for Improvement</h4>
            <ul>
              {insights.weaknesses.map((weakness, index) => (
                <li key={index}>{weakness}</li>
              ))}
            </ul>
          </div>

          {/* Training recommendations */}
          <div className="insight-section recommendations">
            <h4>💡 Training Recommendations</h4>
            <ul>
              {insights.recommendations.map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          </div>

          {/* Player comparisons */}
          <div className="insight-section comparisons">
            <h4>📊 Player Comparisons</h4>
            <div className="player-tags">
              {insights.comparable_players.map((player, index) => (
                <span key={index} className="player-tag">{player}</span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAnalysis;