---
name: neutral-conversion-progress
description: HANANeutral conversion to the Neutral experimental condition — COMPLETE; lint passes
metadata:
  type: project
---

`HANANeutral` (a copy of the Adaptive HANA empathy build) has been converted into the **Neutral** experimental condition. Ren'Py lint passes with no errors (only orphan-translation warnings for the Malay file).

**Neutral condition spec (user's whiteboard + WhatsApp, 2026-06-18):**
- Stress assessment HIDDEN — check-in + DASS questions asked back-to-back, NO per-answer reactions; scoring still computed silently.
- Responses INFORMATIONAL only (no validation/empathy), still tailored to measured stress level (Normal/Mild/Moderate/Severe/Extremely severe).
- NO empathy weightage math, NO learning/updating.
- Calming exercises kept AS-IS.

**Edits applied (game/script.rpy + game/hana_sync.rpy):**
- hana_sync.rpy: `HANA_APP_TYPE = "neutral"`.
- `empathy_step` → log-only, neutral.
- `adapt_weights_from_feedback` + `update_empathy_policy_from_feedback` → no-ops.
- Check-in Q1–Q4 + DASS screening loop → silent (no reactions/bridges).
- Post-screening summary → single neutral line; stress_level expression block → neutral only.
- Routing → by stress_level only, neutral dialogue, no empathy math.
- `affective_input` Q1–Q3 → neutral informational/solution responses; tail empathy/cognitive/compassionate branches → replaced with neutral stress-level summary.
- `calming_loop` → removed weightage/learning block (kept calm_rating + neutral log); calming content/flow untouched.
- `post_response` → log-only, neutral closing.
- `phase5_close_update` → neutral closing (save/summary logic + BeHealth referral kept).
- `session_end_loop` framing → neutral.
- Returning-user greeting → neutral (no stress reflection).

**Dead-but-harmless leftovers (never executed; could be cleaned later):** `table_rule_for_condition`/`empathy_policy_weight`/`base_table_rule_for_condition`, `HANA_BRIDGES`/`hana_bridge`/`level_from_s_in`, the `fillers_before`/`affective_feedback`/`fillers_before_aff` lists, and the empathy param defaults (Ea/Ec/Ad/Be...). Onboarding (name intro, music preference) intentionally left as the shared warm intro across conditions.

**Still open / optional:**
- Malay translation (`game/tl/malay/script.rpy`) is now out of sync (orphan translations + new English lines untranslated). Re-translate if Malay playthrough is needed.
- Manual playthrough test recommended (lint ≠ runtime test).
- Nothing committed yet.
