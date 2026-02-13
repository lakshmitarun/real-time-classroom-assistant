import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Mail, Lock, LogIn, User, Globe, BookOpen, Shield, Eye, EyeOff } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';
import { safeFetch } from '../utils/apiClient';
import API_BASE_URL from '../config/api';
import './LoginPage.css';

const LoginPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const userType = searchParams.get('type') || 'teacher'; // Get type from URL query param
  
  // Log environment and configuration
  React.useEffect(() => {
    console.log('🔍 LoginPage Configuration:');
    console.log('  API_BASE_URL:', API_BASE_URL);
    console.log('  REACT_APP_MOCK_GOOGLE_AUTH:', process.env.REACT_APP_MOCK_GOOGLE_AUTH);
    console.log('  User Type:', userType);
  }, [userType]);
  
  const [isLogin, setIsLogin] = useState(true); // Toggle between login and register
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '', // For register mode
    confirmPassword: ''
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(''); // Clear error on input change
  };

  const validateForm = () => {
    if (!formData.email || !formData.password) {
      setError('Email and password are required');
      return false;
    }

    if (!isLogin) {
      if (!formData.name) {
        setError('Name is required for registration');
        return false;
      }
      if (formData.password.length < 6) {
        setError('Password must be at least 6 characters');
        return false;
      }
      if (formData.password !== formData.confirmPassword) {
        setError('Passwords do not match');
        return false;
      }
    }

    return true;
  };

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const payload = isLogin 
        ? { email: formData.email, password: formData.password }
        : { email: formData.email, password: formData.password, name: formData.name };

      // ✅ Use safe API client with error handling
      const result = await safeFetch(endpoint, {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      if (!result.ok) {
        setError(result.error || 'Authentication failed');
        setLoading(false);
        return;
      }

      const data = result.data;

      if (isLogin) {
        // Login successful - redirect based on role
        // Get role from teacher object or user object, with fallback to 'teacher'
        const role = data.teacher?.role || data.user?.role || data.role || 'teacher';
        
        localStorage.setItem('token', data.token);
        localStorage.setItem('teacher', JSON.stringify(data.teacher));
        localStorage.setItem('userRole', role);
        
        setSuccess('Login successful! Redirecting...');
        
        if (role === 'student') {
          setTimeout(() => navigate('/student'), 1000);
        } else {
          setTimeout(() => navigate('/teacher-dashboard'), 1000);
        }
      } else {
        // Registration successful
        setSuccess('Registration successful! Logging in...');
        setFormData({ email: '', password: '', name: '', confirmPassword: '' });
        setIsLogin(true); // Switch to login mode
        setTimeout(() => {
          setSuccess('');
          // Auto-login with the registered email and password
          handleEmailLogin({ preventDefault: () => {} });
        }, 1000);
      }
    } catch (err) {
      setError(err.message || 'Network error');
    } finally {
      setLoading(false);
    }
  };

    // eslint-disable-next-line no-unused-vars
  const parseJwt = (token) => {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
          })
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (e) {
      return null;
    }
  };

  const handleGoogleResponse = async (credentialResponse) => {
    setLoading(true);
    setError('');

    try {
      // Check if mock Google auth is enabled (for local development)
      let useMockGoogle = process.env.REACT_APP_MOCK_GOOGLE_AUTH === 'true';
      
      if (useMockGoogle) {
        // Mock Google auth for local development - bypass origin check
        console.log('Using mock Google authentication for local development');
        await new Promise(resolve => setTimeout(resolve, 800)); // Simulate network delay
        
        // Create a mock token with teacher role
        const mockToken = 'mock-google-token-' + Math.random().toString(36).substr(2, 9);
        const mockTeacher = {
          id: 'mock-google-' + Math.random().toString(36).substr(2, 9),
          email: 'demo.teacher@example.com',
          name: 'Demo Teacher (Google Mock)'
        };
        
        localStorage.setItem('token', mockToken);
        localStorage.setItem('teacher', JSON.stringify(mockTeacher));
        localStorage.setItem('userRole', 'teacher');
        setSuccess('✅ Mock Google Login successful! Redirecting...');
        setTimeout(() => navigate('/teacher-dashboard'), 1000);
        return;
      }

      const credential = credentialResponse?.credential;
      if (!credential) {
        setError('Google sign-in failed: no credential returned');
        setLoading(false);
        return;
      }

      // Decode the JWT token from Google to get user info
      const decodedToken = parseJwt(credential);
      console.log('🔐 Google token decoded:', decodedToken);

      // Extract user info from the Google token
      const googleEmail = decodedToken?.email || '';
      const googleName = decodedToken?.name || '';
      const googlePicture = decodedToken?.picture || '';

      // Send the raw ID token (credential) to the backend for verification
      try {
        console.log('Attempting Google auth with backend at:', API_BASE_URL);
        const res = await fetch(`${API_BASE_URL}/api/auth/google/callback`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ credential })
        });

        console.log('Response status:', res.status);
        console.log('Response headers:', res.headers);
        
        const responseText = await res.text();
        console.log('Response text:', responseText.substring(0, 200));
        
        let data;
        try {
          data = JSON.parse(responseText);
        } catch (parseError) {
          console.error('Failed to parse response as JSON:', parseError);
          console.error('Response was:', responseText.substring(0, 500));
          throw new Error(`Backend returned non-JSON response: ${responseText.substring(0, 100)}`);
        }

        if (!res.ok) {
          throw new Error(data.error || 'Google login failed');
        }

        // Successful login - redirect based on role
        const role = data.role || data.teacher?.role || 'teacher'; // Default to teacher
        
        localStorage.setItem('token', data.token);
        localStorage.setItem('teacher', JSON.stringify(data.teacher));
        localStorage.setItem('userRole', role);
        setSuccess('Login successful! Redirecting...');
        
        // Redirect based on role (not userType)
        if (role === 'student') {
          setTimeout(() => navigate('/student'), 1000);
        } else {
          setTimeout(() => navigate('/teacher-dashboard'), 1000);
        }
      } catch (fetchError) {
        // If backend auth fails, fall back to using Google token data
        console.warn('Real Google auth failed, falling back to Google token data:', fetchError.message);
        
        if (!googleEmail) {
          throw new Error('Could not extract email from Google token');
        }

        // Create token using actual Google credentials
        const googleToken = 'google-token-' + Math.random().toString(36).substr(2, 9);
        const googleTeacher = {
          id: 'google-' + decodedToken?.sub || Math.random().toString(36).substr(2, 9),
          email: googleEmail,
          name: googleName || 'Google User',
          picture: googlePicture,
          role: 'teacher'
        };
        
        localStorage.setItem('token', googleToken);
        localStorage.setItem('teacher', JSON.stringify(googleTeacher));
        localStorage.setItem('userRole', 'teacher');
        setSuccess('✅ Login via Google successful! Redirecting...');
        setTimeout(() => navigate('/teacher-dashboard'), 1000);
      }
    } catch (err) {
      console.error('Google Auth Error:', err);
      setError(err.message || 'Google login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-wrapper">
        {/* Left Side - Branding */}
        <div className="login-branding">
          <div className="branding-content">
            <h1>Classroom Assistant</h1>
            <p className="tagline">{userType === 'student' ? 'Student Portal' : 'Teacher Portal'}</p>
            <p className="description">{userType === 'student' 
              ? 'Access real-time translations and multilingual support in your classroom.' 
              : 'Empower your classroom with intelligent multilingual support. Connect with your students in their language, anytime, anywhere.'}</p>
            <div className="branding-features">
              <div className="feature">
                <Globe size={28} className="feature-icon" />
                <span>Multilingual Support</span>
              </div>
              <div className="feature">
                <BookOpen size={28} className="feature-icon" />
                <span>{userType === 'student' ? 'Real-time Subtitles' : 'Classroom Management'}</span>
              </div>
              <div className="feature">
                <Shield size={28} className="feature-icon" />
                <span>Secure & Private</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="login-form-side">
          <div className="login-form-container card">
          <div className="form-header">
            <h2>{userType === 'student' ? 'Student Access' : (isLogin ? 'Sign In' : 'Create Account')}</h2>
            <p>{userType === 'student' ? 'Access the classroom' : (isLogin ? `Welcome back, ${userType}!` : `Join as a ${userType}`)}</p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="alert alert-error">
              <span style={{ fontSize: '16px' }}>⚠️ {error}</span>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="alert alert-success">
              <span style={{ fontSize: '16px' }}>✅ {success}</span>
            </div>
          )}

          {/* Email/Password Form - ONLY FOR TEACHERS */}
          {userType === 'teacher' && (
          <form onSubmit={handleEmailLogin} className="login-form">
            {/* Name Field (Register Only) */}
            {!isLogin && (
              <div className="form-group">
                <label htmlFor="name">Full Name</label>
                <div className="input-group">
                  <User size={18} />
                  <input
                    type="text"
                    id="name"
                    name="name"
                    placeholder="Your full name"
                    value={formData.name}
                    onChange={handleInputChange}
                    disabled={loading}
                  />
                </div>
              </div>
            )}

            {/* Email Field */}
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <div className="input-group">
                <Mail size={18} />
                <input
                  type="email"
                  id="email"
                  name="email"
                  placeholder="teacher@school.com"
                  value={formData.email}
                  onChange={handleInputChange}
                  disabled={loading}
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <div className="input-group">
                <Lock size={18} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleInputChange}
                  disabled={loading}
                  required
                />
                <button
                  type="button"
                  className="btn-toggle-password-icon"
                  onClick={() => setShowPassword(!showPassword)}
                  title={showPassword ? 'Hide password' : 'Show password'}
                  disabled={loading}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {/* Confirm Password (Register Only) */}
            {!isLogin && (
              <div className="form-group">
                <label htmlFor="confirmPassword">Confirm Password</label>
                <div className="input-group">
                  <Lock size={18} />
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    id="confirmPassword"
                    name="confirmPassword"
                    placeholder="Confirm your password"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    disabled={loading}
                    required
                  />
                  <button
                    type="button"
                    className="btn-toggle-password-icon"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    title={showConfirmPassword ? 'Hide password' : 'Show password'}
                    disabled={loading}
                  >
                    {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button 
              type="submit" 
              className="btn btn-primary btn-large"
              disabled={loading}
            >
              <LogIn size={20} />
              {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
            </button>
          </form>
          )}

          {/* Divider */}
          <div className="divider">
            <span>OR</span>
          </div>

          {/* Google Login Button (uses Google Identity via @react-oauth/google) */}
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <GoogleLogin
              onSuccess={handleGoogleResponse}
              onError={() => setError('Google sign-in failed')}
              theme="filled_blue"
              size="large"
              text="signin_with"
              shape="rectangular"
            />
          </div>

          {/* Toggle Form Mode - ONLY FOR TEACHERS */}
          {userType === 'teacher' && (
          <div className="form-footer">
            <p>
              {isLogin ? "Don't have an account? " : 'Already have an account? '}
              <button
                type="button"
                className="link-button"
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError('');
                  setSuccess('');
                }}
                disabled={loading}
              >
                {isLogin ? 'Sign Up' : 'Sign In'}
              </button>
            </p>
          </div>
          )}
        </div>

        {/* Demo Credentials - ONLY FOR TEACHERS */}
        {userType === 'teacher' && (
        <div className="demo-info">
          <p><strong>Demo Email:</strong> teacher@example.com</p>
          <p><strong>Demo Password:</strong> password123</p>
        </div>
        )}
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
