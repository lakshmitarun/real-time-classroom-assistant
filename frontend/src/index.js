import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import { GoogleOAuthProvider } from '@react-oauth/google';

const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID || '562438583684-5r38bmc33jhdnsk18uds1kds7h937dcg.apps.googleusercontent.com';

console.log('Google Client ID loaded:', clientId ? 'YES' : 'NO');
console.log('Client ID:', clientId.substring(0, 20) + '...');

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={clientId}>
      <App />
    </GoogleOAuthProvider>
  </React.StrictMode>
);
