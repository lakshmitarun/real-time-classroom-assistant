import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Mail, Lock, LogIn, User, Globe, BookOpen, Shield } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';
import API_BASE_URL from '../config/api';
import './LoginPage.css';

const LoginPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const userType = searchParams.get('type') || 'teacher'; // Get type from URL query param
  
  const [isLogin, setIsLogin] = useState(true); // Toggle between login and register
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

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

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Authentication failed');
        setLoading(false);
        return;
      }

      if (isLogin) {
        // Login successful - redirect based on role
        const role = data.role || 'teacher'; // Default to teacher for backward compatibility
        
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
      const credential = credentialResponse?.credential;
      if (!credential) {
        setError('Google sign-in failed: no credential returned');
        setLoading(false);
        return;
      }

      // Send the raw ID token (credential) to the backend for verification
      const res = await fetch(`${API_BASE_URL}/api/auth/google/callback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential })
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || 'Google login failed');
        setLoading(false);
        return;
      }

      // Successful login - redirect based on role
      const role = data.role || 'teacher'; // Default to teacher
      
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
                  type="password"
                  id="password"
                  name="password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleInputChange}
                  disabled={loading}
                  required
                />
              </div>
            </div>

            {/* Confirm Password (Register Only) */}
            {!isLogin && (
              <div className="form-group">
                <label htmlFor="confirmPassword">Confirm Password</label>
                <div className="input-group">
                  <Lock size={18} />
                  <input
                    type="password"
                    id="confirmPassword"
                    name="confirmPassword"
                    placeholder="Confirm your password"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    disabled={loading}
                    required
                  />
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
