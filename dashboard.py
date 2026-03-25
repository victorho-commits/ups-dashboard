import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time

FILE_PATH = r"C:\Users\31001277\OneDrive - Genscript USA Inc\Desktop\UPS Arrival Notice Folder\UPS Arrival Notice - YTD.xlsx"

st.set_page_config(page_title="UPS Dashboard", layout="wide")

@st.cache_data(ttl=5)
def load_data():
    if os.path.exists(FILE_PATH):
        return pd.read_excel(FILE_PATH)
    return pd.DataFrame()

st.title("📦 UPS Live Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.success("🟢 Automation Running")

with col2:
    st.info(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")

df = load_data()

if not df.empty:
    st.metric("Total Shipments", len(df))
    st.dataframe(df.sort_values(by="DateTimeReceived", ascending=False), use_container_width=True)
else:
    st.warning("Waiting for data...")

time.sleep(5)
st.rerun()
