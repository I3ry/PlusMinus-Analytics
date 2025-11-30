// Utility functions for basketball analytics calculations

/**
 * Calculates shooting percentage from made and total shots
 * @param {number} made - Number of shots made
 * @param {number} total - Total shots attempted
 * @returns {number} Shooting percentage (0-100)
 */
export const calculateShootingPercentage = (made, total) => {
  // Prevent division by zero
  if (total === 0) return 0;
  // Calculate percentage and round to 1 decimal place
  return Math.round((made / total) * 100 * 10) / 10;
};

/**
 * Generates heatmap data from shot locations
 * @param {Array} shots - Array of shot objects with x_coord, y_coord
 * @returns {Object} Heatmap data grouped by court zones
 */
export const generateHeatmapData = (shots) => {
  // Define court zones for grouping shots
  const zones = {
    'paint': { count: 0, made: 0 },
    'mid_range': { count: 0, made: 0 },
    'left_corner_3': { count: 0, made: 0 },
    'right_corner_3': { count: 0, made: 0 },
    'top_3': { count: 0, made: 0 }
  };

  // Process each shot and categorize by zone
  shots.forEach(shot => {
    const { x_coord, y_coord, made } = shot;
    
    // Simple zone classification logic
    if (y_coord < 10) {
      zones.paint.count++;
      if (made) zones.paint.made++;
    } else if (y_coord < 20 && x_coord > 30 && x_coord < 70) {
      zones.mid_range.count++;
      if (made) zones.mid_range.made++;
    } else if (x_coord <= 30 && y_coord >= 20) {
      zones.left_corner_3.count++;
      if (made) zones.left_corner_3.made++;
    } else if (x_coord >= 70 && y_coord >= 20) {
      zones.right_corner_3.count++;
      if (made) zones.right_corner_3.made++;
    } else {
      zones.top_3.count++;
      if (made) zones.top_3.made++;
    }
  });

  return zones;
};

/**
 * Calculates player efficiency rating (simplified)
 * @param {Object} stats - Player statistics object
 * @returns {number} Efficiency rating
 */
export const calculateEfficiency = (stats) => {
  // PER formula components (simplified for demo)
  const { points, rebounds, assists, steals, blocks, turnovers, games_played } = stats;
  
  // Basic efficiency calculation
  const efficiency = (points + rebounds + assists + steals + blocks - turnovers) / games_played;
  return Math.round(efficiency * 10) / 10;
};