import streamlit as st
import pandas as pd
import random
import requests
from io import StringIO

st.set_page_config(page_title="SuperEnalotto App", layout="wide")
st.title("🎯 SuperEnalotto - Analisi e Generazione Combinazioni")

# --- Funzione per caricare i dati da GitHub ---
def carica_dati_da_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data_txt = StringIO(response.text)
        df = pd.read_csv(data_txt, sep=" ", header=None)
        df.columns = ["Data", "N1", "N2", "N3", "N4", "N5", "N6", "Jolly", "Superstar"]
        return df
    except Exception as e:
        st.error(f"Errore nel caricamento del file: {e}")
        return None

# --- URL del file TXT su GitHub ---
st.sidebar.subheader("📄 File delle estrazioni")
url_file = st.sidebar.text_input(
    "Inserisci l'URL RAW del file delle estrazioni SuperEnalotto da GitHub:",
    "https://raw.githubusercontent.com/Operaio74/superenalotto-app/refs/heads/main/estrazioni2025.txt"
)

if url_file:
    df = carica_dati_da_github(url_file)
    if df is not None:
        st.success("✅ File caricato correttamente!")

        # --- Mostra le prime righe del DataFrame ---
        with st.expander("📊 Anteprima estrazioni"):
            st.dataframe(df.head(10), use_container_width=True)

        # --- Calcolo dei ritardi per ciascun numero ---
        tutti_numeri = list(range(1, 91))
        ultimi_numeri = df[["N1", "N2", "N3", "N4", "N5", "N6"]].values[::-1]
        ritardi = {n: 0 for n in tutti_numeri}

        for estrazione in ultimi_numeri:
            for numero in tutti_numeri:
                if numero not in estrazione:
                    ritardi[numero] += 1
                else:
                    ritardi[numero] = 0

        ritardi_ordinati = sorted(ritardi.items(), key=lambda x: x[1], reverse=True)

        # --- Parametri utente ---
        st.sidebar.subheader("⚙️ Parametri combinazione")
        num_combinazioni = st.sidebar.slider("Numero di combinazioni da generare", 1, 10, 5)
        num_ritardatari = st.sidebar.slider("Quanti ritardatari considerare?", 0, 30, 10)
        azione_ritardatari = st.sidebar.radio("Vuoi includere o escludere i ritardatari?", ["Includi", "Escludi"])

        numeri_ritardatari = [n for n, _ in ritardi_ordinati[:num_ritardatari]]

        # --- Generazione combinazioni ---
        def genera_combinazione():
            pool = [n for n in tutti_numeri if (n in numeri_ritardatari) == (azione_ritardatari == "Includi")]
            return sorted(random.sample(pool, 6)) if len(pool) >= 6 else []

        st.subheader("🎰 Combinazioni Generate")
        for i in range(num_combinazioni):
            combinazione = genera_combinazione()
            if combinazione:
                st.success(f"Combinazione {i+1}: {combinazione}")
            else:
                st.error("⚠️ Non ci sono abbastanza numeri per generare una combinazione. Riduci i filtri sui ritardatari.")

        # --- Mostra ritardatari
        with st.expander("🔎 Ritardatari attuali"):
            st.table(pd.DataFrame(ritardi_ordinati[:30], columns=["Numero", "Ritardo"]))
    else:
        st.warning("⚠️ Controlla l'URL del file delle estrazioni.")
