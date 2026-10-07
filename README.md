# HR Evaluation System

This project contains a Django REST API backend and a Vue 3 frontend for the HR evaluation system.

## Local development

### Backend

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The frontend reads `VITE_API_BASE_URL` for API requests. By default it calls the local backend on port 8000.

## Render deployment

This repo is prepared for a free Render deployment using a monorepo structure:

- Backend: Django web service
- Frontend: static web service
- Database: free Postgres instance

### 1) Create a GitHub repo

```bash
git init
git add .
git commit -m "Initial deployment setup"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2) Create Render services

1. Sign in to Render.
2. Click New + > Web Service.
3. Connect the GitHub repository.
4. Select the repo and choose the existing `render.yaml` file.
5. Render will create the backend service, frontend service, and database automatically.

### 3) Set environment values

If you do not use `render.yaml`, set these manually in Render:

Backend:
- `DJANGO_SECRET_KEY`
- `DEBUG=False`
- `FRONTEND_URL=https://your-frontend-url.onrender.com`
- `DATABASE_URL=<postgres-url>`

Frontend:
- `VITE_API_BASE_URL=https://your-backend-url.onrender.com`

## Notes

- The frontend is built with Vite and the built files are published from `frontend/dist`.
- The backend uses Django and serves API endpoints under `/api/`.
- The app assumes a CORS-safe same-origin setup when `VITE_API_BASE_URL` is missing.
