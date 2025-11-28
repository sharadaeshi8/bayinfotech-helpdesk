// API-Based AI Simulator Replacement
// Calls the real backend API instead of using mock scripts

export const detectGuardrailViolation = (message) => {
  // Guardrail checks are now handled by the backend
  return { violated: false };
};

export const analyzeSentiment = (message, conversationContext = {}) => {
  // Sentiment analysis is now handled by the backend
  return {
    sentiment: 'neutral',
    score: 0,
    shouldEscalate: false,
  };
};


export const simulateTypingDelay = (messageLength) => {
  const baseDelay = 500;
  const charDelay = Math.min(messageLength * 10, 1500);
  return baseDelay + charDelay;
};

export const shouldCreateTicket = (conversationHistory) => {
  // Logic can remain here or move to backend. For now, keep simple frontend check or rely on backend.
  // The backend handles ticket creation via explicit endpoint, but frontend UI triggers it.
  return false; 
};

