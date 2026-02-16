import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, LogOut, Eye, EyeOff, ArrowRight, Volume2, VolumeX, Megaphone, Phone } from 'lucide-react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import './StudentView.css';

const StudentView = () => {
  const navigate = useNavigate();
  const lastSpokenTextRef = useRef('');

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loginForm, setLoginForm] = useState({ userId: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [studentData, setStudentData] = useState(null);

  const [selectedLanguage, setSelectedLanguage] = useState('bodo');
  const [languageSelected, setLanguageSelected] = useState(false); // ← NEW: Track if language was selected
  const [englishSubtitle, setEnglishSubtitle] = useState('');
  const [translatedSubtitle, setTranslatedSubtitle] = useState('');
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false); // ← NEW: Track speaking status

  const [joinCodeInput, setJoinCodeInput] = useState('');
  const [joinError, setJoinError] = useState('');
  const [joinedByCode, setJoinedByCode] = useState(false);
  const [currentJoinCode, setCurrentJoinCode] = useState('');
  const [classEnded, setClassEnded] = useState(false); // ← NEW: Track if class ended
  const [classEndedMessage, setClassEndedMessage] = useState(''); // ← NEW: Store class ended message
  const noContentCountRef = useRef(0); // ← NEW: Track consecutive 404s

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

      console.log('Login Success:', response.data);

      if (response.data.success) {
        // Extract user data - backend returns: { success, message, userId, name, role, token }
        const userData = {
          userId: response.data.userId,
          name: response.data.name || response.data.userId,  // Fallback to userId if name not provided
          role: response.data.role || 'student',
          token: response.data.token,
          preferredLanguage: response.data.preferredLanguage
        };
        
        console.log('📊 Student Data:', userData);
        
        setStudentData(userData);
        setIsLoggedIn(true);

        localStorage.setItem('studentSession', JSON.stringify(userData));
        localStorage.setItem('userRole', userData.role);
        localStorage.setItem('token', userData.token);

        if (userData.preferredLanguage) {
          setSelectedLanguage(userData.preferredLanguage.toLowerCase());
        }
      } else {
        setLoginError('Invalid credentials');
      }
    } catch (error) {
      console.error('Login Error Details:');
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
      navigate('/');
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
      } else {
        setJoinError(res.data.message || 'Join failed');
      }
    } catch {
      setJoinError('Invalid or expired join code');
    }
  };

  // =========================
  // LISTEN FOR TEACHER BROADCASTS + AUTO SPEECH
  // =========================
  useEffect(() => {
    if (!joinedByCode || !currentJoinCode) return;

    let noContentCounter = 0;
    const joinTime = Date.now(); // Track when student joined
    const GRACE_PERIOD = 15000; // First 15 seconds: 404 is normal (no broadcast yet)
    const DISCONNECT_THRESHOLD = 10; // After grace period: need 10 consecutive 404s to disconnect

    const pollInterval = setInterval(async () => {
      try {
        const res = await axios.get(
          `${API_BASE_URL}/api/student/get-broadcast/${currentJoinCode}`,
          {
            timeout: 5000
          }
        );

        // Any successful response = reset disconnect counter
        noContentCounter = 0;

        if (res.data.success && res.data.content) {
          const englishText = res.data.content.englishText || '';
          
          // Get translation based on SELECTED LANGUAGE ONLY
          const translation = selectedLanguage === 'mizo' 
            ? res.data.content.mizoTranslation 
            : res.data.content.bodoTranslation;
          
          setEnglishSubtitle(englishText);
          setTranslatedSubtitle(translation || '— (not found in dataset)');
          
          console.log(`[${selectedLanguage.toUpperCase()}] Received:`, translation);
          
          // AUTO-SPEAK: Only if text changed and audio enabled
          if (translation && translation !== lastSpokenTextRef.current && audioEnabled && !isSpeaking) {
            lastSpokenTextRef.current = translation;
            setIsSpeaking(true);
            
            if ('speechSynthesis' in window) {
              window.speechSynthesis.cancel(); // Cancel any previous speech
              
              const utterance = new SpeechSynthesisUtterance(translation);
              
              // Set voice language based on selected language
              if (selectedLanguage === 'bodo') {
                utterance.lang = 'hi-IN'; // Hindi for Bodo approximation
                utterance.rate = 0.9;
              } else {
                utterance.lang = 'en-US'; // English for Mizo approximation
                utterance.rate = 0.85;
              }
              
              utterance.onend = () => setIsSpeaking(false);
              utterance.onerror = () => setIsSpeaking(false);
              
              window.speechSynthesis.speak(utterance);
            }
          }
        }
      } catch (err) {
        // Only 404 errors count as potential class-end (broadcast was deleted)
        if (err.response?.status === 404) {
          const elapsedTime = Date.now() - joinTime;
          
          // During grace period: ignore 404s (class just started, no broadcast yet)
          if (elapsedTime < GRACE_PERIOD) {
            console.debug('No broadcast yet (class just started)');
            noContentCounter = 0; // Reset counter during grace period
          } else {
            // After grace period: count consecutive 404s
            noContentCounter++;
            
            // Disconnect only after sustained 404s beyond grace period
            if (noContentCounter >= DISCONNECT_THRESHOLD) {
              console.log('Class stopped by teacher - disconnecting');
              setClassEndedMessage('Teacher has ended the class');
              setClassEnded(true);
              setJoinedByCode(false);
              setIsConnected(false);
              window.speechSynthesis.cancel(); // Stop any ongoing speech
              clearInterval(pollInterval);
            }
          }
        } else {
          // For other errors (network, timeout), don't count toward disconnect
          if (err.code !== 'ECONNABORTED') {
            console.debug('Polling error:', err.message);
          }
          // Don't increment counter for non-404 errors
        }
      }
    }, 1000);

    return () => {
      clearInterval(pollInterval);
      noContentCountRef.current = 0;
    };
  }, [joinedByCode, currentJoinCode, selectedLanguage, audioEnabled, isSpeaking]);

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
              <div className="form-group">
                <label>Roll Number</label>
                <input
                  type="text"
                  placeholder="23B21A4501"
                  value={loginForm.userId}
                  onChange={(e) => setLoginForm({ ...loginForm, userId: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Password</label>
                <div className="password-input-wrapper">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter password"
                    value={loginForm.password}
                    onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                    required
                  />
                  <button 
                    type="button" 
                    className="btn-toggle-password"
                    onClick={() => setShowPassword(!showPassword)}
                    title={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              {loginError && <div className="error-message">{loginError}</div>}

              <button type="submit" className="btn btn-login-primary">
                <ArrowRight size={20} />
                Login
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
            <div className="top-bar-content">
              <button className="btn-icon" onClick={() => navigate('/')} title="Home">
                <Home size={24} />
              </button>

              <div className="student-info">
                <span className="student-name">{studentData?.name || 'Student'}</span>
                <span className="student-id">{studentData?.userId}</span>
              </div>

              <div className="connection-status">
                <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
                <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
              </div>

              <button className="btn-icon" onClick={handleLogout} title="Logout">
                <LogOut size={24} />
              </button>
            </div>
          </div>

          <div className="subtitle-container">
            {classEndedMessage && (
              <div className="class-ended-message">
                <p>🛑 {classEndedMessage}</p>
              </div>
            )}
            {isConnected && !classEndedMessage ? (
              <div className="subtitle-box">
                {englishSubtitle ? (
                  <>
                    <div className="subtitle-english">
                      <p><strong>English:</strong> {englishSubtitle}</p>
                    </div>
                    <div className="translation-column">
                      <div className="translation-label">
                        <span className="language-badge" style={{
                          background: selectedLanguage === 'bodo' ? '#4f46e5' : '#9333ea'
                        }}>
                          {selectedLanguage.toUpperCase()}
                        </span>
                      </div>
                      <div className="translation-text">
                        {translatedSubtitle && translatedSubtitle !== '— (not found in dataset)' ? (
                          <p>{translatedSubtitle}</p>
                        ) : (
                          <p className="placeholder">{translatedSubtitle}</p>
                        )}
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="waiting-message">
                    <p className="waiting-title">⏳ Waiting for teacher</p>
                    <p className="waiting-subtitle">Teacher will start sharing content soon...</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="no-subtitles">
                <p>Connect to classroom to see subtitles</p>
              </div>
            )}
          </div>

          <div className="join-class-section card">
            <h3>Join Class</h3>
            
            {!languageSelected ? (
              <>
                <p style={{ marginBottom: '20px', color: '#666' }}>
                  Select your preferred translation language:
                </p>
                <div className="language-selection">
                  <button
                    className={`language-btn ${selectedLanguage === 'bodo' ? 'active' : ''}`}
                    onClick={() => {
                      setSelectedLanguage('bodo');
                      setLanguageSelected(true);
                    }}
                  >
                    Bodo
                  </button>
                  <button
                    className={`language-btn ${selectedLanguage === 'mizo' ? 'active' : ''}`}
                    onClick={() => {
                      setSelectedLanguage('mizo');
                      setLanguageSelected(true);
                    }}
                  >
                    Mizo
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="language-info">
                  <p><Megaphone size={18} style={{display: 'inline-block', marginRight: '8px', verticalAlign: 'middle'}} /> Language: <strong>{selectedLanguage.toUpperCase()}</strong></p>
                  <button 
                    className="btn-text"
                    onClick={() => setLanguageSelected(false)}
                    style={{ fontSize: '12px', marginTop: '8px' }}
                  >
                    Change Language
                  </button>
                </div>
                
                <div className="form-group" style={{ marginTop: '15px' }}>
                  <label>Enter join code:</label>
                  <input
                    type="text"
                    placeholder="e.g., GOOG1234"
                    value={joinCodeInput}
                    onChange={(e) => setJoinCodeInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleJoinByCode()}
                  />
                  <button className="btn btn-primary" onClick={handleJoinByCode}>
                    Join Class
                  </button>
                </div>
                {joinError && <div className="error-message">{joinError}</div>}
              </>
            )}
          </div>

          {isConnected && (
            <div className="audio-control card">
              <button 
                className={`btn btn-audio ${audioEnabled ? 'enabled' : 'disabled'}`}
                onClick={() => setAudioEnabled(!audioEnabled)}
              >
                {audioEnabled ? (
                  <>
                    <Volume2 size={20} />
                    Audio ON
                  </>
                ) : (
                  <>
                    <VolumeX size={20} />
                    Audio OFF
                  </>
                )}
              </button>
              {isSpeaking && <span style={{ marginLeft: '10px', color: '#4CAF50', display: 'flex', alignItems: 'center', gap: '6px' }}><Volume2 size={16} /> Speaking...</span>}
            </div>
          )}

          {/* CLASS ENDED MODAL */}
          {classEnded && (
            <div className="modal-overlay">
              <div className="modal-content">
                <div className="modal-icon"><Phone size={64} style={{color: '#ef4444'}} /></div>
                <h2 className="modal-title">Teacher has ended the class</h2>
                <p className="modal-message">The class session has been closed by your teacher. Please wait for the next class or contact your teacher.</p>
                <button 
                  className="btn btn-primary"
                  onClick={() => {
                    setClassEnded(false);
                    setClassEndedMessage('');
                    setLanguageSelected(false);
                    setJoinCodeInput('');
                    setEnglishSubtitle('');
                    setTranslatedSubtitle('');
                  }}
                >
                  Return to Join
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default StudentView;
