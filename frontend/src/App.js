import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import TeacherDashboard from './pages/TeacherDashboard';
import StudentView from './pages/StudentView';
import TranslationTest from './pages/TranslationTest';
import AdminDashboard from './pages/AdminDashboard';
import DiagnosticPage from './pages/DiagnosticPage';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          
          {/* Teacher Routes - Protected */}
          <Route 
            path="/teacher-dashboard" 
            element={
              <ProtectedRoute requiredRole="teacher">
                <TeacherDashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/teacher" 
            element={
              <ProtectedRoute requiredRole="teacher">
                <TeacherDashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* Student Routes - Protected */}
          <Route 
            path="/student" 
            element={
              <ProtectedRoute requiredRole="student">
                <StudentView />
              </ProtectedRoute>
            } 
          />
          
          {/* Other Routes */}
          <Route path="/test" element={<TranslationTest />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/diagnostic" element={<DiagnosticPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
