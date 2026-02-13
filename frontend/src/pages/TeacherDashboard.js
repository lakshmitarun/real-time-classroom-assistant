import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mic, MicOff, Download, Home, Play, Square, LogOut } from 'lucide-react';
import { safeFetch } from '../utils/apiClient';
import './TeacherDashboard.css';

const TeacherDashboard = () => {
  const navigate = useNavigate();
  const [isListening, setIsListening] = useState(false);
  const [englishText, setEnglishText] = useState('');
  const [bodoTranslation, setBodoTranslation] = useState('');
  const [mizoTranslation, setMizoTranslation] = useState('');
  const [latency, setLatency] = useState('0.0');
  const [classActive, setClassActive] = useState(false);
  const [recognitionInterval, setRecognitionInterval] = useState(null);
  const [joinCode, setJoinCode] = useState('');
  const [joinMessage, setJoinMessage] = useState('');
  const [teacherInfo, setTeacherInfo] = useState({ name: '', email: '' });

  // Auth check: redirect to login if no token
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    
    // Retrieve teacher info from localStorage
    const teacherData = localStorage.getItem('teacher');
    if (teacherData) {
      try {
        const teacher = JSON.parse(teacherData);
        setTeacherInfo({
          name: teacher.name || '',
          email: teacher.email || ''
        });
      } catch (e) {
        console.error('Failed to parse teacher data:', e);
      }
    }
  }, [navigate]);

  // Simulated real-time speech recognition
  useEffect(() => {
    let interval;
    if (isListening) {
      interval = setInterval(() => {
        setLatency((Math.random() * 2 + 1).toFixed(1));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isListening]);

  const startClass = async () => {
    try {
      const token = localStorage.getItem('token');
      const teacherData = localStorage.getItem('teacher');
      const teacher = teacherData ? JSON.parse(teacherData) : null;
      const teacherId = teacher?.id;
      
      console.log('🎓 Starting class...');
      console.log('Token available:', !!token);
      console.log('Teacher ID:', teacherId);
      
      if (!teacherId) {
        alert('Teacher ID not found. Please login again.');
        return;
      }
      
      // ✅ Use safeFetch with proper error handling
      const result = await safeFetch('/api/teacher/start-class', {
        method: 'POST',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        body: JSON.stringify({ teacherId })
      });
      
      if (!result.ok) {
        console.error('❌ Failed to start class:', result.error);
        alert(`Failed to start class: ${result.error}`);
        return;
      }
      
      const data = result.data;
      
      if (data.success || data.joinCode) {
        setJoinCode(data.joinCode || '');
        setJoinMessage('Share this code with students');
        console.log('✅ Class started with code:', data.joinCode);
      } else {
        console.error('❌ Failed to start class:', data.message);
        alert(`Failed to start class: ${data.message}`);
        return;
      }
    } catch (err) {
      console.error('❌ Error starting class:', err);
      alert(`Error: ${err.message}`);
      return;
    }
    
    setClassActive(true);
    setIsListening(true);
    setEnglishText('');
    setBodoTranslation('');
    setMizoTranslation('');
  };

  const stopClass = async () => {
    try {
      const token = localStorage.getItem('token');
      console.log('🛑 Stopping class...');
      if (joinCode) {
        // ✅ Use safeFetch with proper error handling
        const result = await safeFetch('/api/teacher/stop-class', {
          method: 'POST',
          headers: token ? { 'Authorization': `Bearer ${token}` } : {},
          body: JSON.stringify({ joinCode })
        });
        console.log('Stop class response:', result);
      }
    } catch (err) {
      console.error('❌ Error stopping class:', err);
    }
    setClassActive(false);
    setIsListening(false);
    setJoinCode('');
    setJoinMessage('');
    if (recognitionInterval) {
      clearInterval(recognitionInterval);
      setRecognitionInterval(null);
    }
  };

  const handleSpeechInput = (text) => {
    setEnglishText(text);
    if (text.trim()) {
      translateText(text);
    } else {
      setBodoTranslation('');
      setMizoTranslation('');
    }
  };

  // Broadcast speech to students
  const broadcastToStudents = async (english, bodo, mizo) => {
    if (!joinCode || !english.trim()) return;
    
    try {
      // ✅ Use safeFetch with proper error handling
      const result = await safeFetch('/api/teacher/broadcast-speech', {
        method: 'POST',
        body: JSON.stringify({
          joinCode: joinCode,
          englishText: english,
          bodoTranslation: bodo,
          mizoTranslation: mizo
        })
      });
      
      if (result.ok) {
        console.log('✅ Broadcast sent to students');
      } else {
        console.log('⚠️ Broadcast failed:', result.error);
      }
    } catch (error) {
      console.error('❌ Broadcast error:', error);
    }
  };

  const translateText = async (text) => {
    if (!text) {
      setBodoTranslation('');
      setMizoTranslation('');
      return;
    }
    
    try {
      console.log('🔤 Translating text:', text);
      const startTime = performance.now();
      
      // ✅ Use safeFetch with proper error handling
      const result = await safeFetch('/api/translate/batch', {
        method: 'POST',
        body: JSON.stringify({
          texts: [text.trim()]
        })
      });
      
      const endTime = performance.now();
      const responseTime = ((endTime - startTime) / 1000).toFixed(1);
      setLatency(responseTime);
      
      if (!result.ok) {
        console.error('Translation failed:', result.error);
        setBodoTranslation('');
        setMizoTranslation('');
        return;
      }
      
      const data = result.data;
      console.log('Translation response:', data);
      
      let bodo = '';
      let mizo = '';
      
      if (data.translations && data.translations.length > 0) {
        const firstTranslation = data.translations[0];
        bodo = firstTranslation.bodoTranslation || '— (not found in dataset)';
        mizo = firstTranslation.mizoTranslation || '— (not found in dataset)';
        setBodoTranslation(bodo);
        setMizoTranslation(mizo);
      } else {
        setBodoTranslation('— (not found in dataset)');
        setMizoTranslation('— (not found in dataset)');
      }
      
      // Broadcast to students
      if (classActive && joinCode) {
        broadcastToStudents(text, bodo, mizo);
      }
    } catch (error) {
      console.error('❌ Translation error:', error);
      setBodoTranslation('— (backend error)');
      setMizoTranslation('— (backend error)');
    }
  };

  const downloadSummary = () => {
    const summary = `
Class Summary
=============
English Text: ${englishText}
Bodo Translation: ${bodoTranslation}
Mizo Translation: ${mizoTranslation}
    `;
    
    const blob = new Blob([summary], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `class-summary-${new Date().toISOString()}.txt`;
    a.click();
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('teacher');
    localStorage.removeItem('userRole');
    navigate('/');
  };

  return (
    <div className="teacher-dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="container">
          <div className="header-content">
            <div>
              <h1>Teacher Dashboard</h1>
              {teacherInfo.email && (
                <p className="teacher-email">Logged in as: {teacherInfo.email}</p>
              )}
            </div>
            <div className="header-buttons">
              <button className="btn btn-secondary" onClick={() => navigate('/')}>
                <Home size={20} />
                Home
              </button>
              <button className="btn btn-danger" onClick={handleLogout}>
                <LogOut size={20} />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container dashboard-content">
        {/* Status Bar */}
        <div className="status-bar card">
          <div className="status-item">
            <span className={`status-indicator ${classActive ? 'active' : 'inactive'}`}>
              <span className="status-dot pulse"></span>
              {classActive ? 'Class Active' : 'Class Inactive'}
            </span>
          </div>
          <div className="status-item">
            <span className={`status-indicator ${isListening ? 'active' : 'inactive'}`}>
              {isListening ? <Mic size={16} /> : <MicOff size={16} />}
              {isListening ? 'Mic ON' : 'Mic OFF'}
            </span>
          </div>
          {joinCode && (
            <div className="status-item">
              <strong>Join Code: {joinCode}</strong> {joinMessage && <span>{joinMessage}</span>}
              <button className="btn btn-sm" onClick={async () => {
                try {
                  await navigator.clipboard?.writeText(joinCode);
                  alert('Join code copied!');
                } catch (err) {
                  // Fallback for when clipboard API fails
                  const textArea = document.createElement('textarea');
                  textArea.value = joinCode;
                  document.body.appendChild(textArea);
                  textArea.select();
                  document.execCommand('copy');
                  document.body.removeChild(textArea);
                  alert('Join code copied!');
                }
              }}>Copy</button>
            </div>
          )}
          <div className="status-item">
            <span className="latency-indicator">
              Latency: <strong>{latency}s</strong>
            </span>
          </div>
        </div>

        {/* Live Speech Input Section */}
        <div className="speech-input-section">
          <div className="card">
            <div className="section-header">
              <h2>Live Speech Input (English)</h2>
              {isListening && <span className="recording-badge pulse">● Recording</span>}
            </div>
            
            <div className="speech-input-box">
              {englishText ? (
                <p className="speech-text">{englishText}</p>
              ) : (
                <p className="placeholder-text">
                  {isListening ? 'Listening... Speak now...' : 'Start class to begin recording'}
                </p>
              )}
            </div>

            {/* Test Input for Demo */}
            {classActive && (
              <div className="test-input">
                <input
                  type="text"
                  placeholder="Type to simulate speech input..."
                  value={englishText}
                  onChange={(e) => handleSpeechInput(e.target.value)}
                  className="speech-test-input"
                />
              </div>
            )}
          </div>
        </div>

        {/* Translation Output Section */}
        <div className="translation-section">
          <h2 className="section-title">Translation Output</h2>
          <div className="translation-grid">
            {/* Bodo Translation */}
            <div className="card translation-card">
              <div className="translation-header">
                <span className="language-badge bodo">Bodo</span>
              </div>
              <div className="translation-output">
                {bodoTranslation ? (
                  <p>{bodoTranslation}</p>
                ) : (
                  <p className="placeholder-text">Bodo translation will appear here...</p>
                )}
              </div>
            </div>

            {/* Mizo Translation */}
            <div className="card translation-card">
              <div className="translation-header">
                <span className="language-badge mizo">Mizo</span>
              </div>
              <div className="translation-output">
                {mizoTranslation ? (
                  <p>{mizoTranslation}</p>
                ) : (
                  <p className="placeholder-text">Mizo translation will appear here...</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Control Buttons */}
        <div className="control-buttons">
          {!classActive ? (
            <button className="btn btn-success btn-large" onClick={startClass}>
              <Play size={24} />
              Start Class
            </button>
          ) : (
            <button className="btn btn-danger btn-large" onClick={stopClass}>
              <Square size={24} />
              Stop Class
            </button>
          )}
          
          <button 
            className="btn btn-primary" 
            onClick={downloadSummary}
            disabled={!englishText}
          >
            <Download size={20} />
            Download Summary
          </button>
        </div>
      </div>
    </div>
  );
};

export default TeacherDashboard;
