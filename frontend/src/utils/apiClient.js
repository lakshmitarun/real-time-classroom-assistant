/**
 * Production-ready API Client for Vercel Deployment
 * - Handles CORS properly with credentials
 * - Includes proper error handling
 * - Supports authorization tokens
 */

// Get API URL from environment or use defaults
const getBackendUrl = () => {
  const apiUrl = process.env.REACT_APP_API_URL ||
    (process.env.NODE_ENV === 'production'
      ? 'https://classroom-assistant-backend.vercel.app'  // ← UPDATE with YOUR backend URL
      : 'http://localhost:5000');
  
  console.log('[API] Backend URL:', apiUrl);
  return apiUrl;
};

/**
 * Main API client - handles fetch with proper CORS headers
 */
export const apiClient = {
  async fetch(endpoint, options = {}) {
    const url = `${getBackendUrl()}${endpoint}`;
    
    console.log(`📤 [${options.method || 'GET'}] ${url}`);
    
    // Build config without spreading options.headers twice
    const config = {
      method: options.method || 'GET',
      credentials: 'include',
    };

    // Carefully merge headers - don't let options.headers override defaults
    config.headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Add authorization token if exists
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
      console.log('[API] Authorization token included');
    }

    // Spread other options (body, etc) but preserve headers
    const { headers: _, ...otherOptions } = options;
    Object.assign(config, otherOptions);

    try {
      const response = await fetch(url, config);

      console.log(`📥 [${response.status}] ${response.statusText}`);

      // Log CORS headers for debugging
      const corsOrigin = response.headers.get('Access-Control-Allow-Origin');
      if (corsOrigin) {
        console.log(`[CORS] Allow-Origin: ${corsOrigin}`);
      }

      // Handle different content types
      const contentType = response.headers.get('content-type');
      let data;

      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      return {
        ok: response.ok,
        status: response.status,
        data: data,
        headers: response.headers,
      };
    } catch (error) {
      console.error(`❌ API Error: ${error.message}`);
      throw new Error(`Network error: ${error.message}`);
    }
  },

  // Convenience methods
  post(endpoint, body, options = {}) {
    return this.fetch(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(body),
    });
  },

  get(endpoint, options = {}) {
    return this.fetch(endpoint, { ...options, method: 'GET' });
  },

  put(endpoint, body, options = {}) {
    return this.fetch(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(body),
    });
  },

  delete(endpoint, options = {}) {
    return this.fetch(endpoint, { ...options, method: 'DELETE' });
  },
};

/**
 * Safe fetch wrapper with error handling
 * Returns {ok, error, data} object
 */
export const safeFetch = async (endpoint, options = {}) => {
  try {
    const result = await apiClient.fetch(endpoint, options);
    
    if (!result.ok) {
      console.error(`[SafeFetch] Error: ${result.status}`, result.data);
      return {
        ok: false,
        error: result.data?.error || result.data?.message || 'API Error',
        data: null,
      };
    }

    return {
      ok: true,
      error: null,
      data: result.data,
    };
  } catch (error) {
    console.error(`[SafeFetch] Exception:`, error);
    
    // Fallback to mock in development if enabled
    if (process.env.NODE_ENV === 'development' && process.env.REACT_APP_USE_MOCK === 'true') {
      console.warn(`⚠️ [API] Falling back to mock data`);
      return {
        ok: true,
        error: null,
        data: { success: true, message: 'Mock data (API unavailable)' },
      };
    }

    return {
      ok: false,
      error: error.message,
      data: null,
    };
  }
};

/**
 * Example usage:
 * 
 * // Login
 * const result = await safeFetch('/api/auth/login', {
 *   method: 'POST',
 *   body: JSON.stringify({ email, password })
 * });
 * 
 * if (result.ok) {
 *   const { token, teacher } = result.data;
 * } else {
 *   setError(result.error);
 * }
 */
