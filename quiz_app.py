import streamlit as st
import random
import time
import json
import os
from Questions import QUESTIONS 

# --- Konfiguration & WWM-Design ---
st.set_page_config(page_title="Religions-Quiz: Millionär", page_icon="💸", layout="wide")

# --- CSS HACK: Studio-Optik & Mobile-Optimierung ---
st.markdown(
    """
    <style>
    html, body {
        touch-action: manipulation;
    }
    .stApp {
        background-color: #0e1117;
    }
    .stButton>button {
        min-height: 75px;
        font-size: 18px !important;
        font-weight: 600;
        border-radius: 40px;
        background-color: #1a1a2e;
        color: #e6e6e6;
        border: 2px solid #4a4e69;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .stButton>button:hover {
        border-color: #fca311;
        color: #fca311;
        box-shadow: 0 0 15px rgba(252, 163, 17, 0.6);
        transform: scale(1.02);
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(90deg, #fca311, #ffb703);
        color: #14213d;
        border: none;
        font-weight: bold;
    }
    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(90deg, #ffb703, #ffd166);
        box-shadow: 0 0 20px rgba(252, 163, 17, 0.8);
        color: #000;
        transform: scale(1.03);
    }
    @keyframes pulse-gold {
        0% { color: #fca311; text-shadow: 0 0 5px #fca311; }
        50% { color: #ffd166; text-shadow: 0 0 20px #ffd166; }
        100% { color: #fca311; text-shadow: 0 0 5px #fca311; }
    }
    .current-level {
        animation: pulse-gold 2s infinite;
        font-size: 1.2em;
        font-weight: bold;
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
    st.write("Bevor du auf dem heißen Stuhl Platz nimmst, trage bitte deinen Namen ein:")
    name_input = st.text_input("Dein Name:")
    if st.button("Auf den heißen Stuhl!"):
        if name_input.strip() == "": st.error("Bitte gib deinen echten Namen ein!")
        else:
            st.session_state.user_name = name_input.strip()
            st.rerun()

if not st.session_state.user_name:
    ask_name()
    st.stop()

# --- Optimierter Publikumsjoker (Berücksichtigt 50:50) ---
def use_audience():
    st.session_state.jokers["audience"] = False
    q = st.session_state.game_questions[st.session_state.current_level - 1]
    correct = q["answer"]
    lvl = st.session_state.current_level
    
    base = 70 if lvl <= 5 else (50 if lvl <= 10 else 35)
    correct_pct = random.randint(base, base + 15)
    
    # Prüfen ob 50:50 aktiv war
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
    
    # Logge den Versuch für das Lern-Tagebuch am Ende
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
c1, c2 = st.columns([4, 1])
c1.write(f"👤 Kandidat/in auf dem Stuhl: **{st.session_state.user_name}**")
if c2.button("Namen ändern", use_container_width=True):
    st.session_state.user_name = ""
    st.rerun()
st.markdown("---")

# ==========================================
# MENÜ: START & HIGHSCORE
# ==========================================
if not st.session_state.game_active:
    st.title("💸 Wer wird Millionär? - Judentum Edition")
    st.write("15 Fragen aus dem Unterricht trennen dich von der Million. Viel Erfolg!")
    
    if st.button("🚀 AUF DEN HEISSEN STUHL", use_container_width=True, type="primary"):
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
    st.subheader("🏆 Hall of Fame (Top 10)")
    scores = load_highscores()
    if scores:
        for i, s in enumerate(scores[:10]):
            st.write(f"**{i+1}. {s['name']}** ➡️ **{s['won_amount']}** (⏱️ {s['duration']} Sek.)")
    else: st.write("Noch keine Einträge. Hol dir die Million!")

# ==========================================
# DAS SPIEL LÄUFT
# ==========================================
elif not st.session_state.game_over:
    if st.session_state.celebration:
        cel = st.session_state.celebration
        if cel in ["500 €", "16.000 €"]:
            st.balloons()
            st.markdown(f"<div style='background-color:#198754; color:white; padding:15px; border-radius:10px; text-align:center; font-size:22px; font-weight:bold; margin-bottom:20px;'>🎉 SICHERHEITSSTUFE ERREICHT! Dir sind {cel} absolut sicher!</div>", unsafe_allow_html=True)
        elif cel == "correct":
            st.markdown("<div style='background-color:#198754; color:white; padding:15px; border-radius:10px; text-align:center; font-size:20px; font-weight:bold; margin-bottom:20px;'>✅ RICHTIG! Weiter zur nächsten Stufe!</div>", unsafe_allow_html=True)
        st.session_state.celebration = None
    
    st.sidebar.markdown("### 💰 Gewinnleiter")
    for i in range(15, 0, -1):
        if i == st.session_state.current_level: st.sidebar.markdown(f"<span class='current-level'>👉 {MONEY_TREE[i]}</span>", unsafe_allow_html=True)
        elif i in [5, 10]: st.sidebar.markdown(f"<span style='color:#ffd166; font-weight:bold;'>{MONEY_TREE[i]} 🛡️</span>", unsafe_allow_html=True)
        elif i < st.session_state.current_level: st.sidebar.markdown(f"<span style='color:#06d6a0'>✓ {MONEY_TREE[i]}</span>", unsafe_allow_html=True)
        else: st.sidebar.markdown(f"<span style='color:#8d99ae'>{MONEY_TREE[i]}</span>", unsafe_allow_html=True)
            
    lvl = st.session_state.current_level
    q = st.session_state.game_questions[lvl - 1]
    
    # Atmosphärischer Warnhinweis bei hohen Stufen
    if lvl > 10:
        st.markdown("<div style='background-color:#6f0a14; color:white; padding:8px; border-radius:5px; text-align:center; font-weight:bold;'>⚠️ Achtung Zocker-Zone: Ein Fehler wirft dich auf 16.000 € zurück!</div>", unsafe_allow_html=True)
    elif lvl > 5:
        st.markdown("<div style='background-color:#3f37c9; color:white; padding:8px; border-radius:5px; text-align:center; font-weight:bold;'>Hier bist du über der ersten Sicherheitsstufe (500 €).</div>", unsafe_allow_html=True)

    st.caption(f"Frage {lvl} von 15 • Kategorie: {q['level']}")
    st.header(f"Frage für {MONEY_TREE[lvl]}:")
    st.subheader(q["text"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    spacer, j1, j2, j3 = st.columns([4, 1.2, 1.2, 1.2])
    with j1:
        if st.button("⚖️ 50:50", disabled=not st.session_state.jokers["5050"], use_container_width=True):
            use_5050(); st.rerun()
    with j2:
        if st.button("👥 Publikum", disabled=not st.session_state.jokers["audience"], use_container_width=True):
            use_audience(); st.rerun()
    with j3:
        if st.button("☎️ Telefon", disabled=not st.session_state.jokers["phone"], use_container_width=True):
            st.session_state.jokers["phone"] = False
            st.session_state.phone_result = q.get("hint", "Da bin ich überfragt...")
            st.rerun()

    if st.session_state.audience_result:
        st.write("📊 **Das Publikum meint:**")
        for opt, pct in st.session_state.audience_result.items(): st.progress(pct / 100, text=f"{opt}: {pct}%")
    if st.session_state.phone_result:
        st.info(f"☎️ **Dein Telefonjoker flüstert:** \"{st.session_state.phone_result}\"")

    st.markdown("<br>", unsafe_allow_html=True)
    opts = q["shuffled_options"]
    active_opts = st.session_state.active_options or opts
    
    colA, colB = st.columns(2)
    with colA:
        if st.button(f"A: {opts[0]}", disabled=(opts[0] not in active_opts), use_container_width=True): check_answer(opts[0]); st.rerun()
        if st.button(f"C: {opts[2]}", disabled=(opts[2] not in active_opts), use_container_width=True): check_answer(opts[2]); st.rerun()
    with colB:
        if st.button(f"B: {opts[1]}", disabled=(opts[1] not in active_opts), use_container_width=True): check_answer(opts[1]); st.rerun()
        if st.button(f"D: {opts[3]}", disabled=(opts[3] not in active_opts), use_container_width=True): check_answer(opts[3]); st.rerun()

    st.markdown("---")
    if st.button(f"🏃 Aufhören & die sicheren {MONEY_TREE[lvl - 1]} mitnehmen!", type="secondary", use_container_width=True):
        st.session_state.game_over = True
        st.session_state.stopped_early = True
        st.session_state.won_amount = MONEY_TREE[lvl - 1]
        st.session_state.duration = time.time() - st.session_state.start_time
        st.rerun()

# ==========================================
# SPIELENDE / AUSWERTUNG & LERN-STAGE
# ==========================================
else:
    st.title("🎬 Das Spiel ist vorbei!")
    if st.session_state.current_level > 15:
        st.balloons(); st.success(f"UNFASSBAR! Du hast alle Fragen gemeistert und bist **MILLIONÄR!** 💰💰💰")
    elif st.session_state.stopped_early:
        st.info(f"Kluge Entscheidung! Du verlässt die Show freiwillig mit starken **{st.session_state.won_amount}**.")
    else:
        st.error(f"Schade, das war leider falsch! Du fällst zurück auf **{st.session_state.won_amount}**.")

    if not st.session_state.score_saved:
        save_highscore(st.session_state.user_name, st.session_state.won_amount, st.session_state.duration)
        st.session_state.score_saved = True

    st.write(f"⏱️ Gespielte Zeit: {round(st.session_state.duration, 1)} Sekunden")
    
    # NEU: Das didaktische Lern-Tagebuch (Sammelbox für Fehler)
    st.markdown("---")
    st.subheader("📚 Dein persönliches Lern-Protokoll")
    
    for h in st.session_state.history_log:
        if h["is_correct"]:
            st.markdown(f"🔹 **Frage:** {h['question']} ➡️ ✅ *Richtig beantwortet!*")
        else:
            with st.expander(f"🔸 **Frage verpasst:** \"{h['question']}\" (Klicke für Erklärung)"):
                st.write(f"❌ Deine Antwort: *{h['user_ans']}*")
                st.write(f"🎯 Richtige Antwort: **{h['correct_ans']}**")
                st.info(f"💡 **Erklärung für den Unterricht:** {h['explanation']}")
                
    st.markdown("---")
    if st.button("🔄 Neue Runde starten", use_container_width=True, type="primary"):
        st.session_state.game_active = False
        st.rerun()