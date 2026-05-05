import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="Tabellone Gara Matematica", layout="wide")

# Inizializzazione Dati (Stato della sessione)
if 'log' not in st.session_state:
    st.session_state.log = []
if 'squadre' not in st.session_state:
    # Aggiungi qui i nomi delle tue squadre
    nomi = ["Pitagora", "Euclide", "Archimede", "Gauss", "Newton"]
    st.session_state.squadre = {n: {"Punti": 200, "Errori": 0} for n in nomi}
if 'problemi' not in st.session_state:
    # Configura i punti base per ogni problema
    st.session_state.problemi = {f"Prob {i}": 20 for i in range(1, 11)}

st.title("🏆 Dashboard Gara a Squadre")

# --- LATERALE: INSERIMENTO DATI (Solo per i giudici) ---
st.sidebar.header("Pannello Giudice")
squadra_scelta = st.sidebar.selectbox("Seleziona Squadra", list(st.session_state.squadre.keys()))
prob_scelto = st.sidebar.selectbox("Seleziona Problema", list(st.session_state.problemi.keys()))
esito = st.sidebar.radio("Esito Risposta", ["Corretta ✅", "Sbagliata ❌"])

if st.sidebar.button("Registra Risposta"):
    punti_attuali = st.session_state.problemi[prob_scelto]
    
    if esito == "Corretta ✅":
        # Bonus: Punteggio base del problema
        st.session_state.squadre[squadra_scelta]["Punti"] += punti_attuali
        # Il valore del problema scende leggermente per gli altri (dinamicità)
        st.session_state.problemi[prob_scelto] = max(10, punti_attuali - 2)
        st.session_state.log.append(f"{datetime.now().strftime('%H:%M')} - {squadra_scelta} ha risolto {prob_scelto} (+{punti_attuali})")
    else:
        # Malus: -5 punti per errore
        st.session_state.squadre[squadra_scelta]["Punti"] -= 5
        st.session_state.squadre[squadra_scelta]["Errori"] += 1
        st.session_state.log.append(f"{datetime.now().strftime('%H:%M')} - {squadra_scelta} ERRORE su {prob_scelto} (-5)")
    
    st.sidebar.success("Registrato!")

---

# --- CENTRALE: CLASSIFICA E LOG ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Classifica in Tempo Reale")
    df = pd.DataFrame.from_dict(st.session_state.squadre, orient='index')
    df = df.sort_values(by="Punti", ascending=False)
    # Visualizzazione con stili (colori)
    st.table(df.style.highlight_max(axis=0, subset=["Punti"], color="#2ecc71"))

with col2:
    st.subheader("Ultimi Eventi")
    for msg in reversed(st.session_state.log[-10:]):
        st.write(msg)

# Sezione Valore Problemi
st.write("---")
st.subheader("Valore Attuale Problemi (Dinamico)")
cols_prob = st.columns(len(st.session_state.problemi))
for i, (p, val) in enumerate(st.session_state.problemi.items()):
    cols_prob[i].metric(p, f"{val} pt")
