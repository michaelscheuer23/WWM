import streamlit as st
import random
import time
import json
import os
from Questions import QUESTIONS 

# --- Konfiguration ---
st.set_page_config(page_title="Religions-Quiz: Millionär", page_icon="💸", layout="centered")

# --- CSS HACK: WWM-Animationen & Massive Rechtecke ---
st.markdown(
    """
    <style>
    html, body {
        touch-action: manipulation;
    }
    .stApp {
        background-color: #0e1117;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    /* ====================================================
       1. DIE ANTWORT-BUTTONS (Riesige Rechtecke, Primary)
       ==================================================== */
    .stButton>button[kind="primary"] {
        width: 100% !important;
        min-height: 85px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        background-color: #1a1a2e !important;
        color: #e6e6e6 !important;
        border: 2px solid #4a4e69 !important;
        margin-bottom: 0.5rem !important;
        transition: all 0.2s ease;
    }
    .stButton>button[kind="primary"]:hover:not(:disabled) {
        background-color: #fca311 !important;
        color: #14213d !important;
        border-color: #fca311 !important;
        transform: scale(1.02);
    }

    /* ====================================================
       2. DIE JOKER & MENÜS (Dezente Pillen, Secondary)
       ==================================================== */
    .stButton>button[kind="secondary"] {
        width: 100% !important;
        min-height: 45px !important;
        font-size: 14px !important;
        border-radius: 25px !important;
        background-color: #2b2d42 !important;
        color: #adb5bd !important;
        border: 1px solid #6c757d !important;
    }
    .stButton>button[kind="secondary"]:hover:not(:disabled) {
        border-color: #fca311 !important;
        color: #fca311 !important;
    }
    .stButton>button[kind="secondary"]:disabled {
        background-color: #161a1d !important;
        color: #3d4146 !important;
        border: 1px dashed #3d4146 !important;
        opacity: 0.5 !important;
    }

    /* ====================================================
       3. DIE ANIMATIONEN FÜR DIE AUFLÖSUNG (HTML-DIVS)
       ==================================================== */
    .wwm-locked-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        min-height: 85px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
        background-color: #1a1a2e;
        color: #e6e6e6;
        border: 2px solid #4a4e69;
        margin-bottom: 0.5rem;
        box-sizing: border-box;
        padding: 10px;
        text-align: center;
    }

    /* Animation: Ausgewählt & Richtig */
    .anim-sel-correct {
        animation: key-sel-correct 3.5s linear forwards;
    }
    @keyframes key-sel-correct {
        0%, 15%, 30%, 45% { background-color: #fca311; border-color: #fff; color: #14213d; }
        7.5%, 22.5%, 37.5%, 52.5% { background-color: #1a1a2e; border-color: #fca311; color: #fca311; }
        70%, 100% { background-color: #198754; border-color: #06d6a0; color: white; transform: scale(1.05); box-shadow: 0 0 20px #06d6a0; }
    }

    /* Animation: Ausgewählt & Falsch */
    .anim-sel-wrong {
        animation: key-sel-wrong 3.5s linear forwards;
    }
    @keyframes key-sel-wrong {
        0%, 15%, 30%, 45% { background-color: #fca311; border-color: #fff; color: #14213d; }
        7.5%, 22.5%, 37.5%, 52.5% { background-color: #1a1a2e; border-color: #fca311; color: #fca311; }
        70%, 100% { background-color: #dc3545; border-color: #ff4d6d; color: white; transform: scale(1.05); box-shadow: 0 0 20px #ff4d6d; }
    }

    /* Animation: Nicht ausgewählt, aber es ist die richtige Antwort (Reveal) */
    .anim-rev-correct {
        animation: key-rev-correct 3.5s linear forwards;
    }
    @keyframes key-rev-correct {
        0%, 65% { background-color: #1a1a2e; border-color: #4a4e69; color: #e6e6e6; }
        70%, 100% { background-color: #198754; border-color: #06d6a0; color: white; box-shadow: 0 0 20px #06d6a0; }
    }

    /* Animation: Nicht ausgewählt und Falsch (Fade out) */
    .anim-fade-wrong {
        animation: key-fade-wrong 3.5s linear forwards;
    }
    @keyframes key-fade-wrong {
        0%, 65% { opacity: 1; }
        70%, 100% { opacity: 0.3; }
    }

    /* Status-Leiste oben */
    .mobile-status {
        background-color: #1a1a2e;
        padding: 10px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid #fca311;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

MONEY_TREE = [
    "0 €", "50 €", "100 €", "200 €", "300 €", "500 €", 
    "1.000 €", "2.000 €", "4.000 €", "8.000 €", "16.000 €", 
    "32.000 €", "64.000 €", "125.000 €", "500.000 €", "1.000.000 €"
]

HIGHSCORE_FILE = "highscores.json"

def parse_money(m_str):
    if not m_str or "Pkt" in m_str: return 0
    return int(m_str.replace('.', '').replace(' €', ''))

def load_highscores():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def save_highscore(name, won_amount, duration):
    scores = load_highscores()
    num_money = parse_money(won_amount)
    valid_scores = [s for s in scores if "num_money" in s]
    valid_scores.append({
        "name": name,
        "won_amount": won_amount,
        "num_money": num_money,
        "duration": round(duration, 1)
    })
    valid_scores.sort(key=lambda x: (-x["num_money"], x["duration"]))
    with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(valid_scores, f, indent=4)

def get_safe_sample(q_list, k):
    return random.sample(q_list, k) if len(q_list) >= k else q_list

# --- Session State Initialisierung ---
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'game_active' not in st.session_state: st.session_state.game_active = False
if 'game_over' not in st.session_state: st.session_state.game_over = False
if 'celebration' not in st.session_state: st.session_state.celebration = None
if 'history_log' not in st.session_state: st.session_state.history_log = []
if 'lock_choice' not in st.session_state: st.session_state.lock_choice = None

# ==========================================
# ROBUSTER LOGIN-SCREEN
# ==========================================
if not st.session_state.user_name:
    st.title("💸 Willkommen im Studio!")
    st.write("Bevor du auf dem heißen Stuhl Platz nimmst, trage bitte deinen Namen ein:")
    
    name_input = st.text_input("Dein Name:", placeholder="Vorname oder Spitzname")
    
    if st.button("Auf den heißen Stuhl!", type="primary", use_container_width=True):
        if name_input.strip() == "": 
            st.error("Bitte gib einen echten Namen ein!")
        else:
            st.session_state.user_name = name_input.strip()
            st.rerun()
            
    st.stop()


def use_audience():
    st.session_state.jokers["audience"] = False
    q = st.session_state.game_questions[st.session_state.current_level - 1]
    correct = q["answer"]
    lvl = st.session_state.current_level
    
    base = 70 if lvl <= 5 else (50 if lvl <= 10 else 35)
    correct_pct = random.randint(base, base + 15)
    opts = st.session_state.active_options or q["shuffled_options"]
    results = {}
    
    if len(opts) == 2:
        results[correct] = correct_pct
        for opt in opts:
            if opt != correct: results[opt] = 100 - correct_pct
    else:
        rem = 100 - correct_pct
        others = []
        for _ in range(3):
            val = random.randint(0, rem)
            others.append(val)
            rem -= val
        others[-1] += rem
        random.shuffle(others)
        idx = 0
        for opt in opts:
            if opt == correct: results[opt] = correct_pct
            else:
                results[opt] = others[idx]
                idx += 1
    st.session_state.audience_result = results

def process_eval(selected):
    """Wertet die Antwort aus, nachdem die Animation abgelaufen ist."""
    q = st.session_state.game_questions[st.session_state.current_level - 1]
    correct = q["answer"]
    
    st.session_state.history_log.append({
        "question": q["text"],
        "user_ans": selected,
        "correct_ans": correct,
        "explanation": q.get("explanation", ""),
        "is_correct": (selected == correct)
    })
    
    if selected == correct:
        st.session_state.current_level += 1
        st.session_state.active_options = None 
        st.session_state.audience_result = None
        st.session_state.phone_result = None
        
        if st.session_state.current_level == 6: st.session_state.celebration = "500 €"
        elif st.session_state.current_level == 11: st.session_state.celebration = "16.000 €"
            
        if st.session_state.current_level > 15:
            st.session_state.game_over = True
            st.session_state.won_amount = "1.000.000 €"
            st.session_state.duration = time.time() - st.session_state.start_time
    else:
        st.session_state.game_over = True
        st.session_state.duration = time.time() - st.session_state.start_time
        st.session_state.stopped_early = False
        
        lvl = st.session_state.current_level
        if lvl > 10: st.session_state.won_amount = "16.000 €"
        elif lvl > 5: st.session_state.won_amount = "500 €"
        else: st.session_state.won_amount = "0 €"
        
    st.session_state.lock_choice = None

# --- Header ---
c1, c2 = st.columns([3, 1.5])
c1.caption(f"👤 Spieler: **{st.session_state.user_name}**")
if c2.button("Name ändern", use_container_width=True, type="secondary", disabled=st.session_state.lock_choice is not None):
    st.session_state.user_name = ""
    st.rerun()

# ==========================================
# MENÜ: START & HIGHSCORE
# ==========================================
if not st.session_state.game_active:
    st.title("💸 Wer wird Millionär?")
    st.write("15 Fragen zum Judentum trennen dich von der Million!")
    
    if st.button("🚀 SPIEL STARTEN", use_container_width=True, type="primary"):
        st.session_state.game_active = True
        st.session_state.game_over = False
        st.session_state.current_level = 1
        st.session_state.jokers = {"5050": True, "phone": True, "audience": True}
        st.session_state.active_options = None
        st.session_state.audience_result = None
        st.session_state.phone_result = None
        st.session_state.stopped_early = False
        st.session_state.score_saved = False
        st.session_state.celebration = None
        st.session_state.history_log = []
        st.session_state.lock_choice = None
        
        q_sehr_leicht = get_safe_sample([q for q in QUESTIONS if q["level"] == "Sehr Leicht"], 3)
        q_leicht = get_safe_sample([q for q in QUESTIONS if q["level"] == "Leicht"], 3)
        q_mittel = get_safe_sample([q for q in QUESTIONS if q["level"] == "Mittel"], 3)
        q_schwer = get_safe_sample([q for q in QUESTIONS if q["level"] == "Schwer"], 3)
        q_sehr_schwer = get_safe_sample([q for q in QUESTIONS if q["level"] == "Sehr Schwer"], 3)
        
        game_qs = q_sehr_leicht + q_leicht + q_mittel + q_schwer + q_sehr_schwer
        for q in game_qs:
            opts = q["options"].copy()
            random.shuffle(opts)
            q["shuffled_options"] = opts
            
        st.session_state.game_questions = game_qs
        st.session_state.start_time = time.time()
        st.rerun()

    st.markdown("---")
    st.subheader("🏆 Top 5 Highscores")
    scores = load_highscores()
    if scores:
        for i, s in enumerate(scores[:5]):
            st.write(f"**{i+1}. {s['name']}** ➡️ {s['won_amount']}")
    else: st.write("Noch keine Einträge.")

# ==========================================
# DAS SPIEL LÄUFT
# ==========================================
elif not st.session_state.game_over:
    lvl = st.session_state.current_level
    q = st.session_state.game_questions[lvl - 1]
    
    st.markdown(
        f"""
        <div class='mobile-status'>
            <span style='color: #8d99ae; font-size: 13px;'>Frage {lvl}/15 • {q['level']}</span><br>
            <span style='color: #fca311; font-size: 18px; font-weight: bold;'>Gewinnstufe: {MONEY_TREE[lvl]}</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    if st.session_state.celebration and st.session_state.lock_choice is None:
        cel = st.session_state.celebration
        if cel in ["500 €", "16.000 €"]:
            st.balloons()
            st.success(f"🎉 **Sicherheitsstufe erreicht!** {cel} gehören dir!")
        st.session_state.celebration = None

    # Dezente Joker (Typ: Secondary)
    jokers_disabled = st.session_state.lock_choice is not None
    j1, j2, j3 = st.columns(3)
    with j1:
        if st.button("⚖️ 50:50", disabled=jokers_disabled or not st.session_state.jokers["5050"], type="secondary", use_container_width=True):
            use_5050(); st.rerun()
    with j2:
        if st.button("👥 Publikum", disabled=jokers_disabled or not st.session_state.jokers["audience"], type="secondary", use_container_width=True):
            use_audience(); st.rerun()
    with j3:
        if st.button("☎️ Telefon", disabled=jokers_disabled or not st.session_state.jokers["phone"], type="secondary", use_container_width=True):
            st.session_state.jokers["phone"] = False
            st.session_state.phone_result = q.get("hint", "Keine Ahnung...")
            st.rerun()

    if st.session_state.audience_result:
        st.write("📊 *Publikumstendenz:*")
        for opt, pct in st.session_state.audience_result.items(): 
            st.progress(pct / 100, text=f"{opt}: {pct}%")
    if st.session_state.phone_result:
        st.info(f"☎️: \"{st.session_state.phone_result}\"")

    st.markdown("---")
    st.subheader(q["text"])
    
    # --- 2x2 ANTWORT-GRID ---
    opts = q["shuffled_options"]
    active_opts = st.session_state.active_options or opts
    letters = ["A", "B", "C", "D"]
    
    colA, colB = st.columns(2)
    cols = [colA, colB, colA, colB]
    
    for i in range(4):
        with cols[i]:
            current_option = opts[i]
            
            if st.session_state.lock_choice is None:
                if current_option in active_opts:
                    if st.button(f"{letters[i]}: {current_option}", key=f"btn_{i}", type="primary", use_container_width=True):
                        st.session_state.lock_choice = current_option
                        st.rerun()
                else:
                    st.markdown("<div style='min-height:85px;'></div>", unsafe_allow_html=True)
            else:
                if current_option not in active_opts:
                    st.markdown("<div style='min-height:85px;'></div>", unsafe_allow_html=True)
                else:
                    selected = st.session_state.lock_choice
                    correct = q["answer"]
                    css_class = "wwm-locked-btn"
                    
                    if current_option == selected:
                        if current_option == correct: css_class += " anim-sel-correct"
                        else: css_class += " anim-sel-wrong"
                    else:
                        if current_option == correct: css_class += " anim-rev-correct"
                        else: css_class += " anim-fade-wrong"
                            
                    st.markdown(f"<div class='{css_class}'>{letters[i]}: {current_option}</div>", unsafe_allow_html=True)

    # --- DER SPANNUNGS-DELAY ---
    if st.session_state.lock_choice is not None:
        time.sleep(3.5) 
        process_eval(st.session_state.lock_choice)
        st.rerun()

    st.markdown("---")
    with st.expander("💰 Gewinnleiter ansehen"):
        for i in range(15, 0, -1):
            if i == lvl: st.write(f"👉 **{MONEY_TREE[i]}**")
            elif i in [5, 10]: st.write(f"🛡️ {MONEY_TREE[i]}")
            elif i < lvl: st.write(f"✓ {MONEY_TREE[i]}")
            else: st.write(MONEY_TREE[i])
            
    if st.button(f"🏃 Aufhören mit {MONEY_TREE[lvl - 1]}", type="secondary", use_container_width=True, disabled=st.session_state.lock_choice is not None):
        st.session_state.game_over = True
        st.session_state.stopped_early = True
        st.session_state.won_amount = MONEY_TREE[lvl - 1]
        st.session_state.duration = time.time() - st.session_state.start_time
        st.rerun()

# ==========================================
# SPIELENDE / AUSWERTUNG
# ==========================================
else:
    st.title("🎬 Spiel vorbei!")
    if st.session_state.current_level > 15:
        st.balloons(); st.success(f"KORREKT! Du bist MILLIONÄR! 💰")
    elif st.session_state.stopped_early:
        st.info(f"Du gehst freiwillig mit **{st.session_state.won_amount}** nach Hause.")
    else:
        st.error(f"Falsch! Du fällst zurück auf **{st.session_state.won_amount}**.")

    if not st.session_state.score_saved:
        save_highscore(st.session_state.user_name, st.session_state.won_amount, st.session_state.duration)
        st.session_state.score_saved = True

    with st.expander("📚 Deine Fragen in dieser Runde ansehen"):
        for h in st.session_state.history_log:
            if h["is_correct"]:
                st.write(f"✅ **Frage:** {h['question']}")
            else:
                st.write(f"❌ **Frage:** {h['question']}")
                st.write(f"• Richtige Antwort: {h['correct_ans']}")
                st.caption(f"Erklärung: {h['explanation']}")
                st.write("---")
                
    if st.button("🔄 Neue Runde", use_container_width=True, type="primary"):
        st.session_state.game_active = False
        st.rerun()