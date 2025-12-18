import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mic, Languages, Volume2, Users, GraduationCap, Globe, LogOut, LayoutDashboard } from 'lucide-react';
import './HomePage.css';

const HomePage = () => {
  const navigate = useNavigate();
  const [teacher, setTeacher] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if teacher is logged in
    const token = localStorage.getItem('token');
    const teacherData = localStorage.getItem('teacher');
    
    if (token && teacherData) {
      try {
        setTeacher(JSON.parse(teacherData));
      } catch (err) {
        console.error('Failed to parse teacher data:', err);
      }
    }
    setLoading(false);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('teacher');
    setTeacher(null);
    navigate('/');
  };

  const features = [
    {
      icon: <Mic size={32} />,
      title: 'Speech-to-Text',
      description: 'Real-time voice recognition'
    },
    {
      icon: <Languages size={32} />,
      title: 'Translation',
      description: 'English ↔ Bodo ↔ Mizo'
    },
    {
      icon: <Volume2 size={32} />,
      title: 'Text-to-Speech',
      description: 'Audio playback support'
    }
  ];

  return (
    <div className="home-page">
      {/* Navbar */}
      <nav className="home-navbar">
        <div className="navbar-container">
          <div className="navbar-logo">
            <Globe size={28} />
            <span>Classroom Assistant</span>
          </div>
          <div className="navbar-right">
            {teacher ? (
              <div className="navbar-auth">
                <span className="teacher-name">Welcome, {teacher.name || 'Teacher'}! 👋</span>
                <button 
                  className="btn btn-nav btn-dashboard"
                  onClick={() => navigate('/teacher-dashboard')}
                >
                  <LayoutDashboard size={18} />
                  Dashboard
                </button>
                <button 
                  className="btn btn-nav btn-logout"
                  onClick={handleLogout}
                >
                  <LogOut size={18} />
                  Logout
                </button>
              </div>
            ) : null}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="hero-section">
        <div className="container">
          <div className="hero-content fade-in">
            <div className="logo-large">
              <Globe size={48} className="logo-icon" />
              <h1>Real-Time Classroom Assistant</h1>
            </div>
            <h2 className="tagline">Breaking Language Barriers in Classrooms</h2>
            <p className="subtitle">
              Instant translation between English, Bodo, and Mizo languages
            </p>

            {/* Main Action Buttons */}
            {!teacher && (
              <div className="action-buttons">
                <button 
                  className="btn btn-login-primary"
                  onClick={() => navigate('/login?type=teacher')}
                >
                  <GraduationCap size={24} />
                  Login as Teacher
                </button>
                <button 
                  className="btn btn-login-primary"
                  onClick={() => navigate('/student')}
                >
                  <Users size={24} />
                  Login as Student
                </button>
              </div>
            )}

            {/* Quick Links */}
            <div className="quick-links">
              <button 
                className="link-btn"
                onClick={() => navigate('/test')}
              >
                Test Translation
              </button>
              <button 
                className="link-btn"
                onClick={() => navigate('/admin')}
              >
                Admin Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="features-section">
        <div className="container">
          <h3 className="section-title">Key Features</h3>
          <div className="features-grid">
            {features.map((feature, index) => (
              <div key={index} className="feature-card card fade-in">
                <div className="feature-icon">{feature.icon}</div>
                <h4>{feature.title}</h4>
                <p>{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Language Support Badge */}
      <div className="language-support">
        <div className="container">
          <div className="support-badges">
            <span className="language-badge">English</span>
            <span className="arrow">↔</span>
            <span className="language-badge bodo">Bodo</span>
            <span className="arrow">↔</span>
            <span className="language-badge mizo">Mizo</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="home-footer">
        <p>Team No. 5 | Real-Time Classroom Assistant Project</p>
        <p className="team-info">P. Lakshmi Tarun • K. Bhavya Akshaya • Ch. Aravind • K. Manikanta • S. Naveen</p>
      </footer>
    </div>
  );
};

export default HomePage;
