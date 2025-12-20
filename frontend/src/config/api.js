// API Configuration
// Use environment variable if available, otherwise default to localhost
// Variable: REACT_APP_API_URL

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export default API_BASE_URL;
