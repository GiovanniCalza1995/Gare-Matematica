import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="Gestione Gara Matematica", layout="wide")

# --- INIZIALIZZAZIONE STATO ---
if 'gara_avviata' not in st.session_state:
    st.session_state.gara_avviata = False
if 'log' not in st.session_state:
    st.session_state.log = []

# --- SCHERMATA DI CONFIGURAZIONE ---
if not st.session_state.gara_avviata:
    st.title("⚙️ Configurazione Nuova Gara")
    
    col_conf1, col_conf2 = st.columns(2)
    
    with col_conf1:
        num_squadre = st.number_input("1) Quante squadre partecipano?", min_value=2, max_value=50, value=5)
        nomi_input = st.text_area("2) Inserisci i nomi delle squadre (uno per riga)", 
                                  value="Squadra A\nSquadra B\nSquadra C\nSquadra D\nSquadra E")
    
    with col_conf2:
        num_problemi = st.number_input("3) Quanti problemi ci sono in totale?", min_value=1, max_value=50, value=10)
        punti_partenza = st.number_input("Punti iniziali per squadra", value=200)

    if st.button("🚀 AVVIA GARA"):
        lista_nomi = [n.strip() for n in nomi_input.split("\n") if n.strip()]
        
        # Controllo se il numero di nomi corrisponde
        if len(lista_nomi) != num_squadre:
            st.error(f"Attenzione: hai indicato {num_squadre} squadre ma hai inserito {len(lista_nomi)} nomi.")
        else:
            # Inizializza i dati della gara
            st.session_state.squadre = {n: {"Punti": punti_partenza, "Errori": 0} for n in lista_nomi}
            st.session_state.problemi = {f"Prob {i}": 20 for i in range(1, num_problemi + 1)}
            st.session_state.gara_avviata = True
            st.rerun()

# --- INTERFACCIA GARA (Si attiva dopo l'avvio) ---
else:
    st.title("🏆 Dashboard Gara Live")
    
    # Tasto per resettare tutto e tornare alla configurazione
    if st.sidebar.button("⚠️ Reset Totale"):
        st.session_state.gara_avviata = False
        st.rerun()

    # --- LATERALE: INSERIMENTO DATI ---
    st.sidebar.header("Pannello Giudice")
    squadra_scelta = st.sidebar.selectbox("Seleziona Squadra", list(st.session_state.squadre.keys()))
    prob_scelto = st.sidebar.selectbox("Seleziona Problema", list(st.session_state.problemi.keys()))
    esito = st.sidebar.radio("Esito Risposta", ["Corretta ✅", "Sbagliata ❌"])

    if st.sidebar.button("Registra Risposta"):
        punti_attuali = st.session_state.problemi[prob_scelto]
        
        if esito == "Corretta ✅":
            st.session_state.squadre[squadra_scelta]["Punti"] += punti_attuali
            # Logica bonus/malus: il valore cala di 2 punti ogni volta che viene risolto
            st.session_state.problemi[prob_scelto] = max(10, punti_attuali - 2)
            st.session_state.log.append(f"{datetime.now().strftime('%H:%M')} - {squadra_scelta} risolve {prob_scelto} (+{punti_attuali})")
        else:
            st.session_state.squadre[squadra_scelta]["Punti"] -= 5
            st.session_state.squadre[squadra_scelta]["Errori"] += 1
            st.session_state.log.append(f"{datetime.now().strftime('%H:%M')} - {squadra_scelta} ERRORE su {prob_scelto} (-5)")
        st.rerun()

    # --- CENTRALE: CLASSIFICA E LOG ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Classifica")
        df = pd.DataFrame.from_dict(st.session_state.squadre, orient='index')
        df = df.sort_values(by="Punti", ascending=False)
        st.table(df)

    with col2:
        st.subheader("Cronologia")
        for msg in reversed(st.session_state.log[-10:]):
            st.write(msg)

    # Sezione Valore Problemi
    st.divider()
    st.subheader("Valore Attuale Problemi")
    # Griglia dinamica per i problemi
    cols_prob = st.columns(min(len(st.session_state.problemi), 10)) 
    for i, (p, val) in enumerate(st.session_state.problemi.items()):
        cols_prob[i % 10].metric(p, f"{val} pt")
