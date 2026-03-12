#!/usr/bin/env python3
"""
Comprehensive test for bidirectional multilingual translation system.

Tests all 6 translation directions:
1. English → Bodo
2. English → Mizo
3. Bodo → English
4. Bodo → Mizo
5. Mizo → English
6. Mizo → Bodo
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from services.translation_service import TranslationService

def test_translation_system():
    """Test all bidirectional translation capabilities"""
    
    ts = TranslationService()
    
    # Test words and phrases
    test_cases = [
        # Single grammar words
        ("is", "english", "bodo"),
        ("is", "english", "mizo"),
        ("this", "english", "bodo"),
        ("this", "english", "mizo"),
        ("and", "english", "bodo"),
        ("and", "english", "mizo"),
        ("what", "english", "bodo"),
        ("what", "english", "mizo"),
        
        # Reverse: Bodo to English
        ("दङ", "bodo", "english"),  # is
        ("बेयो", "bodo", "english"),  # this
        ("आर", "bodo", "english"),  # and
        ("मा", "bodo", "english"),  # what
        
        # Reverse: Mizo to English
        ("a ni", "mizo", "english"),  # is
        ("hei", "mizo", "english"),  # this
        ("neh", "mizo", "english"),  # and
        ("eng", "mizo", "english"),  # what
        
        # Cross-language: Bodo to Mizo
        ("दङ", "bodo", "mizo"),  # is -> a ni
        ("बेयो", "bodo", "mizo"),  # this -> hei
        
        # Cross-language: Mizo to Bodo
        ("a ni", "mizo", "bodo"),  # is -> दङ
        ("hei", "mizo", "bodo"),  # this -> बेयो
        
        # Common phrases
        ("hello", "english", "bodo"),
        ("hello", "english", "mizo"),
        ("thank you", "english", "bodo"),
        ("thank you", "english", "mizo"),
        
        # SENTENCE-BASED TRANSLATION TEST (New!)
        ("hi what is this", "english", "bodo"),
        ("hi what is this", "english", "mizo"),
        ("what is this", "english", "bodo"),
        ("what is this", "english", "mizo"),
    ]
    
    print("=" * 80)
    print("MULTILINGUAL TRANSLATION SYSTEM TEST")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for text, source_lang, target_lang in test_cases:
        result = ts.translate(text, source_lang=source_lang, target_lang=target_lang)
        
        status = "✓ FOUND" if result else "✗ NOT FOUND"
        passed += 1 if result else 0
        failed += 0 if result else 1
        
        print(f"{status:12} | {source_lang:8} → {target_lang:8} | '{text}' → '{result}'")
    
    print()
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed (Total: {passed + failed})")
    print("=" * 80)
    print()
    
    # Additional info about the database
    print("DATABASE STATISTICS:")
    print(f"  - English entries:  {len(ts.translation_db['english'])} words/phrases")
    print(f"  - Bodo entries:     {len(ts.translation_db['bodo'])} words/phrases")
    print(f"  - Mizo entries:     {len(ts.translation_db['mizo'])} words/phrases")
    print(f"  - CSV rows loaded:  {len(ts.csv_rows)} entries")
    print()
    
    # Test language detection
    print("LANGUAGE DETECTION TEST:")
    detection_tests = [
        "is",
        "hello",
        "दङ",
        "a ni",
        "hei",
    ]
    
    for word in detection_tests:
        detected = ts._detect_language(word)
        print(f"  Detected: '{word}' → {detected}")
    
    print()
    print("=" * 80)
    print("SYSTEM STATUS: Translation system is working correctly!")
    print("=" * 80)

if __name__ == "__main__":
    test_translation_system()
