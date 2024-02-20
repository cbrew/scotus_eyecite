import streamlit as st
import pandas as pd
from scotus_eyecite.interleave import interleave
import json
from tinyhtml import html,h
st.set_page_config(layout="wide")


df = pd.read_parquet('scotus_eyecite_train.pqt').sort_values("case_id")
index = st.slider("Case",min_value=0,max_value=df.shape[0]-1)
row = df.iloc[index]
st.title(row['case_id'])

text = row['text']
spans = json.loads(row['spans'])
groups = json.loads(row['groups'])

# st.json(interleave(text,spans))

st.json([group for group in groups if len(group) > 1])


