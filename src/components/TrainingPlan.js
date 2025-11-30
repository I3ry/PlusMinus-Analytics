import React, { useState, useEffect } from 'react';

// Component to generate and display personalized training plans
const TrainingPlan = ({ playerId, weaknesses = [] }) => {
  // State to store generated training plan
  const [trainingPlan, setTrainingPlan] = useState(null);
  
  // useEffect hook to generate plan when weaknesses change
  useEffect(() => {
    if (weaknesses.length > 0) {
      generateTrainingPlan(weaknesses);
    }
  }, [weaknesses]); // Dependency array - runs when weaknesses change

  /**
   * Generates personalized training plan based on weaknesses
   * @param {Array} playerWeaknesses - Array of weakness strings
   */
  const generateTrainingPlan = (playerWeaknesses) => {
    // Exercise database categorized by skill
    const exerciseDatabase = {
      'shooting': [
        { name: 'Form Shooting', duration: '10 mins', focus: 'Mechanics' },
        { name: 'Spot Shooting', duration: '15 mins', focus: 'Consistency' },
        { name: 'Off-Dribble 3s', duration: '20 mins', focus: 'Game Shots' }
      ],
      'ball_handling': [
        { name: 'Two-Ball Dribbling', duration: '15 mins', focus: 'Coordination' },
        { name: 'Cone Weaves', duration: '20 mins', focus: 'Control' }
      ],
      'defense': [
        { name: 'Closeout Drills', duration: '15 mins', focus: 'Footwork' },
        { name: 'Shell Defense', duration: '20 mins', focus: 'Team Defense' }
      ]
    };

    // Map weaknesses to relevant exercises
    const planExercises = [];
    
    playerWeaknesses.forEach(weakness => {
      if (weakness.toLowerCase().includes('shoot')) {
        planExercises.push(...exerciseDatabase.shooting);
      } else if (weakness.toLowerCase().includes('handle') || weakness.toLowerCase().includes('turnover')) {
        planExercises.push(...exerciseDatabase.ball_handling);
      } else if (weakness.toLowerCase().includes('defens')) {
        planExercises.push(...exerciseDatabase.defense);
      }
    });

    // Remove duplicates and limit to 6 exercises
    const uniqueExercises = [...new Map(planExercises.map(item => 
      [item.name, item])).values()].slice(0, 6);

    // Create final training plan object
    const generatedPlan = {
      focus_areas: playerWeaknesses,
      exercises: uniqueExercises,
      schedule: {
        frequency: '4 days/week',
        session_duration: '90 minutes',
        duration_weeks: 6
      },
      goals: [
        `Improve ${playerWeaknesses[0]?.toLowerCase() || 'identified weaknesses'}`,
        "Increase overall efficiency rating by 5%",
        "Develop consistent practice habits"
      ]
    };

    setTrainingPlan(generatedPlan);
  };

  // Show loading state if no plan generated
  if (!trainingPlan) {
    return <div>Generating personalized training plan...</div>;
  }

  return (
    <div className="training-plan">
      <h3>Personalized Training Plan</h3>
      
      {/* Schedule overview */}
      <div className="schedule-overview">
        <h4>📅 Training Schedule</h4>
        <p>Frequency: {trainingPlan.schedule.frequency}</p>
        <p>Session Duration: {trainingPlan.schedule.session_duration}</p>
        <p>Program Length: {trainingPlan.schedule.duration_weeks} weeks</p>
      </div>

      {/* Exercise list */}
      <div className="exercises-section">
        <h4>💪 Daily Exercises</h4>
        <div className="exercises-grid">
          {trainingPlan.exercises.map((exercise, index) => (
            <div key={index} className="exercise-card">
              <h5>{exercise.name}</h5>
              <p>Duration: {exercise.duration}</p>
              <p>Focus: {exercise.focus}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Training goals */}
      <div className="goals-section">
        <h4>🎯 Program Goals</h4>
        <ul>
          {trainingPlan.goals.map((goal, index) => (
            <li key={index}>{goal}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default TrainingPlan;