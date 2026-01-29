// Mock API Service - Provides mock responses for development/demo purposes
// This service intercepts API calls and returns mock data

const MOCK_USERS = {
  'teacher@example.com': {
    id: '1',
    email: 'teacher@example.com',
    name: 'Demo Teacher',
    role: 'teacher',
    password: 'password123'
  },
  'student@example.com': {
    id: '2',
    email: 'student@example.com',
    name: 'Demo Student',
    role: 'student',
    password: 'password123'
  }
};

const MOCK_TOKEN = 'mock-jwt-token-' + Math.random().toString(36);

// Mock login/register handler
export const mockAuthHandler = async (endpoint, payload) => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  if (endpoint === '/api/auth/login') {
    const user = MOCK_USERS[payload.email];
    if (user && user.password === payload.password) {
      return {
        ok: true,
        status: 200,
        json: async () => ({
          token: MOCK_TOKEN,
          teacher: {
            id: user.id,
            email: user.email,
            name: user.name
          },
          role: user.role
        })
      };
    } else {
      return {
        ok: false,
        status: 401,
        json: async () => ({
          error: 'Invalid email or password'
        })
      };
    }
  } else if (endpoint === '/api/auth/register') {
    // Check if user already exists
    if (MOCK_USERS[payload.email]) {
      return {
        ok: false,
        status: 400,
        json: async () => ({
          error: 'Email already registered'
        })
      };
    }
    
    // Create new user
    const newUser = {
      id: Object.keys(MOCK_USERS).length + 1,
      email: payload.email,
      name: payload.name,
      role: 'teacher',
      password: payload.password
    };
    
    MOCK_USERS[payload.email] = newUser;
    
    return {
      ok: true,
      status: 201,
      json: async () => ({
        token: MOCK_TOKEN,
        teacher: {
          id: newUser.id,
          email: newUser.email,
          name: newUser.name
        },
        role: 'teacher'
      })
    };
  } else if (endpoint === '/api/auth/google/callback') {
    // Mock Google OAuth
    return {
      ok: true,
      status: 200,
      json: async () => ({
        token: MOCK_TOKEN,
        teacher: {
          id: '3',
          email: 'google-user@example.com',
          name: 'Google User'
        },
        role: 'teacher'
      })
    };
  }
  
  return {
    ok: false,
    status: 404,
    json: async () => ({ error: 'Not found' })
  };
};

export default mockAuthHandler;
