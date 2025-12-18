// src/pages/TranslationTest.jsx  (or wherever you keep it)

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, Copy, Trash2, Volume2, ArrowRightLeft } from 'lucide-react';
import axios from 'axios';
import './TranslationTest.css';

const TranslationTest = () => {
  const navigate = useNavigate();

  const [inputText, setInputText] = useState('');
  const [sourceLanguage, setSourceLanguage] = useState('english');
  const [englishTranslation, setEnglishTranslation] = useState('');
  const [bodoTranslation, setBodoTranslation] = useState('');
  const [mizoTranslation, setMizoTranslation] = useState('');
  const [isTranslating, setIsTranslating] = useState(false);
  const [error, setError] = useState('');

  // Quick test phrases - matching exact dataset entries
  const samplePhrases = {
    english: [
      'Open your notebooks',
      'Close your books',
      'Please sit down',
      'Be quiet please',
      'Listen carefully',
      'Raise your hand',
      'Write this down',
      'Work in pairs',
      'Hello',
      'Thank you',
      'Yes',
      'No',
      'What is two plus three?',
      'Mathematics',
      'Science',
      'History'
    ],
    bodo: [
      'नायनि फोरमाखौ खेव',
      'नायनि किताबखौ बन्द थ',
      'अननानै फुं',
      'अननानै थिरगोन दङ',
      'मोनो खालामगोन',
      'नायनि खुन्थाखौ थोन',
      'बेखौ लिरगोन',
      'नैथिनि जुगुथाव गोब थ',
      'सुबुं',
      'मोजां',
      'अं',
      'नङा',
      'सान्न्रि',
      'बिजान',
      'बुरुं'
    ],
    mizo: [
      'I lehkhabu hawng rawh',
      'I lehkhabu khar rawh',
      'Thu rawh le',
      'Dâwiin dâi la',
      'Ngaithla ṭha takin',
      'I kut kalh rawh',
      'Hei hi ziak rawh',
      'Paihra hrang hrangah thawk rawh',
      'Chibai',
      'Ka lawm e',
      'Awle',
      'Aih',
      'Mathematics',
      'Science',
      'History'
    ]
  };

  // MAIN translation function - supports all 6 language pairs
  const handleTranslate = async () => {
    if (!inputText.trim()) {
      setError('Please enter some text to translate');
      return;
    }

    setIsTranslating(true);
    setError('');

    try {
      if (sourceLanguage === 'english') {
        // English → Bodo + Mizo
        const [bodoRes, mizoRes] = await Promise.all([
          axios.post('http://localhost:5000/api/translate', {
            text: inputText.trim(),
            source_lang: 'english',
            target_lang: 'bodo'
          }),
          axios.post('http://localhost:5000/api/translate', {
            text: inputText.trim(),
            source_lang: 'english',
            target_lang: 'mizo'
          })
        ]);

        setEnglishTranslation(''); // source is English
        setBodoTranslation(bodoRes.data.translation || 'Translation not found');
        setMizoTranslation(mizoRes.data.translation || 'Translation not found');

      } else if (sourceLanguage === 'bodo') {
        // Bodo → English + Mizo
        const [engRes, mizoRes] = await Promise.all([
          axios.post('http://localhost:5000/api/translate', {
            text: inputText.trim(),
            source_lang: 'bodo',
            target_lang: 'english'
          }),
          axios.post('http://localhost:5000/api/translate', {
            text: inputText.trim(),
            source_lang: 'bodo',
            target_lang: 'mizo'
          })
        ]);

        setEnglishTranslation(engRes.data.translation || 'Translation not found');
        setBodoTranslation(''); // source is Bodo
        setMizoTranslation(mizoRes.data.translation || 'Translation not found');

      } else if (sourceLanguage === 'mizo') {
        // Mizo → English + Bodo
        const [engRes, bodoRes] = await Promise.all([
          axios.post('http://localhost:5000/api/translate', {
            text: inputText.trim(),
            source_lang: 'mizo',
            target_lang: 'english'
          }),
          axios.post('http://localhost:5000/api/translate', {
            text: inputText.trim(),
            source_lang: 'mizo',
            target_lang: 'bodo'
          })
        ]);

        setEnglishTranslation(engRes.data.translation || 'Translation not found');
        setBodoTranslation(bodoRes.data.translation || 'Translation not found');
        setMizoTranslation(''); // source is Mizo
      }
    } catch (err) {
      console.error('Translation error:', err);
      setError('Failed to translate. Make sure the backend is running on port 5000.');
      setEnglishTranslation('⚠️ Translation service unavailable');
      setBodoTranslation('⚠️ Translation service unavailable');
      setMizoTranslation('⚠️ Translation service unavailable');
    } finally {
      setIsTranslating(false);
    }
  };

  // Textarea change
  const handleInputChange = (e) => {
    setInputText(e.target.value);
    setError('');
  };

  // Enter key → translate
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleTranslate();
    }
  };

  // Clear everything
  const clearAll = () => {
    setInputText('');
    setEnglishTranslation('');
    setBodoTranslation('');
    setMizoTranslation('');
    setError('');
  };

  // Copy text helper
  const copyToClipboard = (text) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  // Simple TTS (English + generic Indian voice for others)
  const speakText = (text, lang) => {
    if (!text) return;
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = lang === 'english' ? 'en-US' : 'hi-IN';
      window.speechSynthesis.speak(utterance);
    }
  };

  // When a quick phrase is clicked - auto translate
  const handleSamplePhrase = async (phrase) => {
    setInputText(phrase);
    setError('');
    
    // Auto-translate after setting the text
    setTimeout(() => {
      handleTranslate();
    }, 100);
  };

  return (
    <div className="translation-test">
      {/* Header */}
      <header className="test-header">
        <div className="container">
          <div className="header-content">
            <h1>Translation Test Panel</h1>
            <button className="btn btn-secondary" onClick={() => navigate('/')}>
              <Home size={20} />
              <span>Home</span>
            </button>
          </div>
        </div>
      </header>

      <div className="container">
        {/* Language selector */}
        <div className="language-selector">
          <h3>Source Language:</h3>
          <div className="language-buttons">
            <button
              className={`lang-btn ${sourceLanguage === 'english' ? 'active' : ''}`}
              onClick={() => { setSourceLanguage('english'); clearAll(); }}
            >
              English
            </button>
            <button
              className={`lang-btn ${sourceLanguage === 'bodo' ? 'active' : ''}`}
              onClick={() => { setSourceLanguage('bodo'); clearAll(); }}
            >
              Bodo (बड़ो)
            </button>
            <button
              className={`lang-btn ${sourceLanguage === 'mizo' ? 'active' : ''}`}
              onClick={() => { setSourceLanguage('mizo'); clearAll(); }}
            >
              Mizo
            </button>
          </div>
        </div>

        {/* Input section */}
        <div className="input-section">
          <div className="section-header">
            <h3>{sourceLanguage.charAt(0).toUpperCase() + sourceLanguage.slice(1)} Text</h3>
            <button className="btn-icon" onClick={clearAll} title="Clear all">
              <Trash2 size={20} />
            </button>
          </div>

          <textarea
            className="input-textarea"
            placeholder={`Type ${sourceLanguage} text here... (Press Enter to translate)`}
            value={inputText}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            rows={5}
          />

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          <button
            className="btn btn-primary btn-large translate-btn"
            onClick={handleTranslate}
            disabled={isTranslating || !inputText.trim()}
          >
            <ArrowRightLeft size={20} />
            {isTranslating ? 'Translating...' : 'Translate'}
          </button>
        </div>

        {/* Quick test phrases */}
        <div className="quick-phrases">
          <h3>Quick Test Phrases:</h3>
          <div className="phrase-buttons">
            {samplePhrases[sourceLanguage].map((phrase, i) => (
              <button
                key={i}
                className="phrase-btn"
                onClick={() => handleSamplePhrase(phrase)}
              >
                {phrase}
              </button>
            ))}
          </div>
        </div>

        {/* Results */}
        <div className="translation-results">
          <h2>Translation Results</h2>

          <div className="results-grid">
            {/* English result (hide when English is source) */}
            {sourceLanguage !== 'english' && (
              <div className="result-card">
                <div className="result-header">
                  <span className="language-badge english">ENGLISH</span>
                  <div className="result-actions">
                    <button
                      className="btn-icon"
                      onClick={() => speakText(englishTranslation, 'english')}
                      disabled={!englishTranslation}
                      title="Speak"
                    >
                      <Volume2 size={18} />
                    </button>
                    <button
                      className="btn-icon"
                      onClick={() => copyToClipboard(englishTranslation)}
                      disabled={!englishTranslation}
                      title="Copy"
                    >
                      <Copy size={18} />
                    </button>
                  </div>
                </div>
                <div className="result-text">
                  {englishTranslation || 'Translation will appear here...'}
                </div>
              </div>
            )}

            {/* Bodo result (hide when Bodo is source) */}
            {sourceLanguage !== 'bodo' && (
              <div className="result-card">
                <div className="result-header">
                  <span className="language-badge bodo">BODO (बड़ो)</span>
                  <div className="result-actions">
                    <button
                      className="btn-icon"
                      onClick={() => speakText(bodoTranslation, 'bodo')}
                      disabled={!bodoTranslation}
                      title="Speak"
                    >
                      <Volume2 size={18} />
                    </button>
                    <button
                      className="btn-icon"
                      onClick={() => copyToClipboard(bodoTranslation)}
                      disabled={!bodoTranslation}
                      title="Copy"
                    >
                      <Copy size={18} />
                    </button>
                  </div>
                </div>
                <div className="result-text">
                  {bodoTranslation || 'Translation will appear here...'}
                </div>
              </div>
            )}

            {/* Mizo result (hide when Mizo is source) */}
            {sourceLanguage !== 'mizo' && (
              <div className="result-card">
                <div className="result-header">
                  <span className="language-badge mizo">MIZO</span>
                  <div className="result-actions">
                    <button
                      className="btn-icon"
                      onClick={() => speakText(mizoTranslation, 'mizo')}
                      disabled={!mizoTranslation}
                      title="Speak"
                    >
                      <Volume2 size={18} />
                    </button>
                    <button
                      className="btn-icon"
                      onClick={() => copyToClipboard(mizoTranslation)}
                      disabled={!mizoTranslation}
                      title="Copy"
                    >
                      <Copy size={18} />
                    </button>
                  </div>
                </div>
                <div className="result-text">
                  {mizoTranslation || 'Translation will appear here...'}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Instructions */}
        <div className="instructions">
          <h3>How to Use:</h3>
          <ol>
            <li>Select your source language (English, Bodo, or Mizo).</li>
            <li>Type text manually or click a quick test phrase.</li>
            <li>Click <strong>Translate</strong> or press Enter.</li>
            <li>See the translations in Bodo and/or Mizo below.</li>
            <li>Use the speaker icon to listen, copy icon to copy text.</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default TranslationTest;
