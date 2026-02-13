#!/usr/bin/env python3
"""
Complete Translation Panel Integration Test
Tests the entire flow from student login to receiving translations
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:5000"

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def test_backend_health():
    """Test if backend is running"""
    print_header("1. BACKEND HEALTH CHECK")
    try:
        # Try a simple endpoint
        response = requests.post(
            f"{BASE_URL}/api/student/login",
            json={"userId": "test", "password": "test"},
            timeout=5
        )
        print_success(f"Backend is running! Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to backend at {BASE_URL}")
        print_info("Make sure to run: python backend/app.py")
        return False
    except Exception as e:
        print_error(f"Backend check failed: {str(e)}")
        return False

def test_translation_service():
    """Test the translation service endpoint"""
    print_header("2. TRANSLATION SERVICE TEST")
    
    test_cases = [
        ("hello", "english", "bodo"),
        ("hello", "english", "mizo"),
        ("thank you", "english", "bodo"),
        ("thank you", "english", "mizo"),
    ]
    
    for text, source, target in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/translate",
                json={
                    "text": text,
                    "source_lang": source,
                    "target_lang": target
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                translation = data.get("translation", "")
                if translation:
                    print_success(f"'{text}' → {target.upper()}: '{translation}'")
                else:
                    print_error(f"'{text}' → {target.upper()}: (no translation found)")
            else:
                print_error(f"API returned status {response.status_code}")
        except Exception as e:
            print_error(f"Translation test failed: {str(e)}")

def test_broadcast_flow():
    """Test the complete broadcast flow"""
    print_header("3. BROADCAST FLOW TEST")
    
    join_code = "TEST123"
    english_text = "good morning class"
    
    print_info(f"Testing broadcast with code: {join_code}")
    print_info(f"English text: '{english_text}'")
    
    # Simulate teacher broadcast
    print("\n📨 Simulating teacher broadcast...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/teacher/broadcast",
            json={
                "joinCode": join_code,
                "englishText": english_text,
                "language": "both"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_success("Broadcast sent successfully")
            else:
                print_error(f"Broadcast failed: {data.get('message', 'Unknown error')}")
        else:
            print_info(f"Broadcast returned status {response.status_code}")
    except Exception as e:
        print_error(f"Broadcast test failed: {str(e)}")
    
    # Wait a moment for the broadcast to be stored
    time.sleep(1)
    
    # Retrieve as student
    print("\n👨‍🎓 Retrieving as student...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/student/get-broadcast/{join_code}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("content"):
                content = data.get("content", {})
                print_success("Broadcast retrieved successfully")
                print_info(f"  English: '{content.get('englishText', 'N/A')}'")
                print_info(f"  Bodo: '{content.get('bodoTranslation', 'N/A')}'")
                print_info(f"  Mizo: '{content.get('mizoTranslation', 'N/A')}'")
                
                # Show what student would see
                print("\n📱 Student View:")
                selected_lang = "BODO"
                translation = content.get('bodoTranslation', '(not found in dataset)')
                print(f"  [English] {content.get('englishText', 'N/A')}")
                print(f"  [{selected_lang}]  {translation}")
            else:
                print_error("No content received")
        else:
            print_info(f"Retrieval returned status {response.status_code}")
    except Exception as e:
        print_error(f"Retrieval test failed: {str(e)}")

def test_translation_panel_ready():
    """Check if translation panel is ready"""
    print_header("4. TRANSLATION PANEL READINESS CHECK")
    
    checks = {
        "Backend running": False,
        "Translation service available": False,
        "Broadcast endpoint working": False,
        "Student retrieval working": False,
    }
    
    # Check backend
    try:
        response = requests.post(
            f"{BASE_URL}/api/student/login",
            json={"userId": "test", "password": "test"},
            timeout=5
        )
        checks["Backend running"] = True
    except:
        pass
    
    # Check translation
    try:
        response = requests.post(
            f"{BASE_URL}/api/translate",
            json={"text": "hello", "source_lang": "english", "target_lang": "bodo"},
            timeout=5
        )
        checks["Translation service available"] = (response.status_code == 200)
    except:
        pass
    
    # Check broadcast
    try:
        response = requests.post(
            f"{BASE_URL}/api/teacher/broadcast",
            json={"joinCode": "CHECK", "englishText": "test", "language": "both"},
            timeout=5
        )
        checks["Broadcast endpoint working"] = (response.status_code in [200, 401, 403])
    except:
        pass
    
    # Check retrieval
    try:
        response = requests.get(
            f"{BASE_URL}/api/student/get-broadcast/CHECK",
            timeout=5
        )
        checks["Student retrieval working"] = (response.status_code in [200, 404])
    except:
        pass
    
    # Print results
    for check, passed in checks.items():
        if passed:
            print_success(check)
        else:
            print_error(check)
    
    all_passed = all(checks.values())
    return all_passed

def main():
    print("\n" + "=" * 60)
    print("  🧪 TRANSLATION PANEL INTEGRATION TEST")
    print("=" * 60)
    
    # Check backend first
    if not test_backend_health():
        print_error("\nBackend is not running. Cannot continue testing.")
        print_info("Start the backend with: python backend/app.py")
        sys.exit(1)
    
    # Run tests
    test_translation_service()
    test_broadcast_flow()
    
    # Final readiness check
    ready = test_translation_panel_ready()
    
    # Summary
    print_header("TEST SUMMARY")
    if ready:
        print_success("✨ Translation panel is READY for use!")
        print_info("Next steps:")
        print_info("1. Start frontend: cd frontend && npm start")
        print_info("2. Login as student")
        print_info("3. Select language and join class")
        print_info("4. Teacher broadcasts content")
        print_info("5. Verify translation appears in panel")
    else:
        print_error("Some tests failed. Check the output above.")
    
    print("\n")

if __name__ == "__main__":
    main()
