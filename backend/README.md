# Classroom Assistant Backend API

Flask-based REST API for real-time translation between English, Bodo, and Mizo languages.

## Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Server runs at: `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /api/health
```

### Translate Text
```
POST /api/translate
Content-Type: application/json

{
  "text": "Hello",
  "source_lang": "english",
  "target_lang": "bodo"
}
```

### Batch Translation
```
POST /api/translate/batch
Content-Type: application/json

{
  "text": "Good morning class",
  "source_lang": "english"
}

Returns translations in all languages.
```

### Text-to-Speech
```
POST /api/speech/text-to-speech
Content-Type: application/json

{
  "text": "Hello",
  "language": "english"
}
```

### Get Statistics
```
GET /api/stats
```

## Supported Languages

- English (`english`)
- Bodo (`bodo`)
- Mizo (`mizo`)

## Translation Database

The translation service includes 30+ common classroom phrases in all three languages.

## Features

- ✅ REST API with Flask
- ✅ CORS enabled for frontend integration
- ✅ Bidirectional translation
- ✅ Text-to-speech conversion
- ✅ In-memory translation database
- ✅ Expandable architecture
