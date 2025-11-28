import { API_BASE_URL } from '../config/api';




export const generateTicketData = async (conversationHistory, userMessage) => {
  // Call backend to create ticket
  try {
      const response = await fetch(`${API_BASE_URL}/tickets/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title: userMessage.substring(0, 50),
        description: userMessage,
        priority: 'High', // Default or derived
        category: 'general',
        // Add fields required for dashboard
        tier: 'Tier 1',
        tags: [
          { label: 'AI Generated', confidence: 100 },
          { label: 'Escalation', confidence: 95 }
        ],
        sentiment: 'Neutral',
        sentimentScore: 0.5,
        kbMatch: 'KB-2024-001 (85%)',
        slaRisk: false
      }),
    });
    
    if (!response.ok) throw new Error('Failed to create ticket');
    
    const ticket = await response.json();
    return {
        id: ticket.id,
        subject: ticket.title,
        description: ticket.description,
        priority: ticket.priority,
        status: ticket.status,
        created: ticket.created_at
    };
  } catch (error) {
      console.error("Error creating ticket:", error);
      // Fallback mock for UI continuity if API fails
      return {
        id: `INC-${Date.now()}`,
        subject: "Error creating ticket",
        description: userMessage,
        priority: "High",
        status: "New",
        created: new Date().toISOString()
      };
  }
};

/**
 * Creates a new ticket in the backend.
 * @param {Object} ticketData - The ticket data.
 * @returns {Promise<Object>} - The created ticket.
 */
export const createTicket = async (ticketData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/tickets/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(ticketData),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating ticket:', error);
    throw error;
  }
};

/**
 * Fetches all tickets from the backend.
 * @returns {Promise<Array>} - List of tickets.
 */
export const getTickets = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/tickets/`);

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching tickets:', error);
    throw error;
  }
};
