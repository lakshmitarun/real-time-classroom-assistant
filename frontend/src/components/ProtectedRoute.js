import React from 'react';
import { Navigate } from 'react-router-dom';

/**
 * ProtectedRoute component for role-based access control
 * Checks if user has required role before rendering the component
 */
const ProtectedRoute = ({ children, requiredRole }) => {
  const token = localStorage.getItem('token');
  const teacherData = localStorage.getItem('teacher');
  const studentSession = localStorage.getItem('studentSession');

  // Parse stored data
  let userRole = null;
  
  if (token && teacherData) {
    try {
      const teacher = JSON.parse(teacherData);
      userRole = teacher.role || 'teacher';
    } catch (err) {
      console.error('Failed to parse teacher data:', err);
      localStorage.removeItem('token');
      localStorage.removeItem('teacher');
      return <Navigate to="/login" />;
    }
  } else if (studentSession) {
    try {
      const student = JSON.parse(studentSession);
      userRole = student.role || 'student';
    } catch (err) {
      console.error('Failed to parse student data:', err);
      localStorage.removeItem('studentSession');
      return <Navigate to="/student" />;
    }
  }

  // Special case: Allow unauthenticated access to /student for login form
  if (requiredRole === 'student' && !userRole) {
    return children; // Render StudentView (which shows login form if not authenticated)
  }

  // No role found and not student route - redirect to login
  if (!userRole) {
    return <Navigate to="/login" />;
  }

  // User has required role - render component
  if (userRole === requiredRole) {
    return children;
  }

  // Role mismatch - redirect based on actual role
  if (userRole === 'teacher') {
    return <Navigate to="/teacher-dashboard" />;
  } else if (userRole === 'student') {
    return <Navigate to="/student" />;
  }

  // Fallback - redirect to login
  return <Navigate to="/login" />;
};

export default ProtectedRoute;
