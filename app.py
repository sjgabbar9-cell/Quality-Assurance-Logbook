import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ===================================================
# CONFIG
# ===================================================
st.set_page_config("QA Physical Logbook", layout="wide")
CSV_PATH = "data/qa_logbook.csv"

# ===================================================
# USERS (LOGIN)
# ===================================================
USERS = {
    "qa_sup": "QA_SUP",
    "qa_head": "QA_HEAD",
    "qc_head": "QC_HEAD",
    "sort_head": "SORT_HEAD",
    "gm": "GM"
}
PASSWORD = "123"

# ===================================================
# STYLE
# ===================================================
st.markdown("""
<style>
.stApp { background:#FFE5D4; }
* { color:black !important; }
input, textarea, select { background:white !important; }

.card {
    background:white;
    padding:30px;
    border-radius:16px;
    text-align:center;
    height:220px;
    border:2px solid #ccc;
}
</style>
""", unsafe_allow_html=True)

# ===================================================
# SESSION
# ===================================================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "data" not in st.session_state:
    st.session_state.data = {}
if "saved" not in st.session_state:
    st.session_state.saved = False
if "user" not in st.session_state:
    st.session_state.user = None

# ===================================================
# LOGIN PAGE
# ===================================================
if st.session_state.user is None:

    st.title("QA Logbook Login")
    if os.path.exists("logo.png"):
        st.image("logo.png", width=100)

    uid = st.text_input("User ID")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if uid in USERS and pwd == PASSWORD:
            st.session_state.user = USERS[uid]
            st.session_state.page = "home"
        else:
            st.error("Invalid Credentials")

    st.stop()

# ===================================================
# SAVE FUNCTION
# ===================================================
def save_data(data):
    os.makedirs("data", exist_ok=True)

    data["QA_HEAD"] = "No"
    data["QC_HEAD"] = "No"
    data["SORT_HEAD"] = "No"
    data["GM"] = "No"

    new_df = pd.DataFrame([data])

    try:
        if os.path.exists(CSV_PATH):
            old_df = pd.read_csv(CSV_PATH)
            df = pd.concat([old_df, new_df], ignore_index=True)
        else:
            df = new_df
    except:
        if os.path.exists(CSV_PATH):
            os.rename(CSV_PATH, CSV_PATH.replace(".csv", "_backup.csv"))
        df = new_df

    df.to_csv(CSV_PATH, index=False)

# ===================================================
# DASHBOARD
# ===================================================
if st.session_state.page == "home":

    role = st.session_state.user

    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=80)
    with col_title:
        st.markdown("## QA Physical Parameter Logbook")

    st.divider()

    cols = st.columns(4 if role != "QA_SUP" else 3)

    with cols[0]:
        st.markdown('<div class="card">📝<h3>New Logbook</h3></div>', unsafe_allow_html=True)
        if st.button("Open Entry"):
            st.session_state.page = "entry"

    with cols[1]:
        st.markdown('<div class="card">📥<h3>Download</h3></div>', unsafe_allow_html=True)
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH,"rb") as f:
                st.download_button("Download CSV", f, "qa_logbook.csv")

    with cols[2]:
        st.markdown('<div class="card">📜<h3>Records</h3></div>', unsafe_allow_html=True)
        if st.button("View Records"):
            st.session_state.page = "history"

    if role != "QA_SUP":
        with cols[3]:
            st.markdown('<div class="card">✅<h3>Approvals</h3></div>', unsafe_allow_html=True)
            if st.button("Open Approvals"):
                st.session_state.page = "approval"

