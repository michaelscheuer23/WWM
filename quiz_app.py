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