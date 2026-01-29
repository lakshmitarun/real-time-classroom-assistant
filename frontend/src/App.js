import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import TeacherDashboard from './pages/TeacherDashboard';
import StudentView from './pages/StudentView';
import TranslationTest from './pages/TranslationTest';
import AdminDashboard from './pages/AdminDashboard';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function App() {
  // Enable React Router v7 future flags to suppress deprecation warnings
  const router = createBrowserRouter(
    [
      { path: '/', element: <HomePage /> },
      { path: '/login', element: <LoginPage /> },
      {
        path: '/teacher-dashboard',
        element: (
          <ProtectedRoute requiredRole="teacher">
            <TeacherDashboard />
          </ProtectedRoute>
        ),
      },
      {
        path: '/teacher',
        element: (
          <ProtectedRoute requiredRole="teacher">
            <TeacherDashboard />
          </ProtectedRoute>
        ),
      },
      {
        path: '/student',
        element: (
          <ProtectedRoute requiredRole="student">
            <StudentView />
          </ProtectedRoute>
        ),
      },
      { path: '/test', element: <TranslationTest /> },
      { path: '/admin', element: <AdminDashboard /> },
    ],
    {
      future: {
        v7_startTransition: true,      // ✅ Wrap state updates in React.startTransition
        v7_relativeSplatPath: true,    // ✅ Fix relative splat path resolution
        v7_fetcherPersist: true,       // ✅ Prepare for fetcher persistence
        v7_normalizeFormMethod: true,  // ✅ Normalize form methods
        v7_skipActionErrorRevalidation: true,  // ✅ Skip re-validation on errors
      },
    }
  );

  return <RouterProvider router={router} />;
}

export default App;
