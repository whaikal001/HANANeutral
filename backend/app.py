import os
import io
import csv
import json
import sqlite3
import secrets
from functools import wraps

from flask import (
    Flask, request, session, redirect, url_for,
    render_template, jsonify, Response, abort, g,
)

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "hana-admin")
INGEST_TOKEN = os.environ.get("INGEST_TOKEN", "hana-secret-token")
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))
DB_PATH = os.environ.get("HANA_DB_PATH", os.path.join(os.path.dirname(__file__), "hana.db"))

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

# Columns that make up an interaction row (besides server-side metadata).
INTERACTION_FIELDS = [
    "client_ts", "question", "answer", "score", "stress_level",
    "Ea", "Ec", "Ad", "Be", "D", "Ep", "empathy_mode",
]

SUMMARY_FIELDS = [
    "client_ts", "start_stress_score", "end_stress_score", "stress_improvement",
    "final_calm_rating", "modes_used", "techniques_used", "total_interactions",
    "session_duration_minutes", "end_action",
    "stress_level", "empathy_mode", "intention_level", "empathy_E",
    "support_need_announced",
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS interactions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            received_at     TEXT DEFAULT (datetime('now')),
            device_id       TEXT,
            user_name       TEXT,
            session_id      TEXT,
            session_file    TEXT,
            client_ts       TEXT,
            question        TEXT,
            answer          TEXT,
            score           TEXT,
            stress_level    TEXT,
            Ea              REAL,
            Ec              REAL,
            Ad              REAL,
            Be              REAL,
            D               REAL,
            Ep              REAL,
            empathy_mode    TEXT,
            extra           TEXT
        );

        CREATE TABLE IF NOT EXISTS summaries (
            id                       INTEGER PRIMARY KEY AUTOINCREMENT,
            received_at              TEXT DEFAULT (datetime('now')),
            device_id                TEXT,
            user_name                TEXT,
            session_id               TEXT,
            session_file             TEXT,
            client_ts                TEXT,
            start_stress_score       TEXT,
            end_stress_score         TEXT,
            stress_improvement       TEXT,
            final_calm_rating        TEXT,
            modes_used               TEXT,
            techniques_used          TEXT,
            total_interactions       TEXT,
            session_duration_minutes TEXT,
            end_action               TEXT,
            stress_level             TEXT,
            empathy_mode             TEXT,
            intention_level          TEXT,
            empathy_E                TEXT,
            support_need_announced   TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_inter_device  ON interactions(device_id);
        CREATE INDEX IF NOT EXISTS idx_inter_session ON interactions(session_id);
        CREATE INDEX IF NOT EXISTS idx_summ_device   ON summaries(device_id);
        """
    )

    # Lightweight migration: CREATE TABLE IF NOT EXISTS won't add new columns to a
    # summaries table that already exists on a deployed DB, so add any that are
    # missing. New columns default to NULL for older rows.
    existing_cols = {row[1] for row in db.execute("PRAGMA table_info(summaries)")}
    for col in ("stress_level", "empathy_mode", "intention_level",
                "empathy_E", "support_need_announced"):
        if col not in existing_cols:
            db.execute("ALTER TABLE summaries ADD COLUMN %s TEXT" % col)

    db.commit()
    db.close()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def check_ingest_token(req):
    token = req.headers.get("X-Ingest-Token", "")
    return secrets.compare_digest(token, INGEST_TOKEN)


@app.route("/api/interaction", methods=["POST"])
def api_interaction():
    if not check_ingest_token(request):
        return jsonify(ok=False, error="bad token"), 401

    data = request.get_json(silent=True) or {}

    # Anything outside the known columns is stashed in `extra` so we never lose
    # the enhanced-logging fields (Ea_history, struggle metrics, etc.).
    known = {"device_id", "user_name", "session_id", "session_file"} | set(INTERACTION_FIELDS)
    extra = {k: v for k, v in data.items() if k not in known}

    db = get_db()
    db.execute(
        """
        INSERT INTO interactions
            (device_id, user_name, session_id, session_file, client_ts,
             question, answer, score, stress_level,
             Ea, Ec, Ad, Be, D, Ep, empathy_mode, extra)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            data.get("device_id"), data.get("user_name"), data.get("session_id"),
            data.get("session_file"), data.get("client_ts"),
            data.get("question"), data.get("answer"), _s(data.get("score")),
            data.get("stress_level"),
            _f(data.get("Ea")), _f(data.get("Ec")), _f(data.get("Ad")),
            _f(data.get("Be")), _f(data.get("D")), _f(data.get("Ep")),
            data.get("empathy_mode"),
            json.dumps(extra) if extra else None,
        ),
    )
    db.commit()
    return jsonify(ok=True)


