image bg room = "room.png"
#kucing tukar position
image room_cat_wake = Transform("room_catWakeup.png", xysize=(1920, 1080), fit="cover")
image room_cat_walk = Transform("room_catwalkaway.png", xysize=(1920, 1080), fit="cover")
image room_cat_shelf = Transform("room_catonshelf.png", xysize=(1920, 1080), fit="cover")
image bg room_cat:
    "room_cat_wake"
    pause 2.5
    "room_cat_walk"
    pause 1.6
    "room_cat_shelf"
image hana neutral = "Sprites/Neutral.png"
image hana smiling = "Sprites/Smiling.png"
image hana thinking:
    "Sprites/Thinking.png"
    pause renpy.random.uniform(0.6, 1.4)
    block:
        "Sprites/thinking_eyeclose.png"
        zoom 2.51
        pause 0.18
        "Sprites/Thinking.png"
        zoom 1.0
        pause renpy.random.uniform(2.4, 5.0)
        repeat
image hana sad = "Sprites/Sad.png"
image hana empathetic high = "Sprites/Empathetic high.png"
image hana empathetic low = "Sprites/Empathetic low.png"
image hana warm high = "Sprites/Warm high.png"
image hana warm low = "Sprites/Warm low.png"
image hana concerned high = "Sprites/Concerned high.png"
image hana concerned low = "Sprites/Concerned low.png"
image hana encouraging = "Sprites/Encouraging.png"
image hana good job = "Sprites/Good job.png"
image hana waving = "Sprites/Waving.png"
image hana hello = "Sprites/Waving.png"
image hana listening:
    "Sprites/Listening.png"
    pause renpy.random.uniform(0.6, 1.4)
    block:
        "Sprites/Listening_eyeclose.png"
        pause 0.18
        "Sprites/Listening.png"
        pause renpy.random.uniform(2.4, 5.0)
        repeat
image hana surprised = "Sprites/Thinking.png"

# method hana wink
image hana thinking eyeclose = "Sprites/thinking_eyeclose.png"
image hana listening eyeclose = "Sprites/Listening_eyeclose.png"

# scene extra untuk imagine
image beach = "beautifulbeach.jpg"
image beachscene = Movie(play="video/beachscene.webm")

# --- Hana Location transforms ---
transform hana_center:
    zoom 0.7
    xalign 1.0
    yanchor 0.925
    ypos 0.993

    on show:
        alpha 0.0
        linear 0.3 alpha 1.0
    on replace:
        linear 0.15 alpha 1.0
    on hide:
        alpha 1.0
        linear 0.3 alpha 0.0

transform hana_transition:
    zoom 0.7
    xalign 0.5
    yanchor 0.925
    ypos 0.993
    
    on show:
        alpha 0.0
        linear 0.3 alpha 1.0
    on replace:
        linear 0.15 alpha 1.0
    on hide:
        alpha 1.0
        linear 0.3 alpha 0.0

transform hana_quick_change:
    zoom 0.7
    xalign 0.5
    yanchor 0.925
    ypos 0.993
    linear 0.15 alpha 0.5
    linear 0.15 alpha 1.0

transform hana_center_listen:
    zoom 1.82
    xalign renpy.random.choice([0.10, 0.22, 0.34])
    yanchor 0.912
    ypos 0.993

    on show:
        alpha 0.0
        linear 0.3 alpha 1.0
    on replace:
        linear 0.15 alpha 1.0
    on hide:
        alpha 1.0
        linear 0.3 alpha 0.0

# --- Random scene position transforms ---
transform hana_left:
    zoom 0.7
    xalign 0.1
    yanchor 0.925
    ypos 0.993
    on show:
        alpha 0.0
        linear 0.3 alpha 1.0
    on replace:
        linear 0.15 alpha 1.0
    on hide:
        alpha 1.0
        linear 0.3 alpha 0.0

transform hana_mid:
    zoom 0.7
    xalign 0.5
    yanchor 0.925
    ypos 0.993
    on show:
        alpha 0.0
        linear 0.3 alpha 1.0
    on replace:
        linear 0.15 alpha 1.0
    on hide:
        alpha 1.0
        linear 0.3 alpha 0.0

transform hana_right:
    zoom 0.7
    xalign 0.9
    yanchor 0.925
    ypos 0.993
    on show:
        alpha 0.0
        linear 0.3 alpha 1.0
    on replace:
        linear 0.15 alpha 1.0
    on hide:
        alpha 1.0
        linear 0.3 alpha 0.0

# guna bila method imaginary
transform scene_right:
    zoom 0.5
    xalign 0.95
    yalign 0.5
    on show:
        alpha 0.0
        xoffset 80
        linear 0.6 alpha 1.0 xoffset 0
    on replace:
        linear 0.2 alpha 1.0 xoffset 0
    on hide:
        alpha 1.0
        linear 0.4 alpha 0.0 xoffset 80

