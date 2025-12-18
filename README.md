# Real-Time Classroom Assistant (English ↔ Bodo ↔ Mizo)

A full-stack web application providing real-time speech recognition and translation between English, Bodo, and Mizo languages for multilingual classroom environments.

## Team Details (Team No. 5)

**Team Members:**
- P. Lakshmi Tarun (23B21A4558)
- K. Bhavya Akshaya (23B21A4504)
- Ch. Aravind (23B21A4598)
- K. Manikanta (23B21A4570)
- S. Naveen (23B21A4564)

**Mentor:** Praveen sir

## Project Overview

This project bridges language barriers in multilingual classrooms by providing instant, accurate translation and speech support between English, Bodo, and Mizo languages. It enables seamless communication for teachers and students regardless of their native language.

## ✨ Features

### Core Functionality
- ✅ **Real-time Translation** - Instant bidirectional translation (English ↔ Bodo ↔ Mizo)
- ✅ **Speech Recognition** - Live voice-to-text conversion
- ✅ **Text-to-Speech** - Audio playback of translations using gTTS
- ✅ **376+ Word Dataset** - Comprehensive parallel corpus across 23 categories
- ✅ **Case-Insensitive Search** - Works with any text capitalization

### User Interfaces
- 🏠 **Home Page** - Modern landing page with role-based navigation
- 👨‍🏫 **Teacher Dashboard** - Live speech input, auto-translation, and session recording
- 👨‍🎓 **Student View** - Clean subtitle display with auto-speaking feature
- 🧪 **Translation Test Panel** - Interactive testing interface with 30+ sample phrases
- 📊 **Admin Dashboard** - Analytics, monitoring, and performance tracking

### Technical Features
- 📱 **Responsive Design** - Optimized for desktop, tablet, and mobile
- 🎨 **Modern UI/UX** - Gradient backgrounds, smooth animations, glass-morphism effects
- ⚡ **Fast Performance** - Instant translation without artificial delays
- 🔄 **Auto-Refresh** - Teacher dashboard auto-generates translations every 5 seconds
- 🔊 **Auto-Speaking** - Student view automatically speaks translations

## 🛠️ Technology Stack

### Frontend
- **Framework:** React 18.2.0
- **Routing:** React Router DOM 6.20.0
- **Icons:** Lucide React
- **Styling:** CSS3 with custom properties
- **Charts:** Recharts (for analytics)
- **HTTP Client:** Axios

### Backend
- **Framework:** Flask 3.0.0
- **CORS:** Flask-CORS 4.0.0
- **TTS Engine:** gTTS 2.5.4
- **Environment:** Python-dotenv 1.0.0

### Dataset
- **Format:** CSV (UTF-8 encoded)
- **Size:** 376 entries
- **Categories:** 23 (Classroom Instructions, Math, Science, Social Science, Numbers, Colors, Animals, Food, Family, Nature, School, Verbs, Adjectives, Time, Objects, etc.)
- **Languages:** English, Bodo (Devanagari script), Mizo (Latin script)

## 📁 Project Structure

```
classroom-assistant/
├── public/
│   └── index.html
├── src/
│   ├── pages/
│   │   ├── HomePage.js + .css
│   │   ├── TeacherDashboard.js + .css
│   │   ├── StudentView.js + .css
│   │   ├── TranslationTest.js + .css
│   │   └── AdminDashboard.js + .css
│   ├── App.js + .css
│   ├── index.js + .css
│   └── ...
├── backend/
│   ├── app.py (Flask API server)
│   ├── requirements.txt
│   ├── services/
│   │   ├── translation_service.py
│   │   └── speech_service.py
│   ├── static/audio/ (TTS generated audio)
│   └── venv/
├── data/
│   ├── classroom_dataset_complete.csv (376 entries)
│   └── generate_dataset.py
├── package.json
└── README.md
```

## 🚀 Installation & Setup

### Prerequisites
- Node.js (v14 or higher)
- Python 3.8+ 
- npm or yarn

### Backend Setup

```bash
# Navigate to project directory
cd classroom-assistant

# Create and activate virtual environment
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install Python dependencies
pip install -r requirements.txt

# Run Flask backend
python app.py
# Backend will run on http://localhost:5000
```

### Frontend Setup

```bash
# Navigate to project root
cd classroom-assistant

# Install Node dependencies
npm install

# Start React development server
$env:PORT=3001; npm start  # Windows PowerShell
# PORT=3001 npm start  # macOS/Linux

# Frontend will run on http://localhost:3001
```

## 🌐 API Endpoints

- `GET /api/health` - Health check
- `POST /api/translate` - Single translation
  ```json
  {
    "text": "hello",
    "source_language": "english",
    "target_language": "bodo"
  }
  ```
- `POST /api/translate/batch` - Batch translation
- `GET /api/stats` - Translation statistics
- `POST /api/speech/text-to-speech` - Generate audio

## 📊 Dataset Categories (376 Entries)

