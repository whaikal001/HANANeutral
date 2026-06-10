# HANA Backend — log ingestion + admin dashboard

A tiny Flask + SQLite service that:

1. **Receives** interaction logs and session summaries POSTed by the HANA
   Ren'Py app (desktop **and** the Android build).
2. **Shows** them on a password-protected **web dashboard** so an admin can
   observe every user's *interaction logs* and *session summaries* from a
   browser — and export everything as CSV.

```
HANA app (PC / Android)  --HTTPS POST-->  this backend  -->  SQLite
                                                  |
                                          admin web dashboard (browser)
```

---

## 1. Run it locally (test on your PC first)

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open <http://localhost:5000> → log in with the default password **`hana-admin`**.

Send a fake row to confirm ingestion works:

```powershell
curl -X POST http://localhost:5000/api/interaction `
  -H "Content-Type: application/json" `
  -H "X-Ingest-Token: hana-secret-token" `
  -d '{"device_id":"test01","user_name":"Demo","session_id":"abc123","question":"How are you?","answer":"Good","empathy_mode":"affective"}'
```

Refresh the dashboard — the user "Demo" appears.

---

## 2. Deploy to a free always-on host

Pick **one**. PythonAnywhere is recommended because its free tier keeps the
SQLite file permanently (Render's free tier wipes the disk on every restart).

### Option A — PythonAnywhere (recommended, free, persistent SQLite)

1. Create a free account at <https://www.pythonanywhere.com>.
2. **Files** → upload the `backend/` folder (or clone your Git repo from a Bash
   console).
3. **Web** → *Add a new web app* → *Manual configuration* → *Python 3.x*.
4. In the **Virtualenv** section, create one and `pip install -r requirements.txt`.
5. Edit the **WSGI configuration file** (link on the Web tab). Replace its
   contents with:

   ```python
   import os, sys
   path = "/home/YOURNAME/backend"        # folder you uploaded
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ["ADMIN_PASSWORD"] = "choose-a-strong-password"
   os.environ["INGEST_TOKEN"]   = "choose-a-long-random-token"
   os.environ["SECRET_KEY"]     = "another-long-random-string"
   os.environ["HANA_DB_PATH"]   = "/home/YOURNAME/backend/hana.db"

   from wsgi import application
   ```

6. Click **Reload**. Your URL is `https://YOURNAME.pythonanywhere.com`.

### Option B — Render.com

1. Push this `backend/` folder to a GitHub repo.
2. Render → **New → Web Service** (or **Blueprint** using `render.yaml`).
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn wsgi:application`
3. Set env vars `ADMIN_PASSWORD`, `INGEST_TOKEN`, `SECRET_KEY`.
4. **Important:** the free tier has an *ephemeral* disk — logs are lost on
   restart. To keep data, use the paid `starter` plan with the disk defined in
   `render.yaml`, or switch to PythonAnywhere.

---

## 3. Point the HANA app at your server

In **`game/hana_sync.rpy`** set:

```renpy
define HANA_BACKEND_URL  = "https://YOURNAME.pythonanywhere.com"
define HANA_INGEST_TOKEN = "the-same-token-you-set-as-INGEST_TOKEN"
```

`HANA_INGEST_TOKEN` **must equal** the backend's `INGEST_TOKEN`, or posts are
rejected with HTTP 401. Leave `HANA_BACKEND_URL = ""` to disable syncing
entirely (local CSV logging still works).

Then rebuild the game / Android APK. The app already requests the `INTERNET`
permission (`android.json`), so no extra permission setup is needed.

> If logs never arrive **from Android only** and the desktop build works, it's
> almost always TLS certificate verification on the device. Set
> `define HANA_SYNC_INSECURE = True` in `hana_sync.rpy` as a fallback.

---

## Configuration (environment variables)

| Variable         | Default              | Purpose                                            |
|------------------|----------------------|----------------------------------------------------|
| `ADMIN_PASSWORD` | `hana-admin`         | Dashboard login password.                          |
| `INGEST_TOKEN`   | `hana-secret-token`  | Shared secret the app sends in `X-Ingest-Token`.   |
| `SECRET_KEY`     | random per boot      | Flask session signing. Set a fixed value in prod.  |
| `HANA_DB_PATH`   | `./hana.db`          | Where the SQLite database lives.                   |

**Change `ADMIN_PASSWORD` and `INGEST_TOKEN` before going live.**

## Endpoints

| Method | Path                                  | Auth         | Description                  |
|--------|---------------------------------------|--------------|------------------------------|
| POST   | `/api/interaction`                    | ingest token | Store one interaction row.   |
| POST   | `/api/summary`                        | ingest token | Store one session summary.   |
| GET    | `/api/health`                         | none         | Liveness check.              |
| GET    | `/dashboard`                          | login        | All users overview.          |
| GET    | `/user/<device_id>`                   | login        | One user's sessions.         |
| GET    | `/session/<device_id>/<session_id>`   | login        | One session's interactions.  |
| GET    | `/summaries`                          | login        | All session summaries.       |
| GET    | `/export/interactions.csv`            | login        | Download all interactions.   |
| GET    | `/export/summaries.csv`               | login        | Download all summaries.      |

## Privacy note

This stores conversation answers and stress/calm self-reports — sensitive data.
Use HTTPS (PythonAnywhere/Render give you that), keep your password/token
private, and make sure your participant consent covers central log collection.
