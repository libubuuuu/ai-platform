# Deployment Guide

## System Requirements

### Minimum
- CPU: 2 cores
- RAM: 4 GB
- Storage: 1 GB for the demo app and dependencies
- OS: Windows 10+, macOS 10.15+, Ubuntu 20.04+

### Recommended
- CPU: 4+ cores
- RAM: 8 GB+
- Storage: 5 GB+

## Local Development

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The API runs on `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm start
```

The UI runs on `http://localhost:3000`.

## Environment Variables

- `OWNER_ACCESS_TOKEN`: unlocks the owner-only publishing area. Default: `owner-demo-token`
- `REACT_APP_API_URL`: overrides the frontend API base URL

## Production Notes

- Run the backend as a process service with `python main.py` and keep it behind a reverse proxy.
- Build the frontend with `npm run build` and serve the generated static files from Nginx or another web server.
- Keep the backend on a private network and expose only the reverse proxy to the public internet.
- Use official or authorized platform integrations only.

## Operational Checklist

1. Set a strong owner token before production use.
2. Replace the in-memory store with a persistent database if you need real retention.
3. Connect real publishing APIs only through approved integrations.
4. Add monitoring and audit logging before opening the system to other users.
