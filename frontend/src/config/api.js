// Frontend API Configuration
// Centralized configuration for all API calls

/**
 * Get the API base URL from environment variables
 * Falls back to localhost if not set
 */
const getApiBaseUrl = () => {
  const url = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
  
  // Remove trailing slash if present
  return url.endsWith('/') ? url.slice(0, -1) : url;
};

export const API_BASE_URL = getApiBaseUrl();

/**
 * Get environment name
 */
export const getEnvironment = () => {
  return import.meta.env.VITE_ENV || 'development';
};

/**
 * Check if in development mode
 */
export const isDevelopment = () => {
  return getEnvironment() === 'development';
};

/**
 * Check if in production mode
 */
export const isProduction = () => {
  return getEnvironment() === 'production';
};

// Log configuration on load (development only)
if (isDevelopment()) {
  console.log('API Configuration:', {
    baseUrl: API_BASE_URL,
    environment: getEnvironment(),
  });
}
