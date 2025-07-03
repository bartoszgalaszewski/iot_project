import time
import pandas as pd
import streamlit as st
from pymilvus import connections, Collection, utility

MILVUS_HOST = "milvus"
MILVUS_PORT = "19530"
COLLECTION  = "env_vectors"

connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

if not utility.has_collection(COLLECTION):
    st.error(f"Kolekcja **{COLLECTION}** nie istnieje! "
             "Poczekaj aż Consumer wstawi pierwszy rekord.")
    st.stop()

col = Collection(COLLECTION)

if not col.has_index():
    with st.spinner("Tworzenie indeksu HNSW (jednorazowo)…"):
        col.create_index(
            field_name="vector",
            index_params={
                "index_type":  "HNSW",
                "metric_type": "L2",
                "params": {"M": 16, "efConstruction": 200},
            },
        )

col.load()

if col.num_entities == 0:
    st.info("⏳  Czekam na pierwszy rekord z czujnika… "
            "Strona odświeży się automatycznie.")
    time.sleep(5)
    st.experimental_rerun()

st.title("🔍 Podobieństwo warunków środowiskowych")

city = st.text_input("Miasto referencyjne", "Warsaw")
k    = st.slider("Liczba podobnych rekordów", min_value=1, max_value=20, value=5)

if city:
    ref = col.query(
        expr=f"city == '{city}'",
        output_fields=["vector", "city", "ts"],
        limit=1,
        order_by="ts desc",
    )

    if ref:
        ref_vec = ref[0]["vector"]

        res = col.search(
            data=[ref_vec],
            anns_field="vector",
            param={"metric_type": "L2", "params": {"nprobe": 16}},
            limit=k,
            output_fields=["city", "ts"],
        )

        rows = []
        for hit in res[0]:
            obj = hit.entity.get_field_data()
            obj["distance"] = hit.distance
            rows.append(obj)

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Brak zapisanych pomiarów dla tego miasta.")
