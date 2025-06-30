import streamlit as st
from pymilvus import connections, Collection
import pandas as pd

connections.connect(host='milvus', port='19530')
col = Collection('env_vectors')

st.title('Podobieństwo warunków środowiskowych')
city = st.text_input('Miasto referencyjne', 'Warsaw')
k = st.slider('Liczba podobnych rekordów', 1, 20, 5)

# Pobierz najnowszy rekord referencyjny
data = col.query(expr=f"city == '{city}'", output_fields=['vector','city','ts'], limit=1, offset=0, order_by='ts desc')
if data:
    ref_vec = data[0]['vector']
    res = col.search([ref_vec], 'vector', param={'metric_type':'L2','params':{'nprobe':16}}, limit=k, output_fields=['city','ts'])
    df = pd.DataFrame([{**hit.entity.get_field_data(), 'distance': hit.distance} for hit in res[0]])
    st.dataframe(df)
else:
    st.warning('Brak danych dla tego miasta.')