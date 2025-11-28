import { API_BASE_URL } from '../config/api';


/**
 * Sends a message to the backend chat API.
 * @param {string} message - The user's message.
 * @param {string} sessionId - The current session ID.
 * @param {string} role - The user's role (mapped to backend enum).
 * @returns {Promise<Object>} - The backend response.
 */
export const sendMessageToBackend = async (message, sessionId, role = 'user', history = []) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        role,
        history: history.map(msg => ({
          role: msg.type === 'user' ? 'user' : 'assistant',
          content: msg.content
        }))
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending message to backend:', error);
    throw error;
  }
};

/**
 * Maps frontend role names to backend role enum values.
 * @param {string} frontendRole - The role name from the frontend user object.
 * @returns {string} - The corresponding backend role enum value.
 */
export const mapRoleToBackend = (frontendRole) => {
  switch (frontendRole) {
    case 'Administrator':
      return 'admin';
    case 'Help Desk Analyst':
      return 'support';
    case 'Cyber Operator':
    case 'Training Manager':
    default:
      return 'user';
  }
};

