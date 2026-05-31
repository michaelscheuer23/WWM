import streamlit as st
import random
import time
import json
import os
from Questions import QUESTIONS 

# --- Konfiguration & Mobile-First-Design ---
st.set_page_config(page_title="Religions-Quiz: Millionär", page_icon="💸", layout="centered")

# --- CSS HACK: Radikale Optimierung für Smartphones ---
st.markdown(
    """
    <style>
    html, body {
        touch-action: manipulation;
    }
    .stApp {
        background-color: #0e1117;
    }
    
    /* Hauptcontainer-Abstände für Mobilgeräte reduzieren */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    /* Antwort-Buttons extrem kompakt und daumenfreundlich */
    .stButton>button {
        min-height: 60px !important;
        font-size: 16px !important;
        font-weight: 600;
        border-radius: 20px;
        background-color: #1a1a2e;
        color: #e6e6e6;
        border: 2px solid #4a4e69;
        margin-bottom: 0.2rem !important;
        transition: all 0.2s ease;
    }
    
    /* Joker-Buttons kleiner gestalten */
    div[data-testid="stHorizontalBlock"] .stButton>button {
        min-height: 45px !important;
        font-size: 14px !important;
        border-radius: 12px;
        padding: 0.2rem !important;
    }
    
    .stButton>button:hover {
        border-color: #fca311;
        color: #fca311;
    }
    
    .stButton>button[kind="primary"] {
        background: linear-gradient(90deg, #fca311, #ffb703);
        color: #14213d;
        border: none;
        font-weight: bold;
    }

    /* Schicke, kompakte Status-Leiste oben */
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

@st.dialog("Willkommen im Studio! 💸")
def ask_name():
    st.write("Trage bitte deinen Namen ein:")
    name_input = st.text_input("Dein Name:")
    if st.button("Starten"):
        if name_input.strip() == "": st.error("Bitte gib deinen Namen ein!")
        else:
            st.session_state.user_name = name_input.strip()
            st.rerun()

if not st.session_state.user_name:
    ask_name()
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

def check_answer(selected):
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
        else: st.session_state.celebration = "correct"
            
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

# --- Header ---
c1, c2 = st.columns([3, 1.5])
c1.caption(f"👤 Spieler: **{st.session_state.user_name}**")
if c2.button("Name ändern", use_container_width=True):
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
    
    # NEU: Schlanke, mobile Statusleiste statt riesiger Sidebar
    st.markdown(
        f"""
        <div class='mobile-status'>
            <span style='color: #8d99ae; font-size: 14px;'>Frage {lvl}/15</span><br>
            <span style='color: #fca311; font-size: 20px; font-weight: bold;'>Es geht um: {MONEY_TREE[lvl]}</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    if st.session_state.celebration:
        cel = st.session_state.celebration
        if cel in ["500 €", "16.000 €"]:
            st.balloons()
            st.success(f"🎉 **Sicherheitsstufe erreicht!** {cel} gehören dir!")
        st.session_state.celebration = None
    
    # Frage direkt anzeigen
    st.subheader(q["text"])
    
    # JOKER-LEISTE (Kompakt nebeneinander)
    j1, j2, j3 = st.columns(3)
    with j1:
        if st.button("⚖️ 50:50", disabled=not st.session_state.jokers["5050"], use_container_width=True):
            use_5050(); st.rerun()
    with j2:
        if st.button("👥 Publikum", disabled=not st.session_state.jokers["audience"], use_container_width=True):
            use_audience(); st.rerun()
    with j3:
        if st.button("☎️ Telefon", disabled=not st.session_state.jokers["phone"], use_container_width=True):
            st.session_state.jokers["phone"] = False
            st.session_state.phone_result = q.get("hint", "Keine Ahnung...")
            st.rerun()

    # Joker-Ergebnisse schlank einblenden
    if st.session_state.audience_result:
        for opt, pct in st.session_state.audience_result.items(): 
            st.progress(pct / 100, text=f"{opt}: {pct}%")
    if st.session_state.phone_result:
        st.info(f"☎️: \"{st.session_state.phone_result}\"")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ANTWORT-BUTTONS (Direkt untereinander/Kompakt auf Mobile)
    opts = q["shuffled_options"]
    active_opts = st.session_state.active_options or opts
    
    # Für Mobile ist untereinander oft übersichtlicher als ein gepresstes 2x2 Grid
    for i, letter in enumerate(["A", "B", "C", "D"]):
        if st.button(f"{letter}: {opts[i]}", disabled=(opts[i] not in active_opts), use_container_width=True):
            check_answer(opts[i])
            st.rerun()

    st.markdown("---")
    
    # Gewinnleiter als ausklappbares Info-Element ans Ende setzen
    with st.expander("💰 Gesamte Gewinnleiter anzeigen"):
        for i in range(15, 0, -1):
            if i == lvl: st.write(f"👉 **{MONEY_TREE[i]}** (Aktuell)")
            elif i in [5, 10]: st.write(f"🛡️ {MONEY_TREE[i]} (Sicherheitsstufe)")
            elif i < lvl: st.write(f"✓ {MONEY_TREE[i]}")
            else: st.write(MONEY_TREE[i])
            
    if st.button(f"🏃 Aufhören mit {MONEY_TREE[lvl - 1]}", type="secondary", use_container_width=True):
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

    # Lern-Tagebuch kompakt halten
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