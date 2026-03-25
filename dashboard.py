import streamlit as st
import pandas as pd
import time
import re

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(
    page_title="UPS Live Dashboard",
    layout="wide"
)

FILE_PATH = "UPS Arrival Notice - YTD.xlsx"

# -------------------------------
# AUTO REFRESH (every 30 seconds)
# -------------------------------
REFRESH_INTERVAL = 30
st.markdown(f"⏱ Auto-refresh every {REFRESH_INTERVAL} seconds")
time.sleep(1)

# -------------------------------
# LOAD DATA
# -------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_excel(FILE_PATH)
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No data found.")
    st.stop()

# -------------------------------
# CLEAN DATA
# -------------------------------

# Clean Shipment ID (remove PackageID / Shipment)
def clean_shipment(val):
    if pd.isna(val):
        return val
    return re.sub(r"(PackageID|Shipment)", "", str(val), flags=re.IGNORECASE)

if "Shipment ID" in df.columns:
    df["Shipment ID"] = df["Shipment ID"].apply(clean_shipment)

# Convert datetime safely
if "DateTimeReceived" in df.columns:
    df["DateTimeReceived"] = pd.to_datetime(
        df["DateTimeReceived"], errors="coerce"
    )

# -------------------------------
# HEADER
# -------------------------------
st.title("📦 UPS Shipment Dashboard")
st.caption("Real-time tracking from Outlook → Excel → Dashboard")

# -------------------------------
# METRICS
# -------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Shipments", len(df))

with col2:
    if "Tracking Number" in df.columns:
        st.metric("Unique Tracking #", df["Tracking Number"].nunique())
    else:
        st.metric("Unique Tracking #", "N/A")

with col3:
    if "DateTimeReceived" in df.columns:
        latest = df["DateTimeReceived"].max()
        st.metric("Last Update", str(latest))
    else:
        st.metric("Last Update", "N/A")

# -------------------------------
# FILTERS
# -------------------------------
st.sidebar.header("🔍 Filters")

# Date filter
if "DateTimeReceived" in df.columns:
    min_date = df["DateTimeReceived"].min()
    max_date = df["DateTimeReceived"].max()

    date_range = st.sidebar.date_input(
        "Filter by Date",
        [min_date, max_date]
    )

    if len(date_range) == 2:
        df = df[
            (df["DateTimeReceived"] >= pd.to_datetime(date_range[0])) &
            (df["DateTimeReceived"] <= pd.to_datetime(date_range[1]))
        ]

# Search filter
search = st.sidebar.text_input("Search Tracking / Shipment ID")

if search:
    df = df[
        df.astype(str).apply(
            lambda row: row.str.contains(search, case=False).any(),
            axis=1
        )
    ]

# -------------------------------
# DATA TABLE
# -------------------------------
st.subheader("📋 Shipment Data")
st.dataframe(df, use_container_width=True)

# -------------------------------
# DOWNLOAD BUTTON
# -------------------------------
st.download_button(
    label="📥 Download Data",
    data=df.to_csv(index=False),
    file_name="UPS_Shipments.csv",
    mime="text/csv"
)

# -------------------------------
# AUTO REFRESH LOOP
# -------------------------------
time.sleep(REFRESH_INTERVAL)
st.rerun()
