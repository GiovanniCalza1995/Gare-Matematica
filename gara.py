import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time
import itertools

# 1. Configurazione Pagina
st.set_page_config(page_title="Gara Matematica Live", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. CSS per stile e centraggio
st.markdown("""
<style>
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; color: transparent !important; }
    .main .block-container { max-width: 1000px; padding-top: 1rem; }
    table { margin: auto; width: 100%; border-collapse: collapse; text-align: center; }
    th { font-size: 30px !important; background-color: #f0f2f6 !important; height: 60px; }
    td { font-size: 35px !important; font-weight: bold !important; height: 80px; border-bottom: 1px solid #ddd; }
    .stTitle { text-align: center; font-size: 60px !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNZIONI DI SINCRO ---
def carica_tutto():
    try:
        df_c = conn.read(worksheet="Classifica", ttl=0)
        df_p = conn.read(worksheet="Problemi", ttl=0)
        df_conf = conn.read(worksheet="Config", ttl=0)
        return df_c, df_p, df_conf
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def salva_tutto(df_c, df_p, df_conf):
    conn.update(worksheet="Classifica", data=df_c)
    conn.update(worksheet="Problemi", data=df_p)
    conn.update(worksheet="Config", data=df_conf)

# --- LOGICA DI STATO ---
df_classifica, df_problemi, df_config = carica_tutto()
gara_attiva = not df_classifica.empty

# --- SETUP INIZIALE ---
if not gara_attiva:
    st.title("⚙️ Setup Gara")
    c1, c2 = st.columns(2)
    with c1:
        num_s = st.number_input("1) Numero squadre", min_value=2, value=5)
        nomi_raw = st.text_area("2) Nomi squadre (uno per riga)", "Squadra 1\nSquadra 2\nSquadra 3\nSquadra 4\nSquadra 5")
        num_p = st.number_input("3) Numero Problemi", min_value=1, value=15)
    with c2:
        punti_p = st.number_input("4) Punti iniziali", value=200)
        durata = st.number_input("5) Durata gara (minuti)", min_value=1, value=90)
    
    if st.button("🚀 AVVIA E SINCRONIZZA"):
        lista = [n.strip() for n in nomi_raw.split("\n") if n.strip()]
        if len(lista) != num_s:
            st.error(f"Il numero di nomi ({len(lista)}) non coincide con il numero di squadre ({num_s})!")
        else:
            ciclo = itertools.cycle(["#d4edda", "#fff3cd", "#d1ecf1", "#f8d7da", "#e2e3e5", "#cce5ff", "#e8d5cb"])
            df_c = pd.DataFrame({"SQUADRA": lista, "PUNTI": [punti_p]*len(lista), "COLORE": [next(ciclo) for _ in lista]})
            df_p = pd.DataFrame({"ID": [f"P{i+1}" for i in range(num_p)], "VALORE": [20]*num_p})
            # Salviamo l'orario di fine come stringa nel foglio Config
            fine_orario = (datetime.now() + timedelta(minutes=durata)).strftime("%Y-%m-%d %H:%M:%S")
            df_conf = pd.DataFrame({"PARAMETRO": ["fine_gara"], "VALORE": [fine_orario]})
            
            salva_tutto(df_c, df_p, df_conf)
            st.rerun()

# --- GARA ---
else:
    # --- CALCOLO TIMER ---
    fine_str = df_config.loc[df_config["PARAMETRO"] == "fine_gara", "VALORE"].values[0]
    fine_dt = datetime.strptime(fine_str, "%Y-%m-%d %H:%M:%S")
    secondi_rimanenti = (fine_dt - datetime.now()).total_seconds()

    # --- SIDEBAR GIUDICE ---
    st.sidebar.header("🕹️ Pannello Giudice")
    sq_sel = st.sidebar.selectbox("Squadra", df_classifica["SQUADRA"].tolist())
    prob_sel = st.sidebar.selectbox("Problema", df_problemi["ID"].tolist())
    val_attuale = int(df_problemi.loc[df_problemi["ID"] == prob_sel, "VALORE"].values[0])
    
    st.sidebar.write(f"Valore attuale {prob_sel}: **{val_attuale} pt**")

    c1, c2 = st.sidebar.columns(2)
    if c1.button("✅ CORRETTA"):
        st.session_state.backup_c, st.session_state.backup_p = df_classifica.copy(), df_problemi.copy()
        df_classifica.loc[df_classifica["SQUADRA"] == sq_sel, "PUNTI"] += val_attuale
        df_problemi.loc[df_problemi["ID"] == prob_sel, "VALORE"] = max(10, val_attuale - 2)
        salva_tutto(df_classifica, df_problemi, df_config)
        st.rerun()

    if c2.button("❌ ERRATA"):
        st.session_state.backup_c, st.session_state.backup_p = df_classifica.copy(), df_problemi.copy()
        df_classifica.loc[df_classifica["SQUADRA"] == sq_sel, "PUNTI"] -= 5
        salva_tutto(df_classifica, df_problemi, df_config)
        st.rerun()

    if "backup_c" in st.session_state:
        if st.sidebar.button("⏪ ANNULLA ULTIMA AZIONE"):
            salva_tutto(st.session_state.backup_c, st.session_state.backup_p, df_config)
            del st.session_state.backup_c
            st.rerun()

    if st.sidebar.button("⚠️ RESET"):
        if st.sidebar.checkbox("Confermo reset totale"):
            conn.update(worksheet="Classifica", data=pd.DataFrame())
            conn.update(worksheet="Problemi", data=pd.DataFrame())
            conn.update(worksheet="Config", data=pd.DataFrame())
            st.rerun()

    # --- VISUALIZZAZIONE ---
    placeholder = st.empty()
    with placeholder.container():
        if secondi_rimanenti > 120:
            st.title("🏆 CLASSIFICA LIVE")
            m, s = divmod(int(secondi_rimanenti), 60)
            st.info(f"⏱️ Tempo rimanente: {m:02d}:{s:02d}")
            
            df_pro = df_classifica.sort_values(by="PUNTI", ascending=False)
            html = (df_pro.style
                    .apply(lambda r: [f'background-color: {r["COLORE"]}; color: black;', ''], axis=1, subset=["SQUADRA", "PUNTI"])
                    .hide(axis="index").to_html())
            st.write(html, unsafe_allow_html=True)
            
        elif secondi_rimanenti > 0:
            m, s = divmod(int(secondi_rimanenti), 60)
            st.markdown("<br><br><h1 style='text-align: center; font-size: 70px; color: #ff4b4b;'>🙈 Classifica nascosta 🙈</h1>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: center; font-size: 160px; font-weight: bold; text-align: center;'>{m:02d}:{s:02d}</h1>", unsafe_allow_html=True)
        
        else:
            st.title("🏆 CLASSIFICA FINALE")
            st.error("⌛ GARA TERMINATA!")
            df_pro = df_classifica.sort_values(by="PUNTI", ascending=False)
            html = (df_pro.style
                    .apply(lambda r: [f'background-color: {r["COLORE"]}; color: black;', ''], axis=1, subset=["SQUADRA", "PUNTI"])
                    .hide(axis="index").to_html())
            st.write(html, unsafe_allow_html=True)

    time.sleep(4)
    st.rerun()
