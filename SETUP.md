# Project Structure

```
classroom-assistant/
├── frontend/                 # All frontend files
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── package-lock.json
├── backend/                  # Flask backend
│   ├── app.py
│   ├── auth_service.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── static/
├── data/                     # Data files
└── README.md
```

## Running the Application

### Terminal 1 - Backend (Python)
```powershell
cd d:\classroom-assistant\backend
python app.py
```
Backend runs on http://localhost:5000

### Terminal 2 - Frontend (Node.js)
```powershell
cd d:\classroom-assistant\frontend
npm install  # if needed
npm start
```
Frontend runs on http://localhost:3001

Both are already CORS-configured to communicate with each other.
