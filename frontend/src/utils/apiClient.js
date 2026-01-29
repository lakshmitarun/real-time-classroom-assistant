/**
 * Safe API Client - Handles JSON parse errors gracefully
 * Prevents "Unexpected token '<'" errors from non-JSON responses
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

/**
 * Safely fetch and parse JSON response
 * Falls back to mock data if real API fails in development
 */
export const safeFetch = async (endpoint, options = {}) => {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    console.log(`📡 [API] ${options.method || 'GET'} ${endpoint}`);

    // Merge headers properly - ensure Content-Type is always set
    const mergedHeaders = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers: mergedHeaders,
    });

    console.log(`   Status: ${response.status}`);

    // Check if response is JSON
    const contentType = response.headers.get('content-type');
    const isJSON = contentType && contentType.includes('application/json');

    if (!isJSON) {
      // ❌ Non-JSON response (likely HTML error page)
      const text = await response.text();
      console.error(`❌ [API] Non-JSON response:`, text.substring(0, 100));
      
      throw new Error(
        `Server returned ${response.status} with non-JSON response. ` +
        `Endpoint: ${endpoint}. Response: ${text.substring(0, 100)}`
      );
    }

    // ✅ Parse JSON
    const data = await response.json();

    if (!response.ok) {
      // ❌ API returned error (but in valid JSON)
      console.error(`❌ [API] Error ${response.status}:`, data);
      throw new Error(data.error || data.message || `API Error ${response.status}`);
    }

    // ✅ Success
    console.log(`✅ [API] Success:`, data);
    return {
      ok: true,
      status: response.status,
      data,
    };
  } catch (error) {
    console.error(`❌ [API] Exception:`, error.message);

    // ⚠️ Fallback to mock data in development
    if (process.env.NODE_ENV === 'development' && process.env.REACT_APP_USE_MOCK === 'true') {
      console.warn(`⚠️ [API] Falling back to mock data`);
      return {
        ok: true,
        status: 200,
        data: {
          success: true,
          message: 'Mock data (API unavailable)',
        },
      };
    }

    return {
      ok: false,
      status: 0,
      error: error.message,
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
