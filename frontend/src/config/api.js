/**
 * API Configuration for Create React App
 * 
 * Environment Variable Priority:
 * 1. REACT_APP_API_URL (set in .env or .env.production)
 * 2. Default based on NODE_ENV
 * 
 * For Vercel Production:
 *   - Set REACT_APP_API_URL = https://classroom-assistant-backend.vercel.app
 * 
 * For Local Development:
 *   - REACT_APP_API_URL = http://localhost:5000
 */

// Determine the API URL
const getApiUrl = () => {
  // Priority 1: Environment variable
  if (process.env.REACT_APP_API_URL) {
    console.log('✅ Using REACT_APP_API_URL:', process.env.REACT_APP_API_URL);
    return process.env.REACT_APP_API_URL;
  }
  
  // Priority 2: Default based on environment
  if (process.env.NODE_ENV === 'production') {
    console.log('⚠️ Production mode: Using default backend URL');
    return 'https://classroom-assistant-backend.vercel.app';
  }
  
  // Local development
  console.log('✅ Development mode: Using localhost backend');
  return 'http://localhost:5000';
};

const API_BASE_URL = getApiUrl();

console.log('🔧 API Config:');
console.log('  - NODE_ENV:', process.env.NODE_ENV);
console.log('  - API_BASE_URL:', API_BASE_URL);
console.log('  - REACT_APP_API_URL:', process.env.REACT_APP_API_URL || '(not set)');

export default API_BASE_URL;
