# Project Playto

A modern, full-stack social community platform built with **Django REST Framework** and **React**.

![Demo](https://via.placeholder.com/800x400?text=Project+Playto+Demo)

## 🚀 Features

*   **Social Feed**: Real-time posts with "Linkedin/Twitter" style layout.
*   **Interactions**: Like posts, like comments, and nested replies.
*   **Leaderboard**: Dynamic "Top Contributors" based on interaction karma (24h window).
*   **User Profiles**: Check out user stats, recent activity, and avatars.
*   **Auth & Security**: Profile management, avatar uploads, and strict interaction rules.
*   **Real-time Feel**: Usage of polling and optimistic UI updates for smooth experience.

## 🛠️ Tech Stack

### Backend
*   **Python / Django 6.0**: Robust web framework.
*   **Django REST Framework**: Powerful API construction.
*   **SQLite (Dev) / PostgreSQL (Prod)**: Database.
*   **Whitenoise**: Static file serving.

### Frontend
*   **React 18 + Vite**: Fast, modern frontend.
*   **TailwindCSS**: Utility-first styling.
*   **Lucide React**: Icons.

## 🏃‍♂️ Running Locally

### Prerequisites
*   Python 3.10+
*   Node.js 18+

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Backend runs on `http://localhost:8000`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on `http://localhost:5173`.

## 📂 Project Structure
*   `backend/`: Django project root.
    *   `api/`: REST API views, serializers, models.
    *   `core/`: Project settings & config.
*   `frontend/`: React application.
    *   `src/components/`: Reusable UI components.
    *   `src/api.js`: Centralized API handling.

## 🔧 Configuration
The project uses `python-dotenv` and environment variables for configuration.
See `DEPLOYMENT.md` for production setup.
