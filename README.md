# Winamp

Winamp is a full-stack music discovery app with a Flask backend and a Vite/React frontend.

## Stack

- Backend: Flask, SQLAlchemy, Flask-Migrate, JWT, CORS
- Frontend: React, Vite, Tailwind CSS
- Optional integrations: Spotify and Jamendo
- Mood detection: DeepFace / TensorFlow / OpenCV

## Project Structure

- `backend/`: Flask API and database models
- `static/`: React frontend

## Local Setup

### 1. Backend

```powershell
cd backend
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

The backend runs on `http://127.0.0.1:5000` by default.

### 2. Frontend

```powershell
cd static
npm install
Copy-Item .env.example .env
npm run dev
```

The frontend runs on `http://127.0.0.1:5173` by default.

## Environment Variables

### Backend (`backend/.env`)

- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `DATABASE_URL`
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `SPOTIFY_REDIRECT_URI`
- `JAMENDO_CLIENT_ID`
- `FRONTEND_ORIGINS`
- `PORT`

### Frontend (`static/.env`)

- `VITE_API_BASE_URL`
- `VITE_BACKEND_URL`

For local development, the frontend can use `/api` and rely on the Vite proxy.

## GitHub Push Checklist

- Secrets are excluded through the root `.gitignore`
- `node_modules`, `dist`, databases, caches, and local editor files are ignored
- Example env files are included instead of real secrets

## Suggested First Push

```powershell
git add .
git commit -m "Initial project setup"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```