init python:
    import math
    import random
    import datetime, csv, uuid, os

    def _hana_writable_log_dir():
        candidates = []
        for base in (getattr(config, "basedir", None), getattr(config, "savedir", None)):
            if base:
                candidates.append(os.path.join(base, "logs"))
        for d in candidates:
            try:
                os.makedirs(d, exist_ok=True)
                test = os.path.join(d, ".write_test")
                with open(test, "w") as _wf:
                    _wf.write("ok")
                os.remove(test)
                return d
            except Exception:
                continue
        try:
            import tempfile
            d = os.path.join(tempfile.gettempdir(), "hana_logs")
            os.makedirs(d, exist_ok=True)
            return d
        except Exception:
            return getattr(config, "savedir", ".") or "."

    DROPBOX_LOG_DIR = _hana_writable_log_dir()

    def generate_session_id():
        return str(uuid.uuid4())[:8]

    def make_session_filename():
        return f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    def log_interaction(session_filename, session_id, question, answer,
                        score=None, stress_level=None,
                        Ea=None, Ec=None, Ad=None, Be=None, D=None, Ep=None,
                        empathy_mode=None):

        log_path = os.path.join(DROPBOX_LOG_DIR, session_filename)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [
            timestamp, session_id, question, answer, score, stress_level,
            Ea, Ec, Ad, Be, D, Ep, empathy_mode
        ]

        try:
            write_header = not os.path.exists(log_path)
            with open(log_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow([
                        "timestamp","session_id","question","answer","score",
                        "stress_level","Ea","Ec","Ad","Be","D","Ep","empathy_mode"
                    ])
                writer.writerow(row)
        except Exception:
            pass  
        try:
            hana_sync_interaction(
                session_id, session_filename, timestamp, question, answer,
                score, stress_level, Ea, Ec, Ad, Be, D, Ep, empathy_mode,
            )
        except Exception:
            pass

    def log_interaction_enhanced(session_filename, session_id, question, answer,
                        score=None, stress_level=None,
                        Ea=None, Ec=None, Ad=None, Be=None, D=None, Ep=None,
                        empathy_mode=None, Ea_history=None, user_struggles=None, 
                        struggle_intensity=None, mode_shift_count=None, current_mode=None):
        
        log_path = os.path.join(DROPBOX_LOG_DIR, session_filename)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format Ea_history for logging
        ea_hist_str = "|".join([f"{x:.3f}" for x in (Ea_history or [])]) if Ea_history else ""
        
        row = [
            timestamp, session_id, question, answer, score, stress_level,
            Ea, Ec, Ad, Be, D, Ep, empathy_mode,
            ea_hist_str, user_struggles, struggle_intensity, mode_shift_count, current_mode
        ]
        
        try:
            write_header = not os.path.exists(log_path)
            with open(log_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow([
                        "timestamp","session_id","question","answer","score",
                        "stress_level","Ea","Ec","Ad","Be","D","Ep","empathy_mode",
                        "Ea_history","user_struggles","struggle_intensity","mode_shift_count","current_mode"
                    ])
                writer.writerow(row)
        except Exception:
            pass  

        try:
            hana_sync_interaction(
                session_id, session_filename, timestamp, question, answer,
                score, stress_level, Ea, Ec, Ad, Be, D, Ep, empathy_mode,
                extra={
                    "Ea_history": ea_hist_str,
                    "user_struggles": user_struggles,
                    "struggle_intensity": struggle_intensity,
                    "mode_shift_count": mode_shift_count,
                    "current_mode": current_mode,
                },
            )
        except Exception:
            pass

    def log_session_summary(session_filename, session_id, user_name,
                           start_stress_score, end_stress_score,
                           modes_used, techniques_used, total_interactions,
                           final_calm_rating, session_duration_minutes, end_action,
                           stress_improvement=None,
                           stress_level="", empathy_mode="", intention_level="",
                           empathy_E="", support_need_announced=""):


        log_path = os.path.join(DROPBOX_LOG_DIR, "session_summaries.csv")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # calculatee stress
        if stress_improvement is None:
            stress_improvement = start_stress_score - end_stress_score if start_stress_score else 0

        modes_str = "|".join(modes_used) if modes_used else "none"
        techniques_str = "|".join(techniques_used) if techniques_used else "none"

        row = [
            timestamp, session_id, user_name, start_stress_score, end_stress_score,
            stress_improvement, final_calm_rating, modes_str, techniques_str,
            total_interactions, session_duration_minutes, end_action,
            stress_level, empathy_mode, intention_level, empathy_E, support_need_announced
        ]

        header = [
            "timestamp", "session_id", "user_name", "start_stress_score", "end_stress_score",
            "stress_improvement", "final_calm_rating", "modes_used", "techniques_used",
            "total_interactions", "session_duration_minutes", "end_action",
            "stress_level", "empathy_mode", "intention_level", "empathy_E", "support_need_announced"
        ]
        pending_path = os.path.join(DROPBOX_LOG_DIR, "session_summaries_pending.csv")
        for target in (log_path, pending_path):
            try:
                write_header = not os.path.exists(target)
                with open(target, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if write_header:
                        writer.writerow(header)
                    writer.writerow(row)
                break
            except Exception:
                continue
        try:
            hana_sync_summary(
                session_id, session_filename, timestamp, user_name,
                start_stress_score, end_stress_score, stress_improvement,
                final_calm_rating, modes_used, techniques_used,
                total_interactions, session_duration_minutes, end_action,
                stress_level, empathy_mode, intention_level,
                empathy_E, support_need_announced,
            )
        except Exception:
            pass


    def profile_key_for(name):
        return name.strip().lower()

    def default_user_profile(name):
        return {
            "name": name,
            "visit_count": 0,
            "last_session_id": "",
            "last_stress_score": None,
            "last_stress_level": "unknown",
            "last_empathy_mode": "unknown",
            "last_intention_level": "unknown",
            "last_empathy_E": 0.0,
            "last_calm_rating": None,
            "last_technique": None,
            "last_end_action": "",
            "support_need_announced": False,
            "music_enabled": None,  # None = never asked; True/False = saved preference
        }

    def load_user_profile(name):
        profile_store = getattr(persistent, "hana_user_memory", None) or {}
        key = profile_key_for(name)
        profile = default_user_profile(name)

        if key in profile_store:
            profile.update(profile_store[key])

        return key, profile_store, profile

    def save_user_profile(name, updates):
        profile_store = getattr(persistent, "hana_user_memory", None) or {}
        key = profile_key_for(name)
        profile = default_user_profile(name)

        if key in profile_store:
            profile.update(profile_store[key])

        profile.update(updates)
        profile_store[key] = profile
        persistent.hana_user_memory = profile_store
        return profile

#profile menu bole pilih
    PROFILE_SLOT_COUNT = 6

    def profile_slot_key(slot_index):
        return "slot_%d" % int(slot_index)

    def default_profile_slot(slot_index):
        return {
            "slot_index": int(slot_index),
            "profile_id": "",
            "name": "",
            "visit_count": 0,
            "last_session_id": "",
            "last_stress_level": "unknown",
            "last_calm_rating": None,
        }

    def load_profile_slot(slot_index):
        slot_store = getattr(persistent, "hana_profile_slots", None) or {}
        key = profile_slot_key(slot_index)
        slot = default_profile_slot(slot_index)

        if key in slot_store:
            slot.update(slot_store[key])

        return key, slot_store, slot

    def save_profile_slot(slot_index, updates):
        slot_store = getattr(persistent, "hana_profile_slots", None) or {}
        key = profile_slot_key(slot_index)
        slot = default_profile_slot(slot_index)

        if key in slot_store:
            slot.update(slot_store[key])

        slot.update(updates)
        slot_store[key] = slot
        persistent.hana_profile_slots = slot_store
        return slot

    def get_or_create_profile_id(slot_index):
        key, slot_store, slot = load_profile_slot(slot_index)
        pid = (slot.get("profile_id", "") or "").strip()
        if not pid:
            pid = uuid.uuid4().hex
            save_profile_slot(slot_index, {"profile_id": pid})
        return pid

    def delete_profile_slot(slot_index):
        slot_store = getattr(persistent, "hana_profile_slots", None) or {}
        key = profile_slot_key(slot_index)

        slot = slot_store.get(key)
        if slot:
            name = (slot.get("name", "") or "").strip()
            if name:
                profile_store = getattr(persistent, "hana_user_memory", None) or {}
                pkey = profile_key_for(name)
                if pkey in profile_store:
                    del profile_store[pkey]
                    persistent.hana_user_memory = profile_store
            del slot_store[key]
            persistent.hana_profile_slots = slot_store

        renpy.restart_interaction()

    def cleanup_unfinished_profile_slots():
        slot_store = getattr(persistent, "hana_profile_slots", None) or {}
        profile_store = getattr(persistent, "hana_user_memory", None) or {}
        changed = False

        for i in range(1, PROFILE_SLOT_COUNT + 1):
            key = profile_slot_key(i)
            slot = slot_store.get(key)
            if not slot:
                continue
            name = (slot.get("name", "") or "").strip()
            if name and slot.get("visit_count", 0) <= 0:
                pkey = profile_key_for(name)
                # only drop the user memory if it also never completed a session
                if pkey in profile_store and profile_store[pkey].get("visit_count", 0) <= 0:
                    del profile_store[pkey]
                del slot_store[key]
                changed = True

        if changed:
            persistent.hana_profile_slots = slot_store
            persistent.hana_user_memory = profile_store

    def profile_slot_title(slot_index):
        dummy1, dummy2, slot = load_profile_slot(slot_index)
        name = slot.get("name", "").strip()

        if name:
            return name

        return "Profile %d" % int(slot_index)

    def profile_slot_summary(slot_index):
        dummy1, dummy2, slot = load_profile_slot(slot_index)
        visit_count = slot.get("visit_count", 0)
        last_stress_level = slot.get("last_stress_level", "unknown")
        last_calm_rating = slot.get("last_calm_rating", None)

        if visit_count <= 0 and last_stress_level == "unknown" and last_calm_rating is None:
            return "New slot"

        calm_text = "unknown" if last_calm_rating is None else str(last_calm_rating)
        return "Visits: %d | Stress: %s | Calm: %s" % (visit_count, last_stress_level, calm_text)

    def profile_save_page(slot_index):
        return "profile_%d" % int(slot_index)
    # --- Update functions ---
    def clamp01(x):
        return max(0.0, min(1.0, x))

    def clamp_range(x, lo, hi):
        return max(lo, min(hi, x))

    def compassionate_category(Be, theta_be=0.5, theta_be_high=0.8):
        if Be >= theta_be_high:
            return "high"
        if Be >= theta_be:
            return "low"
        return None
    def classify_user_condition(stress_score_value, stress_level_value):
        if stress_level_value == "Extremely severe" or stress_score_value >= 34:
            return "Extremely severe distress"
        if stress_level_value == "Severe" or stress_score_value >= 26:
            return "Severe distress"
        if stress_level_value == "Moderate" or stress_score_value >= 19:
            return "Moderate distress"
        if stress_level_value == "Mild" or stress_score_value >= 15:
            return "Mild distress"
        return "Normal"

    def repeated_prolonged_distress_detected(condition, calm_rating_value, support_announced):
        if not support_announced:
            return False
        if calm_rating_value is None:
            return condition in ["Severe distress", "Extremely severe distress"]
        return calm_rating_value <= 2 and condition in ["Moderate distress", "Severe distress", "Extremely severe distress"]

    def feedback_signal_from_rating(calm_rating_value):
        if calm_rating_value is None:
            return "neutral"
        if calm_rating_value <= 2:
            return "negative"
        if calm_rating_value >= 4:
            return "positive"
        return "neutral"

    def update_empathy_policy_from_feedback(strategy_name, intensity_name, expression_name, feedback_signal):
        return {}

    def get_animation_transition():
        return "hana_transition"

    def get_quick_expression_change():
        return "hana_quick_change"

    def adapt_weights_from_feedback(calm_rating, s_in):
        return
    def show_hana_with_fade(expression, at_position="hana_center"):
        renpy.show(f"hana {expression} at {at_position}")
        renpy.transition(hana_quick_change)

    def pick_random_scene_pos():
        return renpy.random.choice([hana_left, hana_mid, hana_right])

# method nak clean menu function sebab nak bg main menu clear and bukan ingame
init 999 python:
    cleanup_unfinished_profile_slots()

default support_need_announced = False
default compassion_cooldown_steps = 0
default last_calm_rating = None
default calm_rated_this_session = False
default last_technique = None
default calming_done = False  
default feedback_given = False  
default avoid_technique_first = None  
default struggle_intensity = 0  
default mode_shift_reason = "" 
default quick_menu = True

# --- Characters ---
define e = Character("Hana", color="#b56ab3")

# =========================
# STATE VARIABLES
# =========================
default stress_level = "Normal"
default stress_level_desc = "Normal"
default last_empathy_mode = "neutral"
default day_impact = ""
default routine_stress = ""
default extra_weight = ""

default feedback = 0.0

default modes_used_list = []  # Track all modes used in session
default techniques_used_list = []  # Track all techniques used in session
default session_start_stress = 0  # Initial stress score
default initial_stress_score = 0  # For reference
default interaction_count = 0  # Count of logged interactions
default session_start_time = None  # Track session duration

default session_id = ""
default session_filename = ""

default last_intention_level = "neutral"
default last_empathy_E = 0.0

default stress_score = 0
default checkin_s_in_history = []
default hana_selected_profile_slot = 1
default hana_active_profile_id = ""
default hana_pos = hana_mid

# --- Flow Starts ---


# fade transition ubah muka
label hana_wave:
    show hana neutral at hana_pos
    with Fade(0.3, 0.0, 0.3)
    return

label hana_smile:
    show hana neutral at hana_pos
    with Fade(0.3, 0.0, 0.3)
    return

label hana_listen:
    show hana listening at hana_pos
    with Fade(0.3, 0.0, 0.3)
    return

label hana_listen_wink:
    show hana listening at hana_pos
    with Fade(0.3, 0.0, 0.3)
    return

label hana_thinking_wink:
    show hana neutral at hana_pos
    with Fade(0.3, 0.0, 0.3)
    return

label hana_neutral:
    show hana neutral at hana_pos
    with Fade(0.3, 0.0, 0.3)
    return

label hana_concern_low:
    show hana neutral at hana_pos
    with Fade(0.3, 0.0, 0.3)
    return

label hana_concern_high:
    show hana neutral at hana_pos
    with Fade(0.3, 0.0, 0.3)
    return

label hana_encouraging:
    show hana neutral at hana_pos
    with Fade(0.3, 0.0, 0.3)
    return

label hana_good_job:
    show hana neutral at hana_pos
    with Fade(0.3, 0.0, 0.3)
    return

label start:

    scene black
    with fade
    centered "Disclaimer:\n\nThis session uses some questions from the Depression Anxiety Stress Scales (DASS), specifically the stress subscale. \
    These items are included for research and educational purposes only, and are not a substitute for professional diagnosis or treatment."

    scene bg room_cat
    show black:
        alpha 0.6
    with fade
#ni critical part if error sume tak jalan
    # nak clear slot yang session tak settle abis
    $ cleanup_unfinished_profile_slots()
    $ session_id = generate_session_id()
    $ session_filename = make_session_filename()
    $ checkin_s_in_history = []
    $ modes_used_list = []
    $ techniques_used_list = []
    $ interaction_count = 0
    $ calming_done = False
    $ calm_rated_this_session = False
    $ feedback_given = False
    $ session_start_time = datetime.datetime.now()
    $ selected_slot = clamp_range(hana_selected_profile_slot, 1, PROFILE_SLOT_COUNT)
    $ dummy1, dummy2, selected_slot_data = load_profile_slot(selected_slot)
    $ user_name = selected_slot_data.get("name", "").strip()
    $ hana_selected_profile_slot = selected_slot
    $ hana_active_profile_id = get_or_create_profile_id(selected_slot)
    $ hana_pos = hana_mid

    if user_name:
        $ user_profile_key, user_profile_store, user_profile = load_user_profile(user_name)
    else:
        $ user_profile_key, user_profile_store, user_profile = None, None, {}
    $ is_returning_user = user_profile.get("visit_count", 0) > 0
    $ last_stress_level = user_profile.get("last_stress_level", "unknown")
    $ prev_calm_rating = user_profile.get("last_calm_rating", None)
    # carry last visit's state forward so repeated_prolonged_distress_detected() can fire
    $ last_calm_rating = prev_calm_rating
    $ support_need_announced = user_profile.get("support_need_announced", False)
    $ prev_technique = user_profile.get("last_technique", None)
    $ prev_empathy_mode = user_profile.get("last_empathy_mode", "unknown")
    $ prev_intention_level = user_profile.get("last_intention_level", "unknown")

    # guna dkt technique nnti nak avoid same user dpt technique sama
    $ avoid_technique_first = prev_technique

    # idea dr azizi mintak user preference if nk guna music ke tak
    $ music_pref = user_profile.get("music_enabled", None)
    if music_pref:
        play music "audio/BGM/Hana_lofi.mp3" volume 0.3 fadein 3.0 loop

    # 2 flow (user baru or lama)
    if is_returning_user:
    
        show hana neutral at hana_pos
        e "Welcome back, [user_name]."
        show hana neutral at hana_pos
        with Fade(0.3, 0.0, 0.3)
        if last_stress_level in ["Moderate", "Severe", "Extremely severe"]:
            e "Your last recorded stress level was in the higher range."
        else:
            e "Your last recorded stress level was in the lower range."
    else:
        
        show hana neutral at hana_pos
        e "Hi, I'm Hana."
        if not user_name:
            show hana neutral at hana_pos
            with Fade(0.3, 0.0, 0.3)
            e "And you are..?"
            show hana neutral at hana_pos
            $ user_name = renpy.input("")
            $ user_name = user_name.strip().title() if user_name.strip() else "friend"
            $ save_profile_slot(selected_slot, {"name": user_name})
            $ user_profile_key, user_profile_store, user_profile = load_user_profile(user_name)

        show hana neutral at hana_pos
        with Fade(0.3, 0.0, 0.3)
        e "Hello, [user_name]."
        show hana neutral at hana_pos
        with Fade(0.3, 0.0, 0.3)

        e "My name means \"flower\" in Japanese and \"happiness\" in Arabic."
       
        menu:
            "Nice to meet you too, Hana.":
                show hana neutral at hana_pos
 
                e "Let's begin."
            "That's a really pretty name.":
                show hana neutral at hana_pos

                e "Thank you. Let's begin."
            "...Hi.":
                show hana neutral at hana_pos
 
                e "Alright. Let's begin."

    # line mintak user nak music ke tak
    if music_pref is None:
        show hana neutral at hana_pos
        with Fade(0.3, 0.0, 0.3)
        e "Before we continue, would you like background music during this session?"
        e "You can choose either."

        menu:
            "Yes, music would be nice":
                $ music_pref = True
                show hana neutral at hana_pos
                e "Music will play in the background."
                play music "audio/BGM/Hana_lofi.mp3" volume 0.2 fadein 3.0 loop

            "No, I'd prefer quiet":
                $ music_pref = False
                show hana neutral at hana_pos
                e "No music will play."

        $ user_profile = save_user_profile(user_name, {"music_enabled": music_pref})
        $ log_interaction(session_filename, session_id,
                          "Music preference", "music_on" if music_pref else "music_off",
                          None, None, None, None, None, None, None, None, "preference")

    hide black
    with Dissolve(0.5)

 #greeting and check-in

    show hana neutral at hana_pos

    e "So, [user_name], how have you been feeling today?"
    menu:
        "I'm feeling good":
            $ ans = "I'm feeling good"
            $ s_in = 0.0
        "Pretty okay overall":
            $ ans = "Pretty okay overall"
            $ s_in = 0.33
        "A bit stressed":
            $ ans = "A bit stressed"
            $ s_in = 0.67
        "Really overwhelmed":
            $ ans = "Really overwhelmed"
            $ s_in = 1.0

    $ checkin_s_in_history.append(s_in)
    call empathy_step("How have you been feeling today?", ans, s_in, "checkin_q1", speak=False) from _checkin_q1

    show hana neutral at hana_pos
    e "How has your day been so far?"
    menu:
        "Being productive and getting things done":
            $ ans = "Being productive and getting things done"
            $ s_in = 0.0
        "Relaxing and enjoying some me-time":
            $ ans = "Relaxing and enjoying some me-time"
            $ s_in = 0.0
        "Feeling exhausted from everything":
            $ ans = "Feeling exhausted from everything"
            $ s_in = 0.67
        "Honestly, it's been a rough day":
            $ ans = "Honestly, it's been a rough day"
            $ s_in = 1.0

    $ checkin_s_in_history.append(s_in)
    call empathy_step("How has your day been so far?", ans, s_in, "checkin_q2", speak=False) from _checkin_q2

    show hana neutral at hana_pos
    e "Did anything feel stressful or frustrating for you today?"
    menu:
        "Not really":
            $ ans = "Not really"
            $ s_in = 0.0
        "A little bit":
            $ ans = "A little bit"
            $ s_in = 0.33
        "Quite a lot":
            $ ans = "Quite a lot"
            $ s_in = 0.67
        "Almost all day":
            $ ans = "Almost all day"
            $ s_in = 1.0

    $ checkin_s_in_history.append(s_in)
    call empathy_step("Did anything feel stressful or frustrating for you today?", ans, s_in, "checkin_q3", speak=False) from _checkin_q3

    show hana neutral at hana_pos
    e "One more question before we continue."
    e "What's something that has gone well for you recently?"
    menu:
        "I accomplished something important":
            $ ans = "I accomplished something important"
            $ s_in = 0.0
        "I had a nice moment with someone":
            $ ans = "I had a nice moment with someone"
            $ s_in = 0.0
        "I can't really think of anything":
            $ ans = "I can't really think of anything"
            $ s_in = 0.5
        "Honestly, it's been hard lately":
            $ ans = "Honestly, it's been hard lately"
            $ s_in = 1.0

    $ checkin_s_in_history.append(s_in)
    call empathy_step("What's something that has gone well for you recently?", ans, s_in, "checkin_q4", speak=False) from _checkin_q4

    show hana neutral at hana_pos
    jump stress_input

# =======================================================
# Reusable empathy step:
#   1) Update Ea, Ec, Ad, Be from latest intensity signal s_in
#   2) Select empathy mode
#   3) Speak ONE inline empathy line of the matching type
#   4) Log everything
# =======================================================
label empathy_step(question, ans, s_in, phase, speak=True):
    $ interaction_count += 1
    $ last_empathy_mode = "neutral"
    $ log_interaction(session_filename, session_id, question, ans,
                      None, stress_level, None, None, None, None, None, None,
                      "neutral_" + phase)
    return


# --- Stress input capture ---
label stress_input:
    $ hana_pos = pick_random_scene_pos()
    $ stress_questions = [
        "After a long day, do you find it tricky to calm down?",
        "Do small things sometimes feel bigger than they are?",
        "Do you ever feel like you're running on nervous energy?",
        "Do you catch yourself getting restless more easily?",
        "Is it hard to fully let go and feel settled?",
        "If something interrupts you, does frustration creep in quickly?",
        "Do you sometimes feel extra sensitive or touchy?"
    ]

    $ stress_responses = []
    $ i = 0

    while i < len(stress_questions):
        $ q = stress_questions[i]
        $ hana_pos = pick_random_scene_pos()
        show hana neutral at hana_pos
        e "[q!t]"

        menu:
            "Not really, that doesn't apply to me":
                $ stress_responses.append(0)
                $ ans = "Not really"
                $ s_in = 0.0

            "Maybe a little, once in a while":
                $ stress_responses.append(1)
                $ ans = "Maybe a little"
                $ s_in = 0.33

            "Yes, quite a lot of the time":
                $ stress_responses.append(2)
                $ ans = "Quite a lot"
                $ s_in = 0.67

            "Almost always":
                $ stress_responses.append(3)
                $ ans = "Almost always"
                $ s_in = 1.0

        call empathy_step(q, ans, s_in, "screening_q" + str(i+1), speak=False) from _screening_step

        show hana neutral at hana_pos
        $ i += 1


    $ hi_count = sum(1 for r in stress_responses if r >= 2)
    show hana neutral at hana_pos
    e "Thank you for answering those questions."

    show hana neutral at hana_pos

    # Compute scale from formula:
    # normalized_scale = raw_score / (number_of_items * max_item_score)
    # stress_score = normalized_scale * 42  (DASS-21 equivalent stress range)
    $ raw_score = sum(stress_responses)
    $ max_raw = float(len(stress_questions) * 3)
    $ stress_scale = (raw_score / max_raw) if max_raw > 0 else 0.0
    $ stress_score = int(round(stress_scale * 42.0))
    $ session_start_stress = stress_score
    $ initial_stress_score = stress_score  
    $ prev_end_stress = user_profile.get("last_stress_score", None) if user_profile else None
    if is_returning_user and prev_end_stress is not None:
        $ session_start_stress = prev_end_stress

    if stress_score <= 14:
        $ stress_level = "Normal"
    elif stress_score <= 18:
        $ stress_level = "Mild"
    elif stress_score <= 25:
        $ stress_level = "Moderate"
    elif stress_score <= 33:
        $ stress_level = "Severe"
    else:
        $ stress_level = "Extremely severe"
    $ stress_level_desc = stress_level
    show hana neutral at hana_pos

    $ log_interaction(session_filename, session_id, "Stress score summary", str(raw_score),
                stress_score, stress_level_desc, None, None, None, None, None, None, "stress_summary")

    # NEUTRAL: route by the measured stress level only. No empathy weighting,
    # no intention scoring, no learning.
    $ last_empathy_mode = "neutral"
    $ last_intention_level = "neutral"
    if "neutral" not in modes_used_list:
        $ modes_used_list.append("neutral")
    if stress_level in ["Moderate", "Severe", "Extremely severe"]:
        $ support_need_announced = True

    # Extremely severe: provide safety information, then go to a calming exercise.
    if stress_level == "Extremely severe":
        show hana neutral at hana_pos
        e "If you ever feel unsafe, contact Befrienders or a healthcare professional. You do not have to handle this alone."
        e "Let's start with a short calming exercise."
        call calming_loop from _reactive_calming_loop
        $ calming_done = True
        jump session_end_loop

    # Moderate / Severe: identify the main stressors, then give practical steps.
    if stress_level in ["Moderate", "Severe"]:
        show hana neutral at hana_pos
        e "Let's look at what's been adding to the stress so I can suggest a few practical steps."
        show hana neutral at hana_pos
        call affective_input from _stress_affective_input
        jump session_end_loop

    # Normal or mild stress
    else:
        jump session_end_loop


# option nk continue ke end

label session_end_loop:
    $ hana_pos = pick_random_scene_pos()
    $ session_done = False

    if calming_done:
        $ continue_session = True
        while continue_session:
            show hana neutral at hana_pos
            e "That exercise is complete."
            e "You can do another coping exercise, or end the session here."

            menu:
                "I'd like to keep going a little longer":
                    $ log_interaction(
                        session_filename, session_id,
                        "Session menu", "continue_coping",
                        stress_score, stress_level_desc, None, None, None, None, None, None,
                        "session_loop"
                    )
                    call calming_loop from _continue_calming_loop

                "I think that's enough for me today":
                    if not feedback_given:
                        call post_response(last_empathy_mode) from _end_post_response
                    $ log_interaction(
                        session_filename, session_id,
                        "Session menu", "end_after_feedback",
                        stress_score, stress_level_desc, None, None, None, None, None, None,
                        "session_loop"
                    )
                    $ continue_session = False

        call phase5_close_update("exit_after_calming") from _phase5_after_calming
        return

    while not session_done:
        # Normal / Mild stress
        if stress_level in ["Normal", "Mild"]:
            show hana neutral at hana_pos
            e "Before we finish, you could try a short breathing exercise."
            e "Would you like to give it a try?"

            menu:
                "Yes, let's try it":
                    $ log_interaction(
                        session_filename, session_id,
                        "Session menu", "continue_to_guidance",
                        stress_score, stress_level_desc, None, None, None, None, None, None,
                        "session_loop"
                    )
                    call calming_loop from _session_end_calming_loop
                    $ calming_done = True
                    if not feedback_given:
                        call post_response(last_empathy_mode) from _guided_post_response
                    call phase5_close_update("guided") from _phase5_after_guided
                    $ session_done = True

                "No, I'm okay for today":
                    $ log_interaction(
                        session_filename, session_id,
                        "Session menu", "exit",
                        stress_score, stress_level_desc, None, None, None, None, None, None,
                        "session_loop"
                    )
                    call post_response(last_empathy_mode, "Did checking in today feel helpful?") from _decline_post_response
                    call phase5_close_update("exit") from _phase5_exit
                    $ session_done = True

        # Moderate or severe yg tak lepas calming loop
        else:
            show hana neutral at hana_pos
            e "Before we finish, you could try a short calming exercise."
            e "Would you like to give it a try?"

            menu:
                "Yes, let's try it":
                    $ log_interaction(
                        session_filename, session_id,
                        "Session menu", "continue_to_guidance",
                        stress_score, stress_level_desc, None, None, None, None, None, None,
                        "session_loop"
                    )
                    call calming_loop from _session_end_calming_loop_ms
                    $ calming_done = True
                    if not feedback_given:
                        call post_response(last_empathy_mode) from _guided_post_response_ms
                    call phase5_close_update("guided") from _phase5_after_guided_ms
                    $ session_done = True

                "No, I'm okay for today":
                    $ log_interaction(
                        session_filename, session_id,
                        "Session menu", "exit",
                        stress_score, stress_level_desc, None, None, None, None, None, None,
                        "session_loop"
                    )
                    call post_response(last_empathy_mode) from _decline_post_response_ms
                    call phase5_close_update("exit") from _phase5_exit_ms
                    $ session_done = True

    return

# --- Affective empathy input ---
label affective_input:
    $ hana_pos = pick_random_scene_pos()
    show hana neutral at hana_pos
    $ affective_responses = []
    $ q = "How has this stress been affecting your day-to-day life recently?"
    e "[q!t]"

    menu:
        "It has been hard to focus on daily tasks.":
            $ day_impact = "focus"
            $ ans = "Hard to focus on daily tasks"
            $ aff_score = 1
            show hana neutral at hana_pos
            e "For difficulty focusing, breaking tasks into smaller steps and completing one at a time is a practical way to stay on track."

        "I feel mentally drained most of the time.":
            $ day_impact = "drained"
            $ ans = "Mentally drained most of the time"
            $ aff_score = 3
            show hana neutral at hana_pos
            e "For mental fatigue, scheduling short rest breaks between tasks helps maintain your energy through the day."

        "I keep worrying even when I try to do other things.":
            $ day_impact = "worry"
            $ ans = "Keeps worrying during other things"
            $ aff_score = 2
            show hana neutral at hana_pos
            e "For persistent worry, setting aside a fixed time to address concerns keeps them from interrupting other activities."

        "It has affected my sleep, rest, or mood.":
            $ day_impact = "sleep_mood"
            $ ans = "Affected sleep, rest, or mood"
            $ aff_score = 3
            show hana neutral at hana_pos
            e "For disrupted sleep, keeping a consistent sleep schedule and limiting screens before bed can improve rest."

    $ affective_responses.append(aff_score)
    $ s_in = aff_score / 3.0
    call empathy_step(q, ans, s_in, "affective_followup_q1", speak=False) from _aff_followup_q1

    $ hana_pos = pick_random_scene_pos()
    show hana neutral at hana_pos
    $ q = "Which parts of your routine have been feeling the most stressful lately?"
    e "[q!t]"

    menu:
        "Balancing caregiving with work or study":
            $ routine_stress = "balance"
            $ ans = "Balancing caregiving with work or study"
            $ aff_score = 2
            show hana neutral at hana_pos
            e "To balance caregiving with work or study, list your tasks and rank them by priority, then focus on the most urgent first."

        "Managing household tasks and caregiving":
            $ routine_stress = "household"
            $ ans = "Managing household tasks and caregiving"
            $ aff_score = 2
            show hana neutral at hana_pos
            e "To manage household tasks alongside caregiving, group similar tasks together and delegate where possible to save time and energy."

        "Finding time for myself":
            $ routine_stress = "personal_time"
            $ ans = "Finding time for myself"
            $ aff_score = 1
            show hana neutral at hana_pos
            e "To protect time for yourself, schedule short fixed breaks into your day and treat them as fixed appointments."

        "Handling unexpected caregiving needs":
            $ routine_stress = "unexpected_needs"
            $ ans = "Handling unexpected caregiving needs"
            $ aff_score = 3
            show hana neutral at hana_pos
            e "For unexpected caregiving needs, preparing a backup plan and a contact list in advance reduces last-minute pressure."

    $ affective_responses.append(aff_score)
    $ s_in = aff_score / 3.0
    call empathy_step(q, ans, s_in, "affective_followup_q2", speak=False) from _aff_followup_q2

    $ hana_pos = pick_random_scene_pos()
    show hana neutral at hana_pos
    $ q = "Has anything in your life been adding extra weight lately?"
    e "[q!t]"

    menu:
        "Worrying about the person I care for":
            $ extra_weight = "care_recipient_worry"
            $ ans = "Worrying about the person I care for"
            $ aff_score = 2
            show hana neutral at hana_pos
            e "For worry about the person you care for, focus on what is within your control and note specific concerns to discuss with their healthcare provider."

        "Having too many responsibilities at once":
            $ extra_weight = "too_many_responsibilities"
            $ ans = "Having too many responsibilities at once"
            $ aff_score = 3
            show hana neutral at hana_pos
            e "With too many responsibilities, prioritise the essential tasks and postpone or delegate the non-urgent ones to free up capacity."

        "Not getting enough rest or support":
            $ extra_weight = "lack_of_rest_support"
            $ ans = "Not getting enough rest or support"
            $ aff_score = 3
            show hana neutral at hana_pos
            e "For limited rest or support, contacting community resources or respite-care services can provide additional help."

        "Something else":
            $ extra_weight = "other"
            $ ans = "Something else"
            $ aff_score = 2
            show hana neutral at hana_pos
            e "Identifying the specific source of the pressure is a useful first step toward addressing it."

    $ affective_responses.append(aff_score)
    $ s_in = aff_score / 3.0
    call empathy_step(q, ans, s_in, "affective_followup_q3", speak=False) from _aff_followup_q3

    show hana neutral at hana_pos
    $ log_interaction(session_filename, session_id, "Neutral guidance summary",
                      day_impact + "|" + routine_stress + "|" + extra_weight,
                      stress_score, stress_level_desc, None, None, None, None, None, None,
                      "neutral_guidance")

    if stress_level == "Severe":
        e "When stress builds up like this, it helps to take one priority at a time rather than everything at once."
        e "Writing your tasks down and ranking them by urgency can make a heavy workload feel more manageable."
    else:
        e "A good starting point is to pick out your most urgent tasks and focus on those first."
        e "Setting the non-essential ones aside for later can take some of the pressure off."

    show hana neutral at hana_pos
    return

# ===========================
# POST-RESPONSE FEEDBACK
# ===========================
label post_response(strategy="general", feedback_prompt="Did checking in today feel helpful?"):
    $ hana_pos = pick_random_scene_pos()
    show hana neutral at hana_pos
    e "[feedback_prompt!t]"

    menu:
        "Yes, it helped":
            $ feedback = 1.0
            $ help_ans = "Yes"
        "A little":
            $ feedback = 0.5
            $ help_ans = "A little"
        "Not really":
            $ feedback = 0.0
            $ help_ans = "Not really"

    # NEUTRAL: record the rating only. No feedback learning, no weighting.
    $ post_rating = {1.0: 5, 0.5: 3, 0.0: 1}[feedback]

    $ log_interaction(
        session_filename, session_id,
        "Post-response feedback", help_ans,
        post_rating, stress_level, None, None, None, None, None, None,
        "post_response_" + strategy
    )

    show hana neutral at hana_pos
    e "Thank you for letting me know."

    $ feedback_given = True  # user has now given feedback; session is allowed to end

    show hana neutral at hana_pos
    return

#CALMING LOOP
label calming_loop:
    $ hana_pos = pick_random_scene_pos()
    $ loop_count = 0
    $ max_loops = 3
    $ techniques = ["breathing", "grounding", "body_scan", "gratitude", "reflection"]
    $ used_techniques = []
    $ calm_rating = 0
    $ should_exit = False

    while loop_count < max_loops:
        # Pick 2 techniques for this round
        $ available = [t for t in techniques if t not in used_techniques]
        if len(available) < 2:
            $ used_techniques = []
            $ available = list(techniques)

        # part guna technique beza beza untuk returning user
        $ first_choices = available
        if loop_count == 0 and avoid_technique_first in available and len(available) > 1:
            $ first_choices = [t for t in available if t != avoid_technique_first]

        $ tech1 = renpy.random.choice(first_choices)
        $ used_techniques.append(tech1)
        $ available = [t for t in available if t != tech1]
        $ tech2 = renpy.random.choice(available)
        $ used_techniques.append(tech2)
        $ last_technique = tech2

        # Deliver first technique
        call deliver_technique(tech1) from _deliver_tech_a

        # Brief bridge before second technique
        show hana neutral at hana_pos
        e "Let's try one more. This one is a little different."

        # Deliver second technique
        call deliver_technique(tech2) from _deliver_tech_b

        # Ask calm state after both techniques
        show hana neutral at hana_pos
        e "How are you feeling now, [user_name]?"
        menu:
            "Still very stressed":
                $ calm_rating = 1
                $ s_in = 1.0
                $ ans = "Still very stressed"
            "A bit stressed":
                $ calm_rating = 2
                $ s_in = 0.67
                $ ans = "A bit stressed"
            "Somewhere in between":
                $ calm_rating = 3
                $ s_in = 0.33
                $ ans = "Somewhere in between"
            "A little calmer":
                $ calm_rating = 4
                $ s_in = 0.1
                $ ans = "A little calmer"
            "Much calmer / peaceful":
                $ calm_rating = 5
                $ s_in = 0.0
                $ ans = "Much calmer"
            "I'd like to stop here for now":
                $ should_exit = True
                $ ans = "I'd like to stop"

        if not should_exit:
            $ last_calm_rating = calm_rating
            $ calm_rated_this_session = True
            $ log_interaction(
                session_filename, session_id,
                "Calming loop rating after " + tech1 + "+" + tech2, ans,
                calm_rating, stress_level, None, None, None, None, None, None,
                "calming_loop_iter" + str(loop_count + 1) + "_" + tech1 + "_" + tech2
            )

        $ loop_count += 1

        if should_exit:
            $ log_interaction(
                session_filename, session_id,
                "Calming loop ended (user stopped)", ans,
                None, stress_level, None, None, None, None, None, None,
                "calming_loop_user_exit"
            )
            show hana neutral at hana_pos
            e "Alright, we'll stop the exercise here."
            return

        if calm_rating >= 4:
            show hana neutral at hana_pos
            e "That's the end of this exercise."
            e "You can use these techniques again any time you want to wind down."
            if not feedback_given:
                call post_response(last_empathy_mode) from _calm_post_response_a
            return
        else:
            show hana neutral at hana_pos
            e "Let's try a different exercise."

    # if user reaches max calm loop but is still stressed
    show hana neutral at hana_pos
    e "That's the last exercise for now."
    e "If stress continues to feel heavy, consider reaching out through Befrienders or to someone you trust."
    e "You do not have to handle this alone."
    $ log_interaction(
        session_filename, session_id,
        "Calming loop ended (max loops)", "rating=" + str(calm_rating),
        calm_rating, stress_level, None, None, None, None, None, None,
        "calming_loop_max_reached"
    )
    if not feedback_given:
        call post_response(last_empathy_mode) from _calm_post_response_b
    return


# example techniques 
label deliver_technique(tech):
    $ hana_pos = pick_random_scene_pos()
    python:
        if tech not in techniques_used_list:
            techniques_used_list.append(tech)

    if tech == "breathing":
        show hana neutral at hana_pos
        e "This is a breathing exercise."
        e "Under stress, breathing tends to become quicker and shallower."
        e "Slowing the breath can lower the physical signs of stress."
        show hana neutral at hana_pos
        e "Follow this pattern."
        show hana neutral at hana_pos
        e "Breathe in through your nose for four counts."
        e "In.. one, two, three, four." 
        e "Hold."
        e "Hold.. two, three,four, five, six, seven."
        e "Breathe out through your mouth for eight counts."
        e "two, three, four, five, six, seven, eight."
        show hana neutral at hana_pos
        e "Repeat once more."
        e "In.. one, two, three, four."  
        e "Hold.. two, three, four, five, six, seven."
        e "And out.. two, three, four, five, six, seven, eight."
        show hana neutral at hana_pos
        e "A few slow breaths can reduce the body's stress response."

    elif tech == "grounding":
        show hana neutral at hana_pos
        e "This is the 5-4-3-2-1 grounding technique."
        e "It redirects attention to the present using the senses."
        show hana neutral at hana_pos
        e "Identify 5 things you can see."
        e "Identify 4 things you can physically touch."
        e "Identify 3 sounds you can hear."
        e "Identify 2 things you can smell, or recall smelling."
        e "Identify 1 thing you can taste."
        show hana neutral at hana_pos
        e "Grounding can interrupt racing thoughts and bring focus back to the present."

    elif tech == "body_scan":
        show hana neutral at hana_pos
        e "This is a body scan exercise."
        e "Stress often produces physical tension without notice."
        e "Common areas are the shoulders, jaw, neck, and hands."
        show hana neutral at hana_pos
        e "Direct your attention to your body, one area at a time."
        show hana neutral at hana_pos
        e "Shoulders: let them drop away from your ears."
        e "Jaw: let it loosen."
        e "Hands: let them rest."
        e "Then scan the neck, chest, and stomach for tension."
        show hana neutral at hana_pos
        e "Where you find tension, note it without trying to change it."
        e "Noticing where tension sits is the first step to releasing it."

    elif tech == "gratitude":
        show hana neutral at hana_pos
        e "This is a gratitude exercise."
        show hana neutral at hana_pos
        e "Under stress, attention narrows toward problems and unfinished tasks."
        e "Noting something positive can offset that bias."
        show hana neutral at hana_pos
        e "Identify one thing that has been good or useful recently."
        e "It does not need to be significant."
        e "Examples: a conversation, a meal, or a quiet moment."
        show hana neutral at hana_pos
        e "Hold that example in mind for a few seconds."
        e "Brief positive recall can shift attention away from stressors."

    elif tech == "reflection":
        stop music fadeout 2.0
        show beachscene at scene_right
        show hana neutral at hana_left
        e "This is a guided imagery exercise."
        e "It involves picturing a calm location in detail."
        e "It is commonly used to reduce stress in the moment."
        show hana neutral at hana_left
        e "Choose a place you find calm, such as a beach, a lake, or a forest."
        show hana neutral at hana_left
        e "Picture the scene."
        e "Note what is visible: colours, light, and detail."
        e "Note the sounds, such as waves, birds, or wind."
        e "Note physical sensations, such as warmth, cool air, or the ground underfoot."
        show hana neutral at hana_left
        e "Take one slow breath in."
        e "And out."
        e "Stay with the image for a few moments."
        e "You can return to this image whenever stress increases."
        hide beachscene
        if music_pref:
            play music "audio/BGM/Hana_lofi.mp3" volume 0.2 fadein 3.0 loop

    return

#phase 5: closure 
label phase5_close_update(end_action):

    $ final_calm_text = "unknown"
    if last_calm_rating is not None:
        if last_calm_rating >= 4:
            $ final_calm_text = "calmer"
        elif last_calm_rating <= 2:
            $ final_calm_text = "still_stressed"
        else:
            $ final_calm_text = "in_between"

    python:
        assert session_id is not None and session_id != "", "ERROR: session_id must be set"
        assert user_name is not None and user_name.strip() != "", "ERROR: user_name must be set"
        assert session_filename is not None and session_filename.strip() != "", "ERROR: session_filename must be set"

        session_end_time = datetime.datetime.now()
        session_duration = (session_end_time - session_start_time).total_seconds() / 60.0
        calm_residual_factor = {1: 1.0, 2: 0.8, 3: 0.6, 4: 0.35, 5: 0.15}
        end_baseline = initial_stress_score if initial_stress_score else session_start_stress
        if calm_rated_this_session and last_calm_rating is not None:
            residual = calm_residual_factor.get(last_calm_rating, 1.0)
            session_end_stress = int(round(end_baseline * residual))
        else:
            session_end_stress = end_baseline

        stress_improvement = session_start_stress - session_end_stress

        profile = save_user_profile(user_name, {
            "name": user_name,
            "visit_count": user_profile.get("visit_count", 0) + 1,
            "last_session_id": session_id,
            "last_stress_score": session_end_stress,
            "last_stress_level": stress_level,
            "last_empathy_mode": last_empathy_mode,
            "last_intention_level": last_intention_level,
            "last_empathy_E": round(last_empathy_E, 4),
            "last_calm_rating": last_calm_rating,
            "last_technique": last_technique,
            "last_end_action": end_action,
            "support_need_announced": support_need_announced,
        })

        save_profile_slot(hana_selected_profile_slot, {
            "name": profile.get("name", user_name),
            "visit_count": profile.get("visit_count", 0),
            "last_session_id": profile.get("last_session_id", session_id),
            "last_stress_level": profile.get("last_stress_level", stress_level),
            "last_calm_rating": profile.get("last_calm_rating", last_calm_rating),
        })

        log_session_summary(
            session_filename, session_id, user_name,
            session_start_stress, session_end_stress,
            modes_used_list, techniques_used_list,
            interaction_count, last_calm_rating,
            round(session_duration, 2), end_action,
            stress_improvement,
            stress_level, last_empathy_mode, last_intention_level,
            round(last_empathy_E, 4), support_need_announced
        )

    # terus save after every flow nak avoid user tak save progress
    $ renpy.save("auto-1")

    show hana neutral at hana_pos
    e "That's all for today, [user_name]."

    if final_calm_text == "still_stressed":
        e "If the stress keeps up, it's worth reaching out through BeHealth or to a healthcare professional for further support."

    e "You can come back any time to check in again."
    stop music fadeout 5.0

    return



