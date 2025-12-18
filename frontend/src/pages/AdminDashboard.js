import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Home, Users, Activity, Clock, TrendingUp, 
  Database, Upload, Download, BarChart3 
} from 'lucide-react';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState({
    activeClassrooms: 0,
    totalTeachers: 0,
    totalStudents: 0,
    loggedInStudents: 0,
    totalUniqueLogins: 0,
    avgAccuracy: 0,
    avgLatency: 0,
    totalTranslations: 0
  });
  const [activeStudents, setActiveStudents] = useState([]);

  // Fetch stats and active students on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, studentsRes] = await Promise.all([
          axios.get('http://localhost:5000/api/stats'),
          axios.get('http://localhost:5000/api/active-students')
        ]);
        
        setStats({
          activeClassrooms: statsRes.data.active_classrooms,
          totalTeachers: statsRes.data.total_teachers,
          totalStudents: statsRes.data.total_students,
          loggedInStudents: statsRes.data.logged_in_students,
          totalUniqueLogins: statsRes.data.total_unique_logins,
          avgAccuracy: statsRes.data.avg_accuracy,
          avgLatency: statsRes.data.avg_latency,
          totalTranslations: statsRes.data.total_translations
        });
        
        setActiveStudents(studentsRes.data.students);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      }
    };
    
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
    
    return () => clearInterval(interval);
  }, []);

  // recentActivity and translationStats removed (no hardcoded demo data)
  const recentActivity = [];
  const translationStats = [];

  const handleUploadDataset = () => {
    alert('Upload dataset functionality coming soon!');
  };

  const handleExportData = () => {
    const data = JSON.stringify(stats, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'analytics-data.json';
    a.click();
  };

  return (
    <div className="admin-dashboard">
      {/* Header */}
      <header className="admin-header">
        <div className="container">
          <div className="header-content">
            <div>
              <h1>Admin Dashboard</h1>
              <p className="header-subtitle">Real-Time Classroom Assistant Analytics</p>
            </div>
            <button className="btn btn-secondary" onClick={() => navigate('/')}>
              <Home size={20} />
              Home
            </button>
          </div>
        </div>
      </header>

      <div className="container admin-content">
        {/* Tabs */}
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <Activity size={18} />
            Overview
          </button>
          <button
            className={`tab ${activeTab === 'classrooms' ? 'active' : ''}`}
            onClick={() => setActiveTab('classrooms')}
          >
            <Users size={18} />
            Classrooms
          </button>
          <button
            className={`tab ${activeTab === 'dataset' ? 'active' : ''}`}
            onClick={() => setActiveTab('dataset')}
          >
            <Database size={18} />
            Dataset
          </button>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="tab-content fade-in">
            {/* Stats Grid (renders only stats that have real/non-zero values) */}
            <div className="stats-grid">
              {[
                { key: 'activeClassrooms', label: 'Active Classrooms', icon: Users, color: '#3b82f6' },
                { key: 'totalStudents', label: 'Total Students', icon: Users, color: '#8b5cf6' },
                { key: 'loggedInStudents', label: 'Logged In Students', icon: Activity, color: '#ec4899' },
                { key: 'totalUniqueLogins', label: 'Total Unique Logins', icon: Users, color: '#6366f1' },
                { key: 'avgAccuracy', label: 'Avg Accuracy', icon: TrendingUp, color: '#10b981', isPercent: true },
                { key: 'avgLatency', label: 'Avg Latency', icon: Clock, color: '#f59e0b', isSeconds: true }
              ].map((item) => {
                const value = stats[item.key];
                const hasValue = value !== null && value !== undefined && !(typeof value === 'number' && value === 0);
                if (!hasValue) return null;
                const Icon = item.icon;
                const display = (item.isPercent && typeof value === 'number')
                  ? `${value}%`
                  : (item.isSeconds && typeof value === 'number')
                    ? `${value}s`
                    : (typeof value === 'number' ? value.toLocaleString() : value);

                return (
                  <div className="stat-card card" key={item.key}>
                    <div className="stat-icon" style={{ background: item.color }}>
                      <Icon size={24} />
                    </div>
                    <div className="stat-content">
                      <h3>{display}</h3>
                      <p>{item.label}</p>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Translation Statistics */}
            <div className="translation-stats card">
              <h2>Translation Statistics</h2>
              <div className="stats-table">
                <table>
                  <thead>
                    <tr>
                      <th>Language Pair</th>
                      <th>Total Translations</th>
                      <th>Accuracy</th>
                      <th>Progress</th>
                    </tr>
                  </thead>
                  <tbody>
                    {translationStats.length > 0 ? (
                        translationStats.map((stat, index) => (
                          <tr key={index}>
                            <td><strong>{stat.language}</strong></td>
                            <td>{stat.count.toLocaleString()}</td>
                            <td>
                              <span className="accuracy-badge">{stat.accuracy}%</span>
                            </td>
                            <td>
                              <div className="progress-bar">
                                <div
                                  className="progress-fill"
                                  style={{ width: `${stat.accuracy}%` }}
                                ></div>
                              </div>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={4} style={{ textAlign: 'center', color: '#666' }}>
                            Translation statistics are not available.
                          </td>
                        </tr>
                      )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Logged In Students */}
            <div className="logged-students card">
              <h2>
                <Activity size={24} />
                Currently Logged In Students ({activeStudents.length})
              </h2>
              {activeStudents.length > 0 ? (
                <div className="stats-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Student ID</th>
                        <th>Name</th>
                        <th>Preferred Language</th>
                        <th>Login Time</th>
                      </tr>
                    </thead>
                    <tbody>
                      {activeStudents.map((student, index) => (
                        <tr key={index}>
                          <td><strong>{student.userId}</strong></td>
                          <td>{student.name}</td>
                          <td>
                            <span className="language-badge">
                              {student.preferredLanguage || 'Not set'}
                            </span>
                          </td>
                          <td>{new Date(student.loginTime).toLocaleTimeString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="empty-state">
                  <p>No students currently logged in</p>
                </div>
              )}
            </div>

            {/* Performance Chart Placeholder */}
            <div className="chart-card card">
              <h2>
                <BarChart3 size={24} />
                Performance Metrics
              </h2>
              <div className="chart-placeholder">
                <p>Translation accuracy and latency trends over time</p>
                <div className="mock-chart">
                  <div className="chart-bar" style={{ height: '60%' }}></div>
                  <div className="chart-bar" style={{ height: '75%' }}></div>
                  <div className="chart-bar" style={{ height: '85%' }}></div>
                  <div className="chart-bar" style={{ height: '92%' }}></div>
                  <div className="chart-bar" style={{ height: '95%' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Classrooms Tab */}
        {activeTab === 'classrooms' && (
          <div className="tab-content fade-in">
            <div className="classrooms-list card">
              <h2>Active Classrooms</h2>
              <div className="classrooms-table">
                <table>
                  <thead>
                    <tr>
                      <th>Teacher</th>
                      <th>Subject</th>
                      <th>Students</th>
                      <th>Time</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentActivity.length > 0 ? (
                      recentActivity.map((activity) => (
                        <tr key={activity.id}>
                          <td><strong>{activity.teacher}</strong></td>
                          <td>{activity.class}</td>
                          <td>{activity.students}</td>
                          <td>{activity.time}</td>
                          <td>
                            <span className={`status-badge ${activity.status}`}>
                              {activity.status === 'active' ? '● Active' : '○ Ended'}
                            </span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={5} style={{ textAlign: 'center', color: '#666' }}>
                          No classroom activity data available.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="teacher-stats card">
              <h2>Teacher Performance</h2>
              <div className="teacher-list">
                <div className="empty-state">
                  <p>Teacher performance data is not available.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Dataset Tab */}
        {activeTab === 'dataset' && (
          <div className="tab-content fade-in">
            <div className="dataset-management card">
              <h2>Dataset Management</h2>
              
              <div className="dataset-stats">
                <div className="dataset-stat">
                  <h3>{stats.totalTranslations ? stats.totalTranslations.toLocaleString() : '—'}</h3>
                  <p>Total Parallel Sentences</p>
                </div>
                <div className="dataset-stat">
                  <h3>—</h3>
                  <p>English-Bodo Pairs</p>
                </div>
                <div className="dataset-stat">
                  <h3>—</h3>
                  <p>English-Mizo Pairs</p>
                </div>
              </div>

              <div className="dataset-actions">
                <button className="btn btn-primary" onClick={handleUploadDataset}>
                  <Upload size={20} />
                  Upload New Dataset
                </button>
                <button className="btn btn-secondary" onClick={handleExportData}>
                  <Download size={20} />
                  Export Analytics
                </button>
              </div>
            </div>

            <div className="dataset-quality card">
              <h2>Dataset Quality Metrics</h2>
              <div className="quality-metrics">
                <div className="metric-item">
                  <span className="metric-label">Data Completeness</span>
                  <div className="metric-bar">
                    <div className="metric-fill" style={{ width: '87%' }}></div>
                  </div>
                  <span className="metric-value">87%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Validation Accuracy</span>
                  <div className="metric-bar">
                    <div className="metric-fill" style={{ width: '94%' }}></div>
                  </div>
                  <span className="metric-value">94%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Coverage (Classroom Terms)</span>
                  <div className="metric-bar">
                    <div className="metric-fill" style={{ width: '78%' }}></div>
                  </div>
                  <span className="metric-value">78%</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
