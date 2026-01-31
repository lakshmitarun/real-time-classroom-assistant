import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, LogIn, Eye, EyeOff } from 'lucide-react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import './StudentView.css';

const StudentView = () => {
  const navigate = useNavigate();

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loginForm, setLoginForm] = useState({ userId: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [studentData, setStudentData] = useState(null);

  const [selectedLanguage, setSelectedLanguage] = useState('bodo'); // eslint-disable-line no-unused-vars
  const [englishSubtitle, setEnglishSubtitle] = useState(''); // eslint-disable-line no-unused-vars
  const [translatedSubtitle, setTranslatedSubtitle] = useState(''); // eslint-disable-line no-unused-vars
  const [audioEnabled, setAudioEnabled] = useState(true); // eslint-disable-line no-unused-vars
  const [isConnected, setIsConnected] = useState(false);

  const [joinCodeInput, setJoinCodeInput] = useState('');
  const [joinError, setJoinError] = useState('');
  const [joinedByCode, setJoinedByCode] = useState(false); // eslint-disable-line no-unused-vars
  const [currentJoinCode, setCurrentJoinCode] = useState(''); // eslint-disable-line no-unused-vars
  const [lastContentTimestamp, setLastContentTimestamp] = useState(''); // eslint-disable-line no-unused-vars

  // =========================
  // RESTORE SESSION
  // =========================
  useEffect(() => {
    const savedSession = localStorage.getItem('studentSession');
    if (savedSession) {
      try {
        const data = JSON.parse(savedSession);
        setStudentData(data);
        setIsLoggedIn(true);
        if (data.preferredLanguage) {
          setSelectedLanguage(data.preferredLanguage.toLowerCase());
        }
      } catch {
        localStorage.removeItem('studentSession');
      }
    }
  }, []);

  // =========================
  // LOGIN
  // =========================
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    console.log('🔐 Login Attempt:');
    console.log('  - API URL:', API_BASE_URL);
    console.log('  - User ID:', loginForm.userId.trim());

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/student/login`,
        {
          userId: loginForm.userId.trim(),
          password: loginForm.password.trim()
        },
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: 10000 // 10 second timeout
        }
      );

      console.log('✅ Login Success:', response.data);

      if (response.data.success) {
        const userData = response.data.user || response.data;
        setStudentData(userData);
        setIsLoggedIn(true);

        localStorage.setItem('studentSession', JSON.stringify(userData));
        localStorage.setItem('userRole', userData.role || 'student');

        if (userData.preferredLanguage) {
          setSelectedLanguage(userData.preferredLanguage.toLowerCase());
        }
      } else {
        setLoginError('Invalid credentials');
      }
    } catch (error) {
      console.error('❌ Login Error Details:');
      console.error('  - Message:', error.message);
      console.error('  - Status:', error.response?.status);
      console.error('  - Data:', error.response?.data);
      console.error('  - Config URL:', error.config?.url);
      
      if (error.response?.status === 401) {
        setLoginError('Invalid user ID or password');
      } else if (error.response?.status === 404) {
        setLoginError('Backend server not found. Check API URL: ' + API_BASE_URL);
      } else if (error.code === 'ECONNABORTED') {
        setLoginError('Request timeout - backend is slow or unreachable');
      } else if (error.message === 'Network Error') {
        setLoginError('Network error - check if backend is running at: ' + API_BASE_URL);
      } else {
        setLoginError('Backend not reachable. Error: ' + error.message);
      }
    }
  };

  // =========================
  // LOGOUT
  // =========================
  const handleLogout = async () => {
    try {
      if (studentData?.userId) {
        await axios.post(`${API_BASE_URL}/api/logout`, {
          userId: studentData.userId
        });
      }
    } catch (e) {
      console.error(e);
    } finally {
      localStorage.removeItem('studentSession');
      localStorage.removeItem('userRole');
      setIsLoggedIn(false);
      setStudentData(null);
      setIsConnected(false);
    }
  };

  // =========================
  // TEXT TO SPEECH
  // =========================
  // eslint-disable-next-line no-unused-vars
  const speakText = (text) => {
    if (!audioEnabled || !('speechSynthesis' in window)) return;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);

    if (selectedLanguage === 'bodo') {
      utterance.lang = 'hi-IN';
      utterance.rate = 0.9;
    } else {
      utterance.lang = 'en-US';
      utterance.rate = 0.85;
    }

    window.speechSynthesis.speak(utterance);
  };

  // =========================
  // JOIN BY CODE
  // =========================
  const handleJoinByCode = async () => {
    setJoinError('');
    if (!studentData?.userId) return setJoinError('Please login first');
    if (!joinCodeInput.trim()) return setJoinError('Enter join code');

    try {
      const joinCode = joinCodeInput.trim().toUpperCase();
      const res = await axios.post(`${API_BASE_URL}/api/student/join`, {
        studentId: studentData.userId,
        joinCode
      });

      if (res.data.success) {
        setCurrentJoinCode(joinCode);
        setJoinedByCode(true);
        setIsConnected(true);
        setJoinCodeInput('');
        setLastContentTimestamp('');
      } else {
        setJoinError(res.data.message || 'Join failed');
      }
    } catch {
      setJoinError('Invalid or expired join code');
    }
  };

  // =========================
  // UI
  // =========================
  return (
    <div className="student-view">
      {!isLoggedIn ? (
        <div className="login-container">
          <div className="login-box card">
            <h2>Student Login</h2>

            <form onSubmit={handleLogin}>
              <input
                type="text"
                placeholder="Roll Number"
                value={loginForm.userId}
                onChange={(e) => setLoginForm({ ...loginForm, userId: e.target.value })}
                required
              />

              <div className="password-input-wrapper">
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Password"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  required
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)}>
                  {showPassword ? <EyeOff /> : <Eye />}
                </button>
              </div>

              {loginError && <div className="error-message">{loginError}</div>}

              <button type="submit" className="btn btn-login-primary">
                <LogIn /> Login
              </button>
            </form>

            <button className="btn-text" onClick={() => navigate('/')}>
              Back to Home
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="top-bar">
            <button onClick={() => navigate('/')}>
              <Home />
            </button>

            <div>{studentData?.userId}</div>

            <button onClick={handleLogout}>Logout</button>
          </div>

          <div className="subtitle-container">
            {isConnected ? (
              <p>Connected successfully 🎉</p>
            ) : (
              <p>Connect to classroom</p>
            )}
          </div>

          <div className="join-class-section card">
            <input
              type="text"
              placeholder="Enter join code"
              value={joinCodeInput}
              onChange={(e) => setJoinCodeInput(e.target.value)}
            />
            <button className="btn btn-primary" onClick={handleJoinByCode}>
              Join
            </button>
            {joinError && <div className="error-message">{joinError}</div>}
          </div>
        </>
      )}
    </div>
  );
};

export default StudentView;
