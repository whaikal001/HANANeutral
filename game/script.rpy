image logos_row = HBox(
    Transform("logo_uum.png", fit="contain", ysize=160),
    Transform("logo_kpt.png", fit="contain", ysize=160),
    Transform("logo_ums.png", fit="contain", ysize=160),
    spacing=80,
)

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

# 4-7-8 breathing guide (animated). Uses a looping webm so it actually plays;
# Ren'Py does not animate .gif files (it would only show the first frame).
image breathing_guide = Movie(play="video/478breathing.webm", loop=True)

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

transform breathing_guide_pos:
    zoom 0.5
    xalign 0.9
    yalign 0.42
    on show:
        alpha 0.0
        linear 0.4 alpha 1.0
    on hide:
        linear 0.4 alpha 0.0

init python:
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

    # Study log layout, the same for all three arms:
    # HANA_[ParticipantID]_[Condition]_[DateTime].csv with these columns.
    HANA_CONDITION_CODE = "NEU"
    SESSION_LOG_HEADER = [
        "Participant_ID", "Session_ID", "Condition", "Timestamp", "Cycle",
        "Stage", "Duration", "HANA_Question", "User_Response", "HANA_Response",
        "Ea", "Ec", "Be", "D", "Ep", "E", "I", "Ed", "H", "Ed_Adaptive",
        "Behaviour_Profile",
    ]

    def hana_participant_id():
        try:
            return "P%02d" % int(renpy.store.hana_selected_profile_slot)
        except Exception:
            return "P00"

    def make_session_filename():
        return "HANA_%s_%s_%s.csv" % (
            hana_participant_id(), HANA_CONDITION_CODE,
            datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
        )

    def log_interaction(session_filename, session_id, question, answer,
                        score=None, stress_level=None,
                        Ea=None, Ec=None, Ad=None, Be=None, D=None, Ep=None,
                        empathy_mode=None, extra=None):
        # The step tag passed as empathy_mode goes in Stage. The neutral arm
        # computes no E, I, Bl, Cycle, Ed, H or Ed_Adaptive, so those stay blank.
        x = {"participant_id": hana_participant_id(), "stage": empathy_mode, "Bl": None}
        x.update(extra or {})

        log_path = os.path.join(DROPBOX_LOG_DIR, session_filename)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [
            x["participant_id"], session_id, HANA_CONDITION_CODE, timestamp,
            x.get("cycle"), x["stage"], x.get("duration"),
            question, answer, x.get("hana_response"), Ea, Ec, Be, D, Ep,
            x.get("E"), x.get("I"), x.get("Ed"), x.get("H"), x.get("Ed_adaptive"),
            x["Bl"],
        ]

        try:
            write_header = not os.path.exists(log_path)
            with open(log_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(SESSION_LOG_HEADER)
                writer.writerow(row)
        except Exception:
            pass
        try:
            hana_sync_interaction(
                session_id, session_filename, timestamp, question, answer,
                score, stress_level, Ea, Ec, Ad, Be, D, Ep, empathy_mode,
                extra=x,
            )
        except Exception:
            pass
    SESSION_SUMMARY_FIELDS = [
        "Session start", "Session end", "User", "Profile ID", "Session ID", "Session #",
        "Condition", "DASS stress raw (0-21)", "DASS stress score (0-42)", "Stress level",
        "Pathway", "Start stress score", "End stress score", "Stress improvement",
        "Final calm rating", "Empathy modes", "Last empathy mode", "Intention (I)",
        "Empathy E", "Activities", "Counselling offered", "Turns", "Duration (min)",
        "Ended by",
    ]

    def log_session_summary(session_filename, session_id, user_name,
                           start_stress_score, end_stress_score,
                           modes_used, techniques_used, total_interactions,
                           final_calm_rating, session_duration_minutes, end_action,
                           stress_improvement=None,
                           stress_level="", empathy_mode="", intention_level="",
                           empathy_E="", support_need_announced="", extra=None):

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        x = extra or {}

        if stress_improvement is None:
            stress_improvement = start_stress_score - end_stress_score if start_stress_score else 0

        values = [
            x.get("session_start", ""), timestamp, user_name, hana_participant_id(),
            session_id, x.get("session_index", ""), HANA_CONDITION_CODE,
            x.get("dass_raw", ""), x.get("dass_score", ""), stress_level,
            x.get("pathway", ""), start_stress_score, end_stress_score,
            stress_improvement, final_calm_rating,
            "|".join(modes_used) if modes_used else "none", empathy_mode,
            intention_level, empathy_E,
            "|".join(techniques_used) if techniques_used else "none",
            support_need_announced, total_interactions,
            session_duration_minutes, end_action,
        ]
        rows = [
            [
                hana_participant_id(), session_id, HANA_CONDITION_CODE, timestamp,
                "", "Summary", "", field, value, "",
            ] + [""] * (len(SESSION_LOG_HEADER) - 10)
            for field, value in zip(SESSION_SUMMARY_FIELDS, values)
        ]

        log_path = os.path.join(DROPBOX_LOG_DIR, session_filename)
        try:
            write_header = not os.path.exists(log_path)
            with open(log_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(SESSION_LOG_HEADER)
                writer.writerows(rows)
        except Exception:
            pass
        try:
            hana_sync_summary(
                session_id, session_filename, timestamp, user_name,
                start_stress_score, end_stress_score, stress_improvement,
                final_calm_rating, modes_used, techniques_used,
                total_interactions, session_duration_minutes, end_action,
                stress_level, empathy_mode, intention_level,
                empathy_E, support_need_announced,
                # the backend keeps every session with these, like Adaptive's
                extra={
                    "participant_id": hana_participant_id(),
                    "condition": HANA_CONDITION,
                    "session_start": x.get("session_start", ""),
                    "session_index": x.get("session_index", ""),
                    "dass_raw": x.get("dass_raw", ""),
                    "dass_score": x.get("dass_score", ""),
                    "pathway": x.get("pathway", ""),
                },
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
        # P01-style id, the same in all three apps and in the CSV file names.
        pid = "P%02d" % int(slot_index)
        key, slot_store, slot = load_profile_slot(slot_index)
        if slot.get("profile_id") != pid:
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

        if visit_count <= 0 and last_stress_level == "unknown":
            return "New slot"

        return "Visits: %d | Stress: %s" % (visit_count, last_stress_level)

    def profile_save_page(slot_index):
        return "profile_%d" % int(slot_index)
    def clamp_range(x, lo, hi):
        return max(lo, min(hi, x))

    def pick_random_scene_pos():
        return renpy.random.choice([hana_left, hana_mid, hana_right])

# method nak clean menu function sebab nak bg main menu clear and bukan ingame
init 999 python:
    cleanup_unfinished_profile_slots()

default support_need_announced = False
default last_technique = None
default final_check = ""
default quick_menu = True

# --- Characters ---
define e = Character("Hana", color="#b56ab3")
# Study arm, used by hana_sync.rpy (same file in all three apps).
define HANA_CONDITION = "neutral"

# =========================
# STATE VARIABLES
# =========================
default stress_level = "Normal"
default stress_level_desc = "Normal"
default last_empathy_mode = "neutral"

default feedback = 0.0

default modes_used_list = []  # Track all modes used in session
default techniques_used_list = []  # Track all techniques used in session
default session_start_stress = 0  # Initial stress score
default initial_stress_score = 0  # For reference
default interaction_count = 0  # Count of logged interactions
default session_start_time = None  # Track session duration

default session_id = ""
default session_filename = ""

default last_intention_level = "N/A"
default last_empathy_E = 0.0

default stress_score = 0
default checkin_s_in_history = []
default hana_selected_profile_slot = 1
default hana_active_profile_id = ""
default hana_pos = hana_mid

# --- Flow Starts ---


label start:

    scene black
    with fade

    # English only, like the Adaptive app (the Malay button was removed).
    if _preferences.language is not None:
        $ renpy.change_language(None)

    show logos_row:
        xalign 0.5 yalign 0.9
    centered "Disclaimer\n\nThis session includes questions about stress adapted from the DASS-21.\n\nThese questions are for research purposes only. They are not a medical test and cannot be used to diagnose or treat any health condition.\n\n{size=-10}This research is supported by the Ministry of Higher Education (MoHE) Malaysia through the Fundamental Research Grant Scheme (FRGS/1/2024/ICT02/UUM/02/1).{/size}"
    hide logos_row

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
    $ last_technique = None
    $ final_check = ""
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
    # True once counselling contacts are offered in this session (see
    # support_contacts), like the Adaptive app's counselling_offered.
    $ support_need_announced = False

    # idea dr azizi mintak user preference if nk guna music ke tak
    $ music_pref = user_profile.get("music_enabled", None)
    if music_pref:
        play music "audio/BGM/Hana_lofi.mp3" volume 0.3 fadein 3.0 loop

    # 2 flow (user baru or lama)
    if is_returning_user:
    
        show hana neutral at hana_pos
        e "Session resume for [user_name]."
        show hana neutral at hana_pos
        with Fade(0.3, 0.0, 0.3)
        if last_stress_level in ["Moderate", "Severe", "Extremely severe"]:
            e "Your last stress level is in the high range."
        else:
            e "Your last stress level is in the low range."
    else:
        
        show hana neutral at hana_pos
        e "This is Hana."
        if not user_name:
            show hana neutral at hana_pos
            with Fade(0.3, 0.0, 0.3)
            e "And you...?"
            show hana neutral at hana_pos
            $ user_name = renpy.input("")
            $ user_name = user_name.strip().title() if user_name.strip() else "friend"
            $ save_profile_slot(selected_slot, {"name": user_name})
            $ user_profile_key, user_profile_store, user_profile = load_user_profile(user_name)

        show hana neutral at hana_pos
        with Fade(0.3, 0.0, 0.3)
        e "User identify as [user_name]."
    
    # line mintak user nak music ke tak
    if music_pref is None:
        show hana neutral at hana_pos
        with Fade(0.3, 0.0, 0.3)
        e "Would you like some music?"

        menu:
            "Yes, please.":
                $ music_pref = True
                show hana neutral at hana_pos
                e "Okay, I'll play some music."
                play music "audio/BGM/Hana_lofi.mp3" volume 0.3 fadein 3.0 loop

            "No, thanks.":
                $ music_pref = False
                stop music fadeout 1.0
                show hana neutral at hana_pos
                e "Okay, we'll continue without music."

        $ user_profile = save_user_profile(user_name, {"music_enabled": music_pref})
        $ log_interaction(session_filename, session_id,
                          "Music preference", "music_on" if music_pref else "music_off",
                          None, None, None, None, None, None, None, None, "preference")

    hide black
    with Dissolve(0.5)

 #greeting and check-in

    show hana neutral at hana_pos

    e "How are you feeling today?"
    menu:
        "I feel good.":
            $ ans = "I feel good"
            $ s_in = 0.0
        "I'm okay.":
            $ ans = "I feel quite okay"
            $ s_in = 0.33
        "I'm not feeling good.":
            $ ans = "A bit stressed"
            $ s_in = 0.67
        "I feel stressed.":
            $ ans = "Really stressed"
            $ s_in = 1.0

    $ checkin_s_in_history.append(s_in)
    call empathy_step("How do you feel today?", ans, s_in, "checkin_q1", speak=False) from _checkin_q1

    # Check-in is this one question, as in the Adaptive app. The other
    # questions come once, in the pathway after the stress questions.
    show hana neutral at hana_pos
    jump stress_input

# Neutral arm: after every answer HANA gives a plain acknowledgement, never
# an emotional reply, before the next question.
define NEUTRAL_ACKS = ["Okay.", "Noted.", "Alright."]

label empathy_step(question, ans, s_in, phase, speak=True):
    $ interaction_count += 1
    $ last_empathy_mode = "neutral"
    $ last_intention_level = "N/A"
    $ neutral_ack = renpy.random.choice(NEUTRAL_ACKS)
    $ log_interaction(session_filename, session_id, question, ans,
                      None, stress_level, None, None, None, None, None, None,
                      "neutral_" + phase, extra={"hana_response": neutral_ack})
    e "[neutral_ack]"
    return


label stress_input:
    $ hana_pos = pick_random_scene_pos()
    show hana neutral at hana_pos
    e "Let's check your stress level."
    e "Think about the past seven days."
    e "There are no right or wrong answers. Just choose what fits you best."

    $ stress_questions = [
        _("Was it hard to wind down?"),
        _("Did you overreact to things?"),
        _("Did you feel restless?"),
        _("Was it hard to relax?"),
        _("Did delays make you upset?"),
        _("Did you feel easily annoyed?"),
        _("Was it hard to calm down?"),
    ]

    $ stress_responses = []
    $ i = 0

    while i < len(stress_questions):
        $ q = stress_questions[i]
        $ hana_pos = pick_random_scene_pos()
        show hana neutral at hana_pos
        e "[q!t]"

        menu:
            "Not at all":
                $ stress_responses.append(0)
                $ ans = "Not really"
                $ s_in = 0.0

            "Sometimes":
                $ stress_responses.append(1)
                $ ans = "Maybe a little"
                $ s_in = 0.33

            "Often":
                $ stress_responses.append(2)
                $ ans = "Quite a lot"
                $ s_in = 0.67

            "Most of the time":
                $ stress_responses.append(3)
                $ ans = "Almost always"
                $ s_in = 1.0

        call empathy_step(q, ans, s_in, "screening_q" + str(i+1), speak=False) from _screening_step

        show hana neutral at hana_pos
        $ i += 1


    show hana neutral at hana_pos
    e "All response recorded."

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

    $ last_empathy_mode = "neutral"
    $ last_intention_level = "N/A"
    if "neutral" not in modes_used_list:
        $ modes_used_list.append("neutral")

    jump neutral_adaptive_pathway


label neutral_adaptive_record(question, answer, phase):
    call empathy_step(question, answer, 0.0, phase, False)
    return


label neutral_adaptive_pathway:
    if stress_level in ["Normal", "Mild"]:
        $ pathway = "non_stress"
        jump neutral_adaptive_non_stress
    $ pathway = "stress"
    jump neutral_adaptive_stress


label neutral_adaptive_non_stress:
    show hana neutral at hana_pos
    e "What has been going well lately?"
    menu:
        "Family":
            $ ans = "Family"
        "Caring for someone":
            $ ans = "Caring for someone"
        "Work or daily activities":
            $ ans = "Work or daily activities"
        "My health":
            $ ans = "My health"
        "Things are just okay":
            $ ans = "Things are just okay"
    call neutral_adaptive_record("What has been going well lately?", ans, "non_stress_q1") from _neutral_ns_q1

    show hana neutral at hana_pos
    e "What helps you feel okay?"
    menu:
        "Resting":
            $ ans = "Resting"
        "Talking to someone":
            $ ans = "Talking to someone"
        "Doing something I enjoy":
            $ ans = "Doing something I enjoy"
        "Having time alone":
            $ ans = "Having time alone"
        "My daily routine":
            $ ans = "My daily routine"
    call neutral_adaptive_record("What helps you feel okay?", ans, "non_stress_q2") from _neutral_ns_q2

    show hana neutral at hana_pos
    e "Is there anything you want to talk about?"
    menu:
        "Yes":
            $ ans = "Yes"
        "No":
            $ ans = "No"
    call neutral_adaptive_record("Is there anything you want to talk about?", ans, "non_stress_q3") from _neutral_ns_q3
    jump neutral_adaptive_cycle_2


label neutral_adaptive_stress:
    show hana neutral at hana_pos
    e "What has been stressful lately?"
    menu:
        "Caring for someone":
            $ ans = "Caring for someone"
        "Family":
            $ ans = "Family"
        "Work or money":
            $ ans = "Work or money"
        "Health":
            $ ans = "Health"
        "Something else":
            $ ans = "Something else"
    call neutral_adaptive_record("What has been stressful lately?", ans, "stress_q1") from _neutral_st_q1

    show hana neutral at hana_pos
    e "What worries you most about it?"
    menu:
        "It may get worse":
            $ ans = "It may get worse"
        "I can't manage it":
            $ ans = "I can't manage it"
        "It affects other people":
            $ ans = "It affects other people"
        "I don't know what to do":
            $ ans = "I don't know what to do"
        "Something else":
            $ ans = "Something else"
    call neutral_adaptive_record("What worries you most about it?", ans, "stress_q2") from _neutral_st_q2

    show hana neutral at hana_pos
    e "How has this been affecting you?"
    menu:
        "I feel tired":
            $ ans = "I feel tired"
        "I feel overwhelmed":
            $ ans = "I feel overwhelmed"
        "I can't focus":
            $ ans = "I can't focus"
        "I can't relax":
            $ ans = "I can't relax"
        "Something else":
            $ ans = "Something else"
    call neutral_adaptive_record("How has this been affecting you?", ans, "stress_q3") from _neutral_st_q3

    show hana neutral at hana_pos
    e "What usually helps you feel better?"
    menu:
        "Resting":
            $ ans = "Resting"
        "Talking to someone":
            $ ans = "Talking to someone"
        "Doing something I enjoy":
            $ ans = "Doing something I enjoy"
        "Having time alone":
            $ ans = "Having time alone"
        "Nothing really helps":
            $ ans = "Nothing really helps"
    call neutral_adaptive_record("What usually helps you feel better?", ans, "stress_q4") from _neutral_st_q4

    show hana neutral at hana_pos
    e "Who can you talk to when things are difficult?"
    menu:
        "Family":
            $ ans = "Family"
        "A friend":
            $ ans = "A friend"
        "Someone I trust":
            $ ans = "Someone I trust"
        "A professional":
            $ ans = "A professional"
        "No one":
            $ ans = "No one"
    call neutral_adaptive_record("Who can you talk to when things are difficult?", ans, "stress_q5") from _neutral_st_q5

    # Safety: offer counselling contacts, as the Adaptive app does.
    if ans == "No one":
        show hana neutral at hana_pos
        e "Would you like information about counselling support?"
        menu:
            "Yes":
                $ ans = "Yes"
            "No":
                $ ans = "No"
        call neutral_adaptive_record("Would you like information about counselling support?", ans, "counselling_offer") from _neutral_counselling_offer
        if ans == "Yes":
            call support_contacts from _neutral_st_q5_contacts
    jump neutral_adaptive_cycle_2


label neutral_adaptive_cycle_2:
    show hana neutral at hana_pos
    if stress_level in ["Normal", "Mild"]:
        $ c2_question = "What would be helpful now?"
        e "What would be helpful now?"
    else:
        $ c2_question = "What would help you most now?"
        e "What would help you most now?"
    menu:
        "Talk a little more":
            $ ans = "Talk a little more"
        "Think about what helps me":
            $ ans = "Think about what helps me"
        "Try a short activity":
            $ ans = "Try a short activity"
        # As in the Adaptive app: support information on the stress path.
        "Get support information" if stress_level not in ["Normal", "Mild"]:
            $ ans = "Get support information"
        "Nothing right now" if stress_level in ["Normal", "Mild"]:
            $ ans = "Nothing right now"
    call neutral_adaptive_record(c2_question, ans, "cycle_2_choice") from _neutral_c2_choice
    if ans == "Try a short activity":
        call run_activity from _neutral_c2_activity
    elif ans == "Get support information":
        call support_contacts from _neutral_c2_contacts

    show hana neutral at hana_pos
    e "How do you feel compared with earlier?"
    menu:
        "Better":
            $ ans = "Better"
        "About the same":
            $ ans = "About the same"
        "Worse":
            $ ans = "Worse"
    call neutral_adaptive_record("How do you feel compared with earlier?", ans, "checkpoint_1") from _neutral_checkpoint

    show hana neutral at hana_pos
    e "Would you like to try a short activity?"
    menu:
        "Yes, please.":
            $ ans = "Yes"
        "No, thanks.":
            $ ans = "No"
    call neutral_adaptive_record("Would you like to try a short activity?", ans, "final_activity") from _neutral_final_activity_record
    if ans == "Yes":
        call run_activity from _neutral_final_activity

    # Final check, as in the Adaptive app. The closing goes by this answer.
    show hana neutral at hana_pos
    e "How do you feel compared with earlier?"
    menu:
        "Better":
            $ final_check = "better"
            $ ans = "Better"
        "About the same":
            $ final_check = "same"
            $ ans = "About the same"
        "Worse":
            $ final_check = "worse"
            $ ans = "Worse"
    call neutral_adaptive_record("How do you feel compared with earlier?", ans, "final_check") from _neutral_final_check

    call phase5_close_update("completed") from _neutral_adaptive_close
    return
label support_contacts:
    $ support_need_announced = True
    show hana neutral at hana_pos
    e "UUM Counselling Centre: 04-928 4059 / 4060 / 4071"
    e "MENTARI Kota Setar: 013-434 2359"
    e "Talian HEAL: 15555"
    return

label run_activity:
    show hana neutral at hana_pos
    e "Which activity would you like to try?"
    menu:
        "Breathing":
            $ ans = "Breathing"
            $ last_technique = "breathing"
        "Grounding":
            $ ans = "Grounding"
            $ last_technique = "grounding"
        "Body scan":
            $ ans = "Body scan"
            $ last_technique = "body_scan"
    call neutral_adaptive_record("Which activity would you like to try?", ans, "activity_choice") from _neutral_activity_choice
    call deliver_technique(last_technique) from _neutral_activity_technique
    $ hana_pos = hana_mid
    show hana neutral at hana_pos
    e "This is the end of the exercise."
    return
label deliver_technique(tech):
    $ hana_pos = pick_random_scene_pos()
    python:
        if tech not in techniques_used_list:
            techniques_used_list.append(tech)

    if tech == "breathing":
        show hana neutral at hana_pos
        e "This is breathing exercise."
        e "Under stress, breathing become more quick and more shallow."
        e "Slow the breath can lower the physical sign of stress."
        # step Hana to the left for the breathing rounds
        $ hana_pos = hana_left
        show hana neutral at hana_pos
        e "Follow this pattern."
        show breathing_guide at breathing_guide_pos
        python:
            e(_("Breathe in through your nose for four second."), interact=False)
            renpy.pause(4.0)
            e(_("Hold your breath for seven second."), interact=False)
            renpy.pause(7.0)
            e(_("Breathe out through your mouth for eight second."), interact=False)
            renpy.pause(8.0)
            # two full 4-7-8 breathing rounds
            for _round in range(2):
                e(_("Breath in"), interact=False)
                renpy.pause(4.0)
                e(_("Hold breath."), interact=False)
                renpy.pause(7.0)
                e(_("Breath out."), interact=False)
                renpy.pause(8.0)
                if _round == 0:
                    e(_("Repeat one more time."), interact=False)
                    renpy.pause(2.0)
        hide breathing_guide
        show hana neutral at hana_pos
        e "A few slow breath can reduce the body stress response."

    elif tech == "grounding":
        show hana neutral at hana_pos
        e "This is the 5-4-3-2-1 grounding technique."
        e "It bring your attention back to the present using the senses."
        show hana neutral at hana_pos
        e "Identify 5 things you can see."
        e "Identify 4 things you can touch."
        e "Identify 3 sounds you can hear."
        e "Identify 2 things you can smell, or you remember the smell."
        e "Identify 1 thing you can taste."
        show hana neutral at hana_pos
        e "This grounding can stop the racing thought and bring focus back to the present."

    elif tech == "body_scan":
        show hana neutral at hana_pos
        e "This is body scan exercise."
        e "Stress often produce physical tension without you notice."
        e "The common area is the shoulder, jaw, neck, and hand."
        show hana neutral at hana_pos
        e "Direct your attention to your body, one area at one time."
        show hana neutral at hana_pos
        e "Shoulder: let it drop away from your ear."
        e "Jaw: let it loose."
        e "Hand: let it rest."
        e "After that, scan the neck, chest, and stomach for tension."
        show hana neutral at hana_pos
        e "Where you find tension, just note it, do not try to change it."
        e "To notice where the tension is, that is the first step to release it."

    return

#phase 5: closure 
label phase5_close_update(end_action):
    $ show_close_contacts = final_check == "worse" or (final_check != "better" and stress_level not in ["Normal", "Mild"])
    if show_close_contacts:
        $ support_need_announced = True

    python:
        assert session_id is not None and session_id != "", "ERROR: session_id must be set"
        assert user_name is not None and user_name.strip() != "", "ERROR: user_name must be set"
        assert session_filename is not None and session_filename.strip() != "", "ERROR: session_filename must be set"

        session_end_time = datetime.datetime.now()
        session_duration = (session_end_time - session_start_time).total_seconds() / 60.0
        session_end_stress = initial_stress_score
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
            "last_technique": last_technique,
            "last_end_action": end_action,
            "support_need_announced": support_need_announced,
        })

        save_profile_slot(hana_selected_profile_slot, {
            "name": profile.get("name", user_name),
            "visit_count": profile.get("visit_count", 0),
            "last_session_id": profile.get("last_session_id", session_id),
            "last_stress_level": profile.get("last_stress_level", stress_level),
        })

        log_session_summary(
            session_filename, session_id, user_name,
            session_start_stress, session_end_stress,
            modes_used_list, techniques_used_list,
            interaction_count, None,  # final calm rating: no longer asked
            round(session_duration, 2), end_action,
            stress_improvement,
            stress_level, last_empathy_mode, last_intention_level,
            round(last_empathy_E, 4), support_need_announced,
            extra={
                "session_start": session_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "session_index": profile.get("visit_count", ""),
                "dass_raw": raw_score,
                "dass_score": initial_stress_score,
                "pathway": pathway,
            },
        )

    # terus save after every flow nak avoid user tak save progress
    $ renpy.save("auto-1")

    show hana neutral at hana_pos
    e "Session complete."

    if show_close_contacts:
        e "If high stress persists, counselling support is available."
        call support_contacts from _neutral_close_contacts

    e "A new session can start later."
    stop music fadeout 5.0

    return
