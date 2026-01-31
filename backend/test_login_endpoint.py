#!/usr/bin/env python
"""Test the login endpoint directly"""

from app import app
import json

# Create a test client
with app.test_client() as client:
    # Test teacher login
    response = client.post('/api/auth/login', 
        data=json.dumps({
            'email': 'lakshmitaruntarun@gmail.com',
            'password': 'tarun123'
        }),
        content_type='application/json'
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json}")
    
    data = response.json
    if data.get('teacher'):
        print(f"✅ Teacher name from response: {data['teacher'].get('name')}")
