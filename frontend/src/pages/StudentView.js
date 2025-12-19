import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, Volume2, VolumeX, LogIn } from 'lucide-react';
import axios from 'axios';
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

    try {
      const response = await axios.post('http://localhost:5000/api/student/login', {
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
      } else {
        setLoginError('Login failed. Please make sure the backend server is running.');
      }
    }
  };

  const handleLogout = async () => {
    try {
      if (studentData?.userId) {
        await axios.post('http://localhost:5000/api/logout', {
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

  // Simulate receiving subtitles
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
    } else if (isConnected && joinedByCode) {
      // Joined by code - wait for real teacher input
      setEnglishSubtitle('Waiting for teacher to speak...');
      setTranslatedSubtitle('शिक्षक के बोलने का इंतजार कर रहे हैं...');
    }
  }, [isConnected, joinedByCode, selectedLanguage, audioEnabled]);

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
      const resp = await axios.post('http://localhost:5000/api/student/join', {
        studentId: studentId.trim(),
        joinCode: joinCodeInput.trim().toUpperCase()
      });

      if (resp.data && resp.data.success) {
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

  const speakText = (text) => {
    if (audioEnabled && 'speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = selectedLanguage === 'bodo' ? 'hi-IN' : 'en-US';
      window.speechSynthesis.speak(utterance);
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
