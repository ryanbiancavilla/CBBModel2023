from CBBModel2023 import proj_scores
import streamlit as st
import pandas as pd

st.title("""
2023-24 College Basketball Model
""")
st.text("""
Updated Daily With Odds From Oddsshark
""")

st.write(proj_scores)