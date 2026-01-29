import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, Volume2, VolumeX, LogIn } from 'lucide-react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import './StudentView.css';

const StudentView = () => {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loginForm, setLoginForm] = useState({ userId: '', password: '' });
  const [loginError, setLoginError] = useState('');
  const [studentData, setStudentData] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('bodo');
  const [englishSubtitle, setEnglishSubtitle] = useState('');
  const [translatedSubtitle, setTranslatedSubtitle] = useState('');
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [joinCodeInput, setJoinCodeInput] = useState('');
  const [joinError, setJoinError] = useState('');
  const [joinedByCode, setJoinedByCode] = useState(false);
  const [currentJoinCode, setCurrentJoinCode] = useState('');
  const [lastContentTimestamp, setLastContentTimestamp] = useState('');

  // Check for saved session on component mount
  useEffect(() => {
    const savedSession = localStorage.getItem('studentSession');
    if (savedSession) {
      try {
        const sessionData = JSON.parse(savedSession);
        setStudentData(sessionData);
        setIsLoggedIn(true);
        if (sessionData.preferredLanguage) {
          setSelectedLanguage(sessionData.preferredLanguage.toLowerCase());
        }
      } catch (error) {
        console.error('Failed to restore session:', error);
        localStorage.removeItem('studentSession');
      }
    }
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    console.log('Login attempt with API URL:', API_BASE_URL);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/student/login`, {
        userId: loginForm.userId.trim(),
        password: loginForm.password.trim()
      });

      if (response.data.success) {
        const userData = response.data.user;
        setStudentData(userData);
        setIsLoggedIn(true);
        
        // Save session and role to localStorage
        localStorage.setItem('studentSession', JSON.stringify(userData));
        localStorage.setItem('userRole', userData.role || 'student');
        
        // Set preferred language if available
        if (userData.preferredLanguage) {
          setSelectedLanguage(userData.preferredLanguage.toLowerCase());
        }
      }
    } catch (error) {
      console.error('Login error:', error);
      if (error.response && error.response.data) {
        setLoginError(error.response.data.message || 'Invalid user ID or password');
      } else if (error.response && error.response.status === 404) {
        setLoginError('Backend server not found. Please check if the server is running.');
      } else if (error.message && error.message.includes('CORS')) {
        setLoginError('CORS error: Backend server is not accepting requests from this domain.');
      } else if (error.request && !error.response) {
        setLoginError('Could not reach the backend server. Please check if the server is running.');
      } else {
        setLoginError('Login failed. Please make sure the backend server is running.');
      }
    }
  };

  const handleLogout = async () => {
    try {
      if (studentData?.userId) {
        await axios.post(`${API_BASE_URL}/api/logout`, {
          userId: studentData.userId
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear session from localStorage
      localStorage.removeItem('studentSession');
      
      setIsLoggedIn(false);
      setStudentData(null);
      setLoginForm({ userId: '', password: '' });
      setIsConnected(false);
      localStorage.removeItem('userRole');
    }
  };

    // eslint-disable-next-line react-hooks/exhaustive-deps
  const speakText = (text) => {
    if (audioEnabled && 'speechSynthesis' in window) {
      // Stop any ongoing speech first
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Set language based on selected language
      if (selectedLanguage === 'bodo') {
        utterance.lang = 'hi-IN'; // Use Hindi for Bodo (closest match)
        utterance.rate = 0.9; // Slightly slower for clarity
      } else {
        utterance.lang = 'en-US'; // Use English for Mizo (closest match)
        utterance.rate = 0.85; // Slower for clarity
      }
      
      utterance.volume = 1;
      utterance.pitch = 1;
      
      console.log(`🔊 Speaking ${selectedLanguage}: "${text}"`);
      window.speechSynthesis.speak(utterance);
    }
  };

  // Simulate receiving subtitles or poll for real content
  useEffect(() => {
    if (isConnected && !joinedByCode) {
      // Only show demo subtitles if manually connected (not joined by code)
      const demoSubtitles = [
        { en: 'Good morning class', bodo: 'सुबुं बिहान', mizo: 'Zing tlâm ṭha class' },
        { en: 'Today we will learn Mathematics', bodo: 'दिनै बे सान्न्रि होननाय गोनां', mizo: 'Tunah Mathematics kan zir dawn' },
        { en: 'Please open your books', bodo: 'अननानै नायनि किताबखौ खेव', mizo: 'I lehkhabu hung hawng rawh' },
        { en: 'Do you understand?', bodo: 'नों गोजौ खायला?', mizo: 'I hrethiam em?' }
      ];

      let index = 0;
      const interval = setInterval(() => {
        const subtitle = demoSubtitles[index % demoSubtitles.length];
        setEnglishSubtitle(subtitle.en);
        const translation = selectedLanguage === 'bodo' ? subtitle.bodo : subtitle.mizo;
        setTranslatedSubtitle(translation);
        
        // Auto-speak if audio is enabled
        if (audioEnabled) {
          speakText(translation);
        }
        
        index++;
      }, 4000);

      return () => clearInterval(interval);
    } else if (isConnected && joinedByCode && currentJoinCode) {
      // Joined by code - poll for real teacher input AND check if class is still active
      console.log('📡 Polling for teacher content...');
      
      const pollContent = async () => {
        try {
          // First check if class is still active
          const classCheckRes = await axios.get(`${API_BASE_URL}/api/student/check-class-active`, {
            params: { joinCode: currentJoinCode }
          });
          
          if (!classCheckRes.data.isActive) {
            // Class was stopped by teacher - auto-disconnect
            console.log('🔴 Class stopped by teacher. Disconnecting...');
            setIsConnected(false);
            setJoinedByCode(false);
            setEnglishSubtitle('Class ended by teacher');
            setTranslatedSubtitle('शिक्षक द्वारा कक्षा समाप्त / Zirtir lal sawn');
            return;
          }
          
          const response = await axios.get(`${API_BASE_URL}/api/student/get-content`, {
            params: { joinCode: currentJoinCode }
          });
          
          if (response.data.success && response.data.content) {
            const content = response.data.content;
            
            // Only update if there's new content (different timestamp)
            if (content.timestamp && content.timestamp !== lastContentTimestamp) {
              setEnglishSubtitle(content.englishText || 'Waiting for teacher to speak...');
              
              const translation = selectedLanguage === 'bodo' 
                ? content.bodoTranslation 
                : content.mizoTranslation;
              setTranslatedSubtitle(translation || 'Waiting for teacher to speak...');
              
              // Auto-speak if audio is enabled and there's content
              if (audioEnabled && translation) {
                speakText(translation);
              }
              
              setLastContentTimestamp(content.timestamp);
            } else if (!lastContentTimestamp) {
              // First load
              setEnglishSubtitle(content.englishText || 'Waiting for teacher to speak...');
              const translation = selectedLanguage === 'bodo' 
                ? content.bodoTranslation 
                : content.mizoTranslation;
              setTranslatedSubtitle(translation || 'Waiting for teacher to speak...');
              if (lastContentTimestamp === '') {
                setLastContentTimestamp(content.timestamp || 'init');
              }
            }
          }
        } catch (error) {
          console.error('Error polling content:', error);
        }
      };
      
      // Poll every 500ms for new content
      const interval = setInterval(pollContent, 500);
      
      // Also fetch immediately
      pollContent();
      
      return () => clearInterval(interval);
    }
  }, [isConnected, joinedByCode, currentJoinCode, selectedLanguage, audioEnabled, lastContentTimestamp, speakText]);

  const toggleConnection = () => {
    setIsConnected(!isConnected);
    setJoinedByCode(false);
    if (!isConnected) {
      setEnglishSubtitle('');
      setTranslatedSubtitle('');
    }
  };

  const handleJoinByCode = async () => {
    setJoinError('');
    const studentId = studentData?.userId;
    if (!studentId) {
      setJoinError('Please login first.');
      return;
    }
    if (!joinCodeInput || joinCodeInput.trim().length === 0) {
      setJoinError('Enter a join code');
      return;
    }

    try {
      const joinCode = joinCodeInput.trim().toUpperCase();
      const resp = await axios.post(`${API_BASE_URL}/api/student/join`, {
        studentId: studentId.trim(),
        joinCode: joinCode
      });

      if (resp.data && resp.data.success) {
        console.log('✅ Joined class with code:', joinCode);
        setCurrentJoinCode(joinCode);
        setLastContentTimestamp('');
        setJoinCodeInput('');
        setJoinError('');
        setJoinedByCode(true);
        setIsConnected(true);
      } else {
        setJoinError((resp.data && resp.data.message) || 'Failed to join');
        setIsConnected(false);
      }
    } catch (err) {
      console.error('Join error', err);
      setJoinError('Invalid or expired join code. Please check with your teacher.');
      setIsConnected(false);
    }
  };

  return (
    <div className="student-view">
      {!isLoggedIn ? (
        // Login Screen
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
                <input
                  type="password"
                  placeholder="Enter password"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  required
                />
              </div>
              {loginError && <div className="error-message">{loginError}</div>}
              <button type="submit" className="btn btn-login-primary">
                <LogIn size={20} />
                Login
              </button>
            </form>
            <button className="btn-text" onClick={() => navigate('/')}>
              Back to Home
            </button>
          </div>
        </div>
      ) : (
        // Main Student View
        <>
          {/* Top Bar */}
          <div className="top-bar">
            <div className="container">
              <div className="top-bar-content">
                <button className="btn-icon" onClick={() => navigate('/')}>
                  <Home size={24} />
                </button>
                
                <div className="student-info">
                  <span className="student-name">{studentData?.name}</span>
                  <span className="student-id">{studentData?.userId}</span>
                </div>
                
                <div className="connection-status">
                  <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
                  <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
                </div>

                <button 
                  className="btn-icon"
                  onClick={() => setAudioEnabled(!audioEnabled)}
                >
                  {audioEnabled ? <Volume2 size={24} /> : <VolumeX size={24} />}
                </button>
                
                <button className="btn-text" onClick={handleLogout}>
                  Logout
                </button>
              </div>
            </div>
          </div>

      {/* Main Subtitle Area */}
      <div className="subtitle-container">
        {isConnected && (englishSubtitle || translatedSubtitle) ? (
          <div className="subtitle-box fade-in">
            <div className="subtitle-line english">
              {englishSubtitle}
            </div>
            <div className="subtitle-line translated">
              <span className={`lang-indicator ${selectedLanguage}`}>
                {selectedLanguage.toUpperCase()}
              </span>
              {translatedSubtitle}
            </div>
          </div>
        ) : (
          <div className="no-subtitles">
            <p>
              {isConnected 
                ? 'Waiting for teacher to start...' 
                : 'Connect to classroom to see subtitles'}
            </p>
          </div>
        )}
      </div>

      {/* Language Switcher */}
      <div className="language-switcher">
        <div className="switcher-container">
          <button
            className={`lang-btn ${selectedLanguage === 'bodo' ? 'active' : ''}`}
            onClick={() => setSelectedLanguage('bodo')}
          >
            Bodo (बड़ो)
          </button>
          <button
            className={`lang-btn ${selectedLanguage === 'mizo' ? 'active' : ''}`}
            onClick={() => setSelectedLanguage('mizo')}
          >
            Mizo
          </button>
        </div>
      </div>

      {/* Control Buttons */}
      <div className="control-panel">
        <button 
          className={`btn ${isConnected ? 'btn-danger' : 'btn-success'} btn-large`}
          onClick={toggleConnection}
          disabled={joinError ? true : false}
          title={joinError ? 'Clear the error and try joining by code again' : ''}
        >
          {isConnected ? 'Disconnect' : 'Connect to Classroom'}
        </button>
        
        <button 
          className={`btn ${audioEnabled ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setAudioEnabled(!audioEnabled)}
        >
          {audioEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
          {audioEnabled ? 'Audio ON (Auto-speaking)' : 'Audio OFF'}
        </button>
      </div>

      {/* Join Class by Code */}
      <div className="join-class-section card">
        <h3>Join Class</h3>
        <p>Enter the join code shared by your teacher to join the class.</p>
        <div className="form-group">
          <input
            type="text"
            placeholder="Enter join code"
            value={joinCodeInput}
            onChange={(e) => setJoinCodeInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleJoinByCode()}
          />
          <button className="btn btn-primary" onClick={handleJoinByCode}>
            Join
          </button>
        </div>
        {joinError && <div className="error-message">{joinError}</div>}
      </div>

          {/* Instructions */}
          {!isConnected && (
            <div className="instructions card">
              <h3>How to use:</h3>
              <ol>
                <li>Click "Connect to Classroom" to join the live session</li>
                <li>Switch between Bodo and Mizo using the language buttons</li>
                <li>Enable audio to hear the translations</li>
                <li>Subtitles will appear automatically when the teacher speaks</li>
              </ol>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default StudentView;