@app.route("/api/summary", methods=["POST"])
def api_summary():
    if not check_ingest_token(request):
        return jsonify(ok=False, error="bad token"), 401

    data = request.get_json(silent=True) or {}
    db = get_db()
    db.execute(
        """
        INSERT INTO summaries
            (device_id, user_name, session_id, session_file, client_ts,
             start_stress_score, end_stress_score, stress_improvement,
             final_calm_rating, modes_used, techniques_used,
             total_interactions, session_duration_minutes, end_action,
             stress_level, empathy_mode, intention_level, empathy_E,
             support_need_announced)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            data.get("device_id"), data.get("user_name"), data.get("session_id"),
            data.get("session_file"), data.get("client_ts"),
            _s(data.get("start_stress_score")), _s(data.get("end_stress_score")),
            _s(data.get("stress_improvement")), _s(data.get("final_calm_rating")),
            data.get("modes_used"), data.get("techniques_used"),
            _s(data.get("total_interactions")), _s(data.get("session_duration_minutes")),
            data.get("end_action"),
            data.get("stress_level"), data.get("empathy_mode"),
            data.get("intention_level"), _s(data.get("empathy_E")),
            _s(data.get("support_need_announced")),
        ),
    )
    db.commit()
    return jsonify(ok=True)


@app.route("/api/health")
def health():
    return jsonify(ok=True)


def _f(v):
    """Best-effort float; keeps NULLs as NULL."""
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _s(v):
    """Store scalars as text without turning None into the string 'None'."""
    if v is None:
        return None
    return str(v)

@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if secrets.compare_digest(request.form.get("password", ""), ADMIN_PASSWORD):
            session["admin"] = True
            return redirect(request.args.get("next") or url_for("dashboard"))
        error = "Wrong password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    users = db.execute(
        """
        SELECT
            device_id,
            MAX(user_name)                          AS user_name,
            COUNT(*)                                AS interactions,
            COUNT(DISTINCT session_id)              AS sessions,
            MAX(received_at)                        AS last_seen
        FROM interactions
        GROUP BY device_id
        ORDER BY last_seen DESC
        """
    ).fetchall()

    totals = db.execute(
        "SELECT COUNT(*) AS i, COUNT(DISTINCT device_id) AS d, "
        "COUNT(DISTINCT session_id) AS s FROM interactions"
    ).fetchone()
    summ_total = db.execute("SELECT COUNT(*) AS c FROM summaries").fetchone()["c"]

    return render_template(
        "dashboard.html", users=users, totals=totals, summ_total=summ_total
    )


@app.route("/user/<device_id>")
@login_required
def user_detail(device_id):
    db = get_db()
    sessions = db.execute(
        """
        SELECT
            session_id,
            MAX(user_name)  AS user_name,
            COUNT(*)        AS turns,
            MIN(client_ts)  AS started,
            MAX(client_ts)  AS ended
        FROM interactions
        WHERE device_id = ?
        GROUP BY session_id
        ORDER BY started DESC
        """,
        (device_id,),
    ).fetchall()

    summaries = db.execute(
        "SELECT * FROM summaries WHERE device_id = ? ORDER BY received_at DESC",
        (device_id,),
    ).fetchall()

    name = sessions[0]["user_name"] if sessions else device_id
    return render_template(
        "user.html", device_id=device_id, name=name,
        sessions=sessions, summaries=summaries,
    )


@app.route("/session/<device_id>/<session_id>")
@login_required
def session_detail(device_id, session_id):
    db = get_db()
    rows = db.execute(
        """
        SELECT * FROM interactions
        WHERE device_id = ? AND session_id = ?
        ORDER BY id ASC
        """,
        (device_id, session_id),
    ).fetchall()
    name = rows[0]["user_name"] if rows else ""
    return render_template(
        "session.html", rows=rows, device_id=device_id,
        session_id=session_id, name=name,
    )


@app.route("/summaries")
@login_required
def summaries():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM summaries ORDER BY received_at DESC"
    ).fetchall()
    return render_template("summaries.html", rows=rows)


@app.route("/export/interactions.csv")
@login_required
def export_interactions():
    return _export("interactions")


@app.route("/export/summaries.csv")
@login_required
def export_summaries():
    return _export("summaries")


def _export(table):
    db = get_db()
    rows = db.execute("SELECT * FROM %s ORDER BY id ASC" % table).fetchall()
    out = io.StringIO()
    writer = csv.writer(out)
    if rows:
        writer.writerow(rows[0].keys())
        for r in rows:
            writer.writerow([r[k] for k in r.keys()])
    return Response(
        out.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=%s.csv" % table},
    )


# Initialise the schema as soon as the module is imported, so it works both
# under `flask run`, `python app.py`, and WSGI hosting (gunicorn / PythonAnywhere).
init_db()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
