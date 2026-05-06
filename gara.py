# --- CSS "FORZA BRUTA" PER CENTRAGGIO TOTALE ---
st.markdown("""
<style>
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
        color: transparent !important;
    }
    [data-testid="stHeader"] button {
        color: #555 !important;
        visibility: visible !important;
    }
    [data-testid="stStatusWidget"] { visibility: hidden !important; }
    
    .main .block-container { max-width: 900px; padding-top: 1rem; }
    div[data-testid="stTable"] table { margin-left: auto; margin-right: auto; width: 100% !important; }
    
    /* 1. Reset totale di allineamenti e padding per le celle */
    div[data-testid="stTable"] th, div[data-testid="stTable"] td {
        height: 80px !important;
        padding: 0 !important; 
        vertical-align: middle !important;
        text-align: center !important;
    }
    
    /* 2. Forza il Flexbox su TUTTI i discendenti della cella */
    div[data-testid="stTable"] td *, div[data-testid="stTable"] th * {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding: 0 !important;
        width: 100% !important;
    }

    /* 3. Stili caratteri */
    thead th {
        font-size: 36px !important;
        background-color: #f0f2f6 !important;
        color: #000000 !important;
    }
    
    tbody td {
        font-size: 32px !important;
        font-weight: bold !important;
    }
    
    .stTitle { text-align: center; font-size: 60px !important; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)
