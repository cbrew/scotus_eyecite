"""
Visualizer for citation dataset.
"""

import json
import streamlit as st
import spacy
import pandas as pd
import streamlit.components.v1 as components
from scotus_eyecite.interleave import interleave, present, paras
from yattag import Doc

st.set_page_config(layout="wide")

nlp = spacy.load('en_core_web_md')




df = pd.read_parquet("scotus_eyecite_train.pqt").sort_values("case_id")
index = st.slider("Case", min_value=0, max_value=df.shape[0] - 1)
row = df.iloc[index]
st.title(row["case_id"])

fulltext = row["text"]
spans = json.loads(row["spans"])
groups = json.loads(row["groups"])

html_tab, span_tab, group_tab, spacy_tab = st.tabs(
    ["HTML", "SPANS", "GROUPS", "SPACY"]
)

with html_tab:
    components.html(present(fulltext, spans), height=1200, scrolling=True)
with span_tab:
    st.table(interleave(fulltext, spans))
with group_tab:
    for group in groups:
        if len(group) > 1:
            st.table(group)


def sent_present(fulltext, sdoc):
    doc, tag, text = Doc().tagtext()
    with tag('html'):
        with tag("body"):
            for para in paras(fulltext):
                if para['type'] == "whitespace":
                    doc.stag("hr")
                else:
                    para_text = para['text']
                    with tag("p"):
                        text(para_text)
                    start = para['start']
                    end = para['end']
                    sents = [s for s in sdoc.sents if (start <= s[0].idx ) and ((s[-1].idx + len(s[-1].text)) <= end)]
                    with tag("p"):
                        text(f"[{start}:{end}]")
                        doc.stag("br")
                        for sent in sents:
                            text(f"{sent[0].idx}:{sent[-1].idx}")
                            doc.text(": ")
                            text(sent.text)
                            doc.stag("br")


    return doc.getvalue()


with spacy_tab:
    doc = nlp(fulltext)



    components.html(sent_present(fulltext,doc), height=1200)


