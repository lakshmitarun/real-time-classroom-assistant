/**
 * Production-Aware Google Authentication Handler
 * Automatically disables mock auth in production
 */

/**
 * Determine if mock auth should be enabled
 * ✅ DEV: true (bypass origin check)
 * ✅ PROD: false (use real Google OAuth)
 */
const isMockAuthEnabled = () => {
  const mockEnv = process.env.REACT_APP_MOCK_GOOGLE_AUTH;
  const nodeEnv = process.env.NODE_ENV;
  const isProduction = nodeEnv === 'production';

  console.log('🔐 Auth Config:', {
    REACT_APP_MOCK_GOOGLE_AUTH: mockEnv,
    NODE_ENV: nodeEnv,
    isProduction,
  });

  // ✅ Auto-disable mock auth in production
  if (isProduction) {
    console.warn('⚠️ Production mode detected - Mock auth DISABLED');
    return false;
  }

  // ✅ Use env variable in development
  return mockEnv === 'true';
};

/**
 * Create mock Google response (for local development)
 */
export const createMockGoogleResponse = () => {
  const mockToken = 'mock-google-token-' + Math.random().toString(36).substr(2, 9);
  const mockId = 'mock-' + Math.random().toString(36).substr(2, 9);

  return {
    id: mockId,
    email: 'demo.teacher@example.com',
    name: 'Demo Teacher',
    picture: 'https://via.placeholder.com/96',
    credential: `mock-credential-${mockId}`,
  };
};

/**
 * Safe Google Login Handler
 * Handles both real and mock authentication with fallback
 */
export const handleGoogleLogin = async (credentialResponse, apiCallback) => {
  try {
    const useMockAuth = isMockAuthEnabled();

    if (useMockAuth) {
      console.log('🔐 Using MOCK authentication (development only)');
      const mockResponse = createMockGoogleResponse();
      return apiCallback({
        token: mockResponse.credential,
        email: mockResponse.email,
        name: mockResponse.name,
        isMock: true,
      });
    }

    // ✅ Real authentication
    console.log('🔐 Using REAL Google authentication');
    const credential = credentialResponse?.credential;

    if (!credential) {
      throw new Error('Google sign-in failed: no credential returned');
    }

    // Send to backend for verification
    return apiCallback({
      token: credential,
      isMock: false,
    });
  } catch (error) {
    console.error('❌ Google Login Error:', error);
    throw error;
  }
};

export default {
  isMockAuthEnabled,
  createMockGoogleResponse,
  handleGoogleLogin,
};
