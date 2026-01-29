// API Configuration with Mock Fallback
import mockAuthHandler from '../services/mockApi';

// Get API URL from environment variable or mock by default for development
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const USE_MOCK_API = process.env.REACT_APP_USE_MOCK === 'true' || false; // Disable mock by default to use real backend

// Create a fetch wrapper that can use mock API
const fetchWithMock = async (url, options) => {
  if (USE_MOCK_API && url.includes('/api/auth')) {
    // Extract endpoint from full URL
    const endpoint = url.replace(API_URL, '');
    const body = options?.body ? JSON.parse(options.body) : {};
    
    try {
      const mockResponse = await mockAuthHandler(endpoint, body);
      return mockResponse;
    } catch (error) {
      console.error('Mock API error:', error);
      throw error;
    }
  }
  
  // Fall back to real API
  return fetch(url, options);
};

// Export both the base URL and the fetch wrapper
export const API_BASE_URL = API_URL;
export const customFetch = fetchWithMock;

export default API_BASE_URL;