| Category | Count | Examples |
|----------|-------|----------|
| Classroom Instructions | 20 | "Open your notebooks", "Listen carefully" |
| Mathematics | 20 | "What is two plus three?", "Calculate the area" |
| Science | 20 | "Observe the experiment", "Photosynthesis" |
| Social Science | 20 | "Capital of India", "Seven continents" |
| Student Questions | 20 | "May I ask a question?", "I don't understand" |
| Feedback | 20 | "Excellent work!", "Keep it up!" |
| Daily Interactions | 21 | "Good morning", "Thank you", "Hi" |
| Exam Instructions | 20 | "Time is up", "No cheating allowed" |
| Numbers | 15 | One to Hundred |
| Colors | 10 | Red, Blue, Green, Yellow, etc. |
| Body Parts | 15 | Head, Hand, Eye, etc. |
| Animals | 15 | Dog, Cat, Tiger, Elephant, etc. |
| Food & Drinks | 15 | Rice, Water, Bread, etc. |
| Family | 15 | Father, Mother, Brother, Sister, etc. |
| Nature | 15 | Sun, Moon, Tree, River, etc. |
| School Items | 15 | Book, Pen, Notebook, etc. |
| Verbs | 20 | Go, Come, Read, Write, etc. |
| Adjectives | 20 | Big, Small, Good, Hot, etc. |
| Time & Days | 20 | Today, Tomorrow, Monday, etc. |
| Objects | 20 | House, Car, Door, etc. |
| Prepositions | 8 | In, On, Under, With, etc. |
| Conjunctions | 4 | And, Or, But, Because |
| Questions | 8 | What, Where, When, Who, etc. |

## 🎯 How to Use

### For Teachers:
1. Navigate to **Teacher Dashboard** (`/teacher`)
2. Click **"Start Class"** button
3. Speak or type in English
4. View automatic Bodo and Mizo translations
5. Translations auto-refresh every 5 seconds
6. Click **"Download Summary"** to save session

### For Students:
1. Navigate to **Student View** (`/student`)
2. Click **"Connect to Classroom"**
3. Toggle between **Bodo** or **Mizo** language
4. Enable **audio** for automatic speech playback
5. Subtitles update automatically every 4 seconds

### For Testing Translations:
1. Go to **Translation Test Panel** (`/test`)
2. Select source language (English/Bodo/Mizo)
3. Type text or click a **sample phrase**
4. Click **"Translate"** (instant results)
5. Use **speaker icon** for audio, **copy icon** to copy text

### For Administrators:
1. Access **Admin Dashboard** (`/admin`)
2. View real-time translation statistics
3. Monitor active classrooms
4. Check system performance metrics
5. Analyze dataset usage patterns

## 🎨 UI Highlights

- **Gradient Backgrounds** - Modern purple-to-blue gradients
- **Glass-morphism Cards** - Frosted glass effect with backdrop blur
- **Smooth Animations** - Fade-in effects and hover transitions
- **Responsive Grid Layouts** - Adapts to all screen sizes
- **Color-coded Language Tags** - Visual language identification
- **Interactive Charts** - Real-time analytics visualization (Recharts)

## 🔧 Configuration

### Environment Variables (Optional)
Create `.env` file in backend/:
```
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

### Customization
- **Port Configuration:** Edit `$env:PORT` in startup command
- **Dataset:** Modify `data/generate_dataset.py` to add more phrases
- **Styling:** Update CSS variables in component stylesheets
- **Translation Logic:** Customize `backend/services/translation_service.py`

## 📝 Development Notes

- All translations are case-insensitive
- Dataset loaded from CSV into in-memory database on backend startup
- gTTS generates audio files cached in `backend/static/audio/`
- Frontend uses mock data fallback if backend unavailable
- WebSocket support planned for future real-time updates

## 🚧 Known Limitations

1. **Disk Space:** Frontend requires free disk space for npm compilation
2. **Limited Vocabulary:** 376 entries (expandable via dataset generator)
3. **No Authentication:** Open access (add login for production)
4. **Development Server:** Flask dev server not suitable for production
5. **TTS Quality:** gTTS uses Hindi approximation for Bodo pronunciation

## 🔮 Future Enhancements

### Phase 1 (Immediate)
- [ ] Add proper Mizo translations for: Orange, Pink, Pen, Pencil, Board, Chalk, Eraser, Classroom, Motor, Key, Minute
- [ ] Implement user authentication (JWT)
- [ ] WebSocket for real-time synchronization
- [ ] Offline mode with service workers

### Phase 2 (Advanced)
- [ ] Custom NMT model training for Bodo/Mizo
- [ ] Real microphone integration (Web Speech API)
- [ ] Session recording and playback
- [ ] Multi-classroom support
- [ ] Teacher performance analytics

### Phase 3 (Production)
- [ ] Deploy on cloud (AWS/Azure/GCP)
- [ ] Production WSGI server (Gunicorn/uWSGI)
- [ ] Database integration (PostgreSQL)
- [ ] Video call integration (WebRTC)
- [ ] Mobile apps (React Native)

## 🐛 Troubleshooting

**Frontend won't start (ENOSPC error):**
- Free up disk space on C: drive
- Run: `npm cache clean --force`
- Delete `node_modules` and reinstall

**Backend import errors:**
- Ensure virtual environment activated
- Run: `pip install -r requirements.txt`
- Check Python version (3.8+)

**Translations not working:**
- Restart backend to reload CSV
- Check console for API errors
- Verify backend running on port 5000

**Audio not playing:**
- Install gTTS: `pip install gTTS`
- Check `backend/static/audio/` folder exists
- Enable browser audio permissions

## 📜 License

Educational project developed by Team No. 5 for academic purposes.

## 🤝 Contributing

Team members can contribute via:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push and create Pull Request

## 📧 Contact

For questions, suggestions, or collaboration:
- **Team Lead:** P. Lakshmi Tarun
- **Mentor:** Praveen sir
- **Institution:** [Your College Name]

## 🙏 Acknowledgments

- Thanks to our mentor **Praveen sir** for guidance
- Bodo and Mizo language resources from community contributors
- React and Flask communities for excellent documentation

---

**🎓 Built with dedication by Team No. 5 | Breaking Language Barriers in Education**

*Last Updated: December 10, 2025*
