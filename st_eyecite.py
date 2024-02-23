import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components

from scotus_eyecite.interleave import interleave,present

st.set_page_config(layout="wide")


df = pd.read_parquet('scotus_eyecite_train.pqt').sort_values("case_id")
index = st.slider("Case",min_value=0,max_value=df.shape[0]-1)
row = df.iloc[index]
st.title(row['case_id'])

fulltext = row['text']
spans = json.loads(row['spans'])
groups = json.loads(row['groups'])

html_tab,span_tab,group_tab,spans_tab2 = st.tabs(["HTML","SPANS","GROUPS", "SPANS2"])

with html_tab:
    components.html(present(fulltext,spans),height=1200,scrolling=True)
with span_tab:
    st.table(interleave(fulltext,spans))
with group_tab:
    for group in groups:
        if len(group) > 1:
            st.table(group)
with spans_tab2:
    st.table(spans)