# ===================================================
# ENTRY PAGE
# ===================================================
elif st.session_state.page == "entry":

    st.header("Logbook Entry")

    d = st.session_state.data

    d["Date"] = st.date_input("Date")
    d["Batch"] = st.text_input("Batch No")
    d["Design"] = st.text_input("Design Name")
    d["Shade"] = st.text_input("Shade No")
    d["Production Boxes"] = st.number_input("Production Boxes")
    d["Checked Boxes"] = st.number_input("Boxes Checked")
    d["Stamping"] = st.selectbox("Stamping/Box Packing", ["OK","NOT OK"])
    d["Size"] = st.text_input("Tile Size")

    # ================= TABLE =================
    st.subheader("Measurement Table")

    table = st.data_editor(
        pd.DataFrame({
            "Size": ["600x600","600x1200"],
            "Diag Min": [0,0],
            "Diag Max": [0,0],
            "Gloss": ["",""]
        }),
        num_rows="dynamic"
    )

    def size_to_area(size):
        try:
            w,h = size.split("x")
            return float(w)*float(h)
        except:
            return 0

    if not table.empty:
        table["Area"] = table["Size"].apply(size_to_area)
        min_row = table.loc[table["Area"].idxmin()]
        max_row = table.loc[table["Area"].idxmax()]

        st.write("✅ Min Size:", min_row["Size"])
        st.write("✅ Max Size:", max_row["Size"])

    # ================= PLANARITY ✅ NEW =================
    st.subheader("Planarity Measurement (6 Tiles)")

    for tile in range(1,7):

        st.markdown(f"### Tile {tile}")

        st.markdown("#### PLC")
        for i in range(1,7):
            col1, col2 = st.columns(2)
            with col1:
                st.number_input(f"PLC{i} MIN", key=f"plc{tile}_{i}_min")
            with col2:
                st.number_input(f"PLC{i} MAX", key=f"plc{tile}_{i}_max")

        st.markdown("#### PWC")
        for i in range(1,13):
            col1, col2 = st.columns(2)
            with col1:
                st.number_input(f"PWC{i} MIN", key=f"pwc{tile}_{i}_min")
            with col2:
                st.number_input(f"PWC{i} MAX", key=f"pwc{tile}_{i}_max")

        st.markdown("#### Diagonal 1")
        for i in range(1,4):
            col1, col2 = st.columns(2)
            with col1:
                st.number_input(f"D1_{i} MIN", key=f"d1{tile}_{i}_min")
            with col2:
                st.number_input(f"D1_{i} MAX", key=f"d1{tile}_{i}_max")

        st.markdown("#### Diagonal 2")
        for i in range(1,4):
            col1, col2 = st.columns(2)
            with col1:
                st.number_input(f"D2_{i} MIN", key=f"d2{tile}_{i}_min")
            with col2:
                st.number_input(f"D2_{i} MAX", key=f"d2{tile}_{i}_max")

        st.divider()

    if st.button("Next"):
        st.session_state.page = "qa"

# ===================================================
# QA PAGE
# ===================================================
elif st.session_state.page == "qa":

    st.header("QA Parameters")

    d = st.session_state.data

    d["Randomness"] = st.selectbox(
        "Randomness",
        ["Standard","Uniform","Slightly","Moderately","Distinctly"]
    )

    d["Time Calibration"] = st.text_input("Time of Calibration")
    d["Verify Time"] = st.selectbox("Verification", ["OK","NOT OK"])

    if st.button("Save"):
        save_data(d)
        st.success("Saved ✅")

# ===================================================
# HISTORY
# ===================================================
elif st.session_state.page == "history":

    if os.path.exists(CSV_PATH):
        st.dataframe(pd.read_csv(CSV_PATH))

    if st.button("Back"):
        st.session_state.page = "home"

# ===================================================
# APPROVAL
# ===================================================
elif st.session_state.page == "approval":

    df = pd.read_csv(CSV_PATH)

    for i,row in df.iterrows():
        st.write(row["Batch"], row["Design"])

        if st.button("Approve", key=f"a{i}"):
            df.loc[i,st.session_state.user]="Yes"
            df.to_csv(CSV_PATH,index=False)
            st.rerun()
