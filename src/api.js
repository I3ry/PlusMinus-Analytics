// API service layer for handling all data operations

const API_BASE = 'http://localhost:3001';

/**
 * Fetches player data from API
 * @param {number} playerId - ID of player to fetch
 * @returns {Promise} Promise resolving to player data
 */
export const fetchPlayer = async (playerId) => {
  try {
    // Make GET request to players endpoint
    const response = await fetch(`${API_BASE}/players/${playerId}`);
    
    // Check if response is successful
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    // Parse JSON response
    const playerData = await response.json();
    return playerData;
  } catch (error) {
    console.error('Error fetching player:', error);
    throw error;
  }
};

/**
 * Fetches shooting sessions for a player
 * @param {number} playerId - ID of player
 * @returns {Promise} Promise resolving to sessions array
 */
export const fetchShootingSessions = async (playerId) => {
  try {
    // Query sessions by player_id
    const response = await fetch(`${API_BASE}/shooting_sessions?player_id=${playerId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const sessions = await response.json();
    return sessions;
  } catch (error) {
    console.error('Error fetching sessions:', error);
    throw error;
  }
};

/**
 * Submits new shot data to API
 * @param {Object} shotData - Shot data object
 * @returns {Promise} Promise resolving to created shot
 */
export const submitShot = async (shotData) => {
  try {
    // POST request to create new shot
    const response = await fetch(`${API_BASE}/shot_locations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(shotData)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const newShot = await response.json();
    return newShot;
  } catch (error) {
    console.error('Error submitting shot:', error);
    throw error;
  }
};