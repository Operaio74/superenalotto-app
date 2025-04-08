import streamlit as st
import pandas as pd
import random
from datetime import datetime

st.set_page_config(page_title="SuperEnalotto App", page_icon="🎰", layout="centered")

st.title("🎰 SuperEnalotto: Analisi e Generazione Combinazioni")

uploaded_file = st.file_uploader("Carica un file TXT con le estrazioni", type="txt")

def parse_data(file):
    lines = file.getvalue().decode("utf-8").splitlines()
    data = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 9:
            try:
                row = {
                    "data": datetime.strptime(parts[0], "%d/%m/%Y"),
                    "n1": int(parts[1]), "n2": int(parts[2]), "n3": int(parts[3]),
                    "n4": int(parts[4]), "n5": int(parts[5]), "n6": int(parts[6]),
                    "jolly": int(parts[7]), "superstar": int(parts[8])
                }
                data.append(row)
            except ValueError:
                continue
    return pd.DataFrame(data)

def frequenze_numeri(df):
    tutti_numeri = df[["n1", "n2", "n3", "n4", "n5", "n6"]].values.flatten()
    return pd.Series(tutti_numeri).value_counts().sort_index()

def numeri_ritardatari(df):
    tutti_numeri = set(range(1, 91))
    ultime_uscite = {n: None for n in tutti_numeri}
    for index, row in df[::-1].iterrows():
        estratti = set(row[["n1", "n2", "n3", "n4", "n5", "n6"]])
        for n in estratti:
            if ultime_uscite[n] is None:
                ultime_uscite[n] = row["data"]
    oggi = df["data"].max()
    ritardi = {n: (oggi - ultime_uscite[n]).days if ultime_uscite[n] else float("inf") for n in tutti_numeri}
    return pd.Series(ritardi).sort_values(ascending=False)

def genera_combinazioni(freq, include_rit, exclude_rit, n_comb):
    popolazione = list(freq.index)
    if include_rit:
        popolazione = include_rit + [n for n in popolazione if n not in include_rit]
    if exclude_rit:
        popolazione = [n for n in popolazione if n not in exclude_rit]
    combinazioni = []
    for _ in range(n_comb):
        combinazioni.append(sorted(random.sample(popolazione, 6)))
    return combinazioni

if uploaded_file:
    df = parse_data(uploaded_file)
    st.success(f"File caricato con {len(df)} estrazioni.")

    st.subheader("📊 Statistiche")
    freq = frequenze_numeri(df)
    ritardi = numeri_ritardatari(df)

    st.write("**Top 10 Numeri più frequenti:**")
    st.dataframe(freq.sort_values(ascending=False).head(10))

    st.write("**Top 10 Numeri più ritardatari:**")
    st.dataframe(ritardi.head(10))

    st.subheader("🎲 Generatore Combinazioni")

    n_rit_include = st.slider("Includi quanti numeri più ritardatari?", 0, 20, 0)
    n_rit_exclude = st.slider("Escludi quanti numeri più ritardatari?", 0, 20, 0)
    n_comb = st.number_input("Numero di combinazioni da generare", min_value=1, max_value=20, value=5)

    rit_include = list(ritardi.head(n_rit_include).index)
    rit_exclude = list(ritardi.head(n_rit_exclude).index)

    if st.button("Genera combinazioni"):
        combs = genera_combinazioni(freq, rit_include, rit_exclude, n_comb)
        st.write("**Combinazioni generate:**")
        for i, c in enumerate(combs, 1):
            st.markdown(f"**{i}**: `{c}`")

else:
    st.info("Carica un file per iniziare. Formato: `data n1 n2 n3 n4 n5 n6 jolly superstar`")
