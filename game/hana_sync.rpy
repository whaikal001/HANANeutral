define HANA_BACKEND_URL = "https://wanhaikal001.pythonanywhere.com"
define HANA_INGEST_TOKEN = "14daa2406e9a4827b48f7ff2dd5fd446"
define HANA_SYNC_INSECURE = True 
define HANA_SYNC_TIMEOUT = 8        
define HANA_APP_TYPE = "neutral"

init python:

    import json as _hana_json
    import threading as _hana_threading
    import uuid as _hana_uuid
    import queue as _hana_queue
    import urllib.request as _hana_urlreq
    import ssl as _hana_ssl

    def hana_device_id():
        # Stable per-install id so the dashboard can tell devices/users apart.
        did = getattr(persistent, "hana_device_id", None)
        if not did:
            did = _hana_uuid.uuid4().hex[:12]
            persistent.hana_device_id = did
        return did

    _hana_q = _hana_queue.Queue()

    def _hana_enabled():
        return bool(HANA_BACKEND_URL)

    def _hana_do_post(endpoint, payload, insecure=False):
        url = HANA_BACKEND_URL.rstrip("/") + endpoint
        body = _hana_json.dumps(payload).encode("utf-8")
        req = _hana_urlreq.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("X-Ingest-Token", HANA_INGEST_TOKEN)
        ctx = None
        if insecure:
            ctx = _hana_ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = _hana_ssl.CERT_NONE
        else:
            try:
                import certifi
                ctx = _hana_ssl.create_default_context(cafile=certifi.where())
            except Exception:
                ctx = None
        resp = _hana_urlreq.urlopen(req, timeout=HANA_SYNC_TIMEOUT, context=ctx)
        return 200 <= resp.getcode() < 300

    def _hana_try_post(endpoint, payload):
        try:
            return _hana_do_post(endpoint, payload, insecure=False)
        except Exception:
            # Escape hatch for Android devices that can't verify the TLS chain.
            if HANA_SYNC_INSECURE:
                try:
                    return _hana_do_post(endpoint, payload, insecure=True)
                except Exception:
                    return False
            return False

    def _hana_save_failed(endpoint, payload):
        try:
            pending = list(getattr(persistent, "hana_unsent_logs", None) or [])
            pending.append({"e": endpoint, "p": payload})
            persistent.hana_unsent_logs = pending[-1000:]  # cap so it can't grow forever
        except Exception:
            pass

    def _hana_worker():
        while True:
            try:
                endpoint, payload = _hana_q.get()
            except Exception:
                continue
            ok = False
            try:
                if _hana_enabled():
                    ok = _hana_try_post(endpoint, payload)
            except Exception:
                ok = False
            if not ok and _hana_enabled():
                _hana_save_failed(endpoint, payload)
            try:
                _hana_q.task_done()
            except Exception:
                pass

    def hana_enqueue(endpoint, payload):
        if not _hana_enabled():
            return
        try:
            _hana_q.put((endpoint, payload))
        except Exception:
            pass

    def hana_flush_unsent():
        # Re-queue anything that failed on a previous run (e.g. offline session).
        if not _hana_enabled():
            return
        try:
            pending = list(getattr(persistent, "hana_unsent_logs", None) or [])
            persistent.hana_unsent_logs = []
            for item in pending:
                _hana_q.put((item.get("e"), item.get("p")))
        except Exception:
            pass

    def hana_sync_interaction(session_id, session_file, timestamp, question, answer,
                              score, stress_level, Ea, Ec, Ad, Be, D, Ep,
                              empathy_mode, extra=None):
        payload = {
            "device_id": hana_device_id(),
            "app_type": HANA_APP_TYPE,
            "user_name": (getattr(renpy.store, "user_name", "") or ""),
            "profile_id": getattr(renpy.store, "hana_active_profile_id", ""),
            "profile_slot": getattr(renpy.store, "hana_selected_profile_slot", ""),
            "session_id": session_id,
            "session_file": session_file,
            "client_ts": timestamp,
            "question": question,
            "answer": answer,
            "score": score,
            "stress_level": stress_level,
            "Ea": Ea, "Ec": Ec, "Ad": Ad, "Be": Be, "D": D, "Ep": Ep,
            "empathy_mode": empathy_mode,
        }
        if extra:
            payload.update(extra)
        hana_enqueue("/api/interaction", payload)

    def hana_sync_summary(session_id, session_file, timestamp, user_name,
                          start_stress_score, end_stress_score, stress_improvement,
                          final_calm_rating, modes_used, techniques_used,
                          total_interactions, session_duration_minutes, end_action,
                          stress_level="", empathy_mode="", intention_level="",
                          empathy_E="", support_need_announced=""):
        def _join(v):
            if isinstance(v, (list, tuple)):
                return "|".join(str(x) for x in v) if v else "none"
            return v
        payload = {
            "device_id": hana_device_id(),
            "app_type": HANA_APP_TYPE,
            "user_name": user_name or (getattr(renpy.store, "user_name", "") or ""),
            "profile_id": getattr(renpy.store, "hana_active_profile_id", ""),
            "profile_slot": getattr(renpy.store, "hana_selected_profile_slot", ""),
            "session_id": session_id,
            "session_file": session_file,
            "client_ts": timestamp,
            "start_stress_score": start_stress_score,
            "end_stress_score": end_stress_score,
            "stress_improvement": stress_improvement,
            "final_calm_rating": final_calm_rating,
            "modes_used": _join(modes_used),
            "techniques_used": _join(techniques_used),
            "total_interactions": total_interactions,
            "session_duration_minutes": session_duration_minutes,
            "end_action": end_action,
            "stress_level": stress_level,
            "empathy_mode": empathy_mode,
            "intention_level": intention_level,
            "empathy_E": empathy_E,
            "support_need_announced": support_need_announced,
        }
        hana_enqueue("/api/summary", payload)
        
init 999 python:
    try:
        _hana_thread = _hana_threading.Thread(target=_hana_worker, name="hana-sync", daemon=True)
        _hana_thread.start()
    except Exception:
        _hana_thread = None

    hana_flush_unsent()
