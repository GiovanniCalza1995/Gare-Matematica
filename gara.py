# --- VISUALIZZAZIONE GARA ---
        if sec_rimanenti > 120:
            st.title("🏆 CLASSIFICA LIVE")
            m, s = divmod(int(sec_rimanenti), 60)
            st.info(f"⏱️ Tempo rimanente: {m:02d}:{s:02d}")
            st.write(html_classifica, unsafe_allow_html=True)
            
        elif sec_rimanenti > 0:
            # QUI SPARISCE TUTTO: Niente st.write(html_classifica)
            m, s = divmod(int(sec_rimanenti), 60)
            st.markdown("<br><br><h1 style='text-align: center; font-size: 80px; color: #ff4b4b;'>🙈 CLASSIFICA NASCOSTA 🙈</h1>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: center; font-size: 180px; font-weight: bold; color: white;'>{m:02d}:{s:02d}</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 30px;'>La gara continua... i giudici stanno registrando gli ultimi punti!</p>", unsafe_allow_html=True)
        
        else:
            st.title("🏆 CLASSIFICA FINALE")
            st.error("⌛ GARA TERMINATA!")
            st.write(html_classifica, unsafe_allow_html=True)
