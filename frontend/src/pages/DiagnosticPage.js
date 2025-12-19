import React, { useEffect, useState } from 'react';

const DiagnosticPage = () => {
  const [info, setInfo] = useState({});

  useEffect(() => {
    setInfo({
      currentOrigin: window.location.origin,
      hostname: window.location.hostname,
      port: window.location.port,
      protocol: window.location.protocol,
      href: window.location.href
    });
  }, []);

  return (
    <div style={{ padding: '40px', fontFamily: 'monospace', backgroundColor: '#f0f0f0' }}>
      <h2>🔍 Google OAuth Diagnostic</h2>
      <p><strong>Current Origin:</strong> {info.currentOrigin}</p>
      <p><strong>Hostname:</strong> {info.hostname}</p>
      <p><strong>Port:</strong> {info.port}</p>
      <p><strong>Protocol:</strong> {info.protocol}</p>
      
      <hr />
      
      <h3>✅ What to add to Google Cloud Console:</h3>
      <p style={{ backgroundColor: 'yellow', padding: '10px', fontWeight: 'bold' }}>
        {info.currentOrigin}
      </p>
      
      <h3>📋 Instructions:</h3>
      <ol>
        <li>Go to: <a href="https://console.cloud.google.com/apis/credentials" target="_blank" rel="noopener noreferrer">Google Cloud Console</a></li>
        <li>Find your OAuth 2.0 Client ID</li>
        <li>Under "Authorized JavaScript origins", add: <code>{info.currentOrigin}</code></li>
        <li>Save and wait 5-10 minutes</li>
        <li>Clear browser cache (Ctrl+Shift+Delete) and refresh</li>
      </ol>
    </div>
  );
};

export default DiagnosticPage;
