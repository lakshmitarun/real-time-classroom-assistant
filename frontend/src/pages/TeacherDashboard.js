import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mic, MicOff, Download, Home, Play, Square } from 'lucide-react';
import API_BASE_URL from '../config/api';
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

  // Auth check: redirect to login if no token
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
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
      const response = await fetch(`${API_BASE_URL}/api/teacher/start-class`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : ''
        },
        body: JSON.stringify({ subject: 'General' })
      });
      const data = await response.json();
      if (data.success) {
        setJoinCode(data.joinCode || '');
        setJoinMessage('Share this code with students');
      }
    } catch (err) {
      console.error('Error starting class', err);
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
      if (joinCode) {
        await fetch(`${API_BASE_URL}/api/teacher/stop-class`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
          },
          body: JSON.stringify({ joinCode })
        });
      }
    } catch (err) {
      console.error('Error stopping class', err);
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

  const translateText = async (text) => {
    if (!text) {
      setBodoTranslation('');
      setMizoTranslation('');
      return;
    }
    
    try {
      const startTime = performance.now();
      const response = await fetch(`${API_BASE_URL}/api/translate/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text.trim(),
          source_lang: 'english'
        })
      });
      
      const endTime = performance.now();
      setLatency(((endTime - startTime) / 1000).toFixed(1));
      
      if (!response.ok) {
        throw new Error('Translation API failed');
      }
      
      const data = await response.json();
      
      if (data.translations && data.translations.bodo) {
        setBodoTranslation(data.translations.bodo);
      } else {
        setBodoTranslation('— (not found in dataset)');
      }
      
      if (data.translations && data.translations.mizo) {
        setMizoTranslation(data.translations.mizo);
      } else {
        setMizoTranslation('— (not found in dataset)');
      }
    } catch (error) {
      console.error('Translation error:', error);
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

  return (
    <div className="teacher-dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="container">
          <div className="header-content">
            <h1>Teacher Dashboard</h1>
            <button className="btn btn-secondary" onClick={() => navigate('/')}>
              <Home size={20} />
              Home
            </button>
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
              <button className="btn btn-sm" onClick={() => navigator.clipboard?.writeText(joinCode)}>Copy</button>
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
