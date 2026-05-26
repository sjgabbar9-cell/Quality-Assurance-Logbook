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
# USERS
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
if "selected_row" not in st.session_state:
    st.session_state.selected_row = None

# ===================================================
# LOGIN
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

    df_new = pd.DataFrame([data])

    if os.path.exists(CSV_PATH):
        df_old = pd.read_csv(CSV_PATH)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_csv(CSV_PATH, index=False)

# ===================================================
# DASHBOARD
# ===================================================
if st.session_state.page == "home":

    st.markdown("## QA Physical Parameter Logbook")

    cols = st.columns(4 if st.session_state.user != "QA_SUP" else 3)

    with cols[0]:
        st.markdown('<div class="card">📝<h3>New Logbook</h3></div>', unsafe_allow_html=True)
        if st.button("Open Entry"):
            st.session_state.page = "entry"

    with cols[1]:
        st.markdown('<div class="card">📥<h3>Download</h3></div>', unsafe_allow_html=True)

    with cols[2]:
        st.markdown('<div class="card">📜<h3>Records</h3></div>', unsafe_allow_html=True)
        if st.button("View Records"):
            st.session_state.page = "history"

    if st.session_state.user != "QA_SUP":
        with cols[3]:
            st.markdown('<div class="card">✅<h3>Approvals</h3></div>', unsafe_allow_html=True)
            if st.button("Open Approvals"):
                st.session_state.page = "approval"

# ===================================================
# QA PAGE (RESTORED ✅)
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
    d["Marker Test"] = st.selectbox("Marker Test", ["Normal Water","Hot Water"])
    d["Cleaning Agent"] = st.text_input("Cleaning Agent")
    d["Chamfering"] = st.selectbox("Chamfering", ["OK","NOT OK"])
    d["Visual Inspection"] = st.text_area("Visual Inspection")
    d["Foot Mark"] = st.text_area("Foot Mark")
    d["Bump Standard"] = st.text_input("Bump Standard")
    d["Remarks"] = st.text_area("Remarks")

    if st.button("Save"):
        save_data(d)
        st.success("Saved ✅")

# ===================================================
# HISTORY (CLICKABLE)
# ===================================================
elif st.session_state.page == "history":

    st.header("Previous Records")

    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)

        for i,row in df.iterrows():
            col1, col2 = st.columns([4,1])

            with col1:
                st.write(f"{row.get('Design')} | {row.get('Batch')}")

            with col2:
                if st.button("Open", key=f"open_{i}"):
                    st.session_state.selected_row = i
                    st.session_state.page = "view_record"

    if st.button("Back"):
        st.session_state.page = "home"

# ===================================================
# ✅ FULL RECORD VIEW (UPDATED ✅ ALL 6 TILES)
# ===================================================
elif st.session_state.page == "view_record":

    st.header("Full Logbook View")

    df = pd.read_csv(CSV_PATH)
    row = df.loc[st.session_state.selected_row]

    st.subheader("Basic Details")
    st.write(row)

    # ================= PLANARITY =================
    for tile in range(1,7):

        st.markdown(f"### Tile {tile}")

        # PLC
        st.markdown("#### PLC")
        for i in range(1,7):
            st.write(f"PLC{i} → Min: {row.get(f'plc{tile}_{i}_min')} | Max: {row.get(f'plc{tile}_{i}_max')}")

        # PWC
        st.markdown("#### PWC")
        for i in range(1,13):
            st.write(f"PWC{i} → Min: {row.get(f'pwc{tile}_{i}_min')} | Max: {row.get(f'pwc{tile}_{i}_max')}")

        # Diagonal
        st.markdown("#### Diagonal")
        for i in range(1,4):
            st.write(f"D1_{i} → Min: {row.get(f'd1{tile}_{i}_min')} | Max: {row.get(f'd1{tile}_{i}_max')}")

        for i in range(1,4):
            st.write(f"D2_{i} → Min: {row.get(f'd2{tile}_{i}_min')} | Max: {row.get(f'd2{tile}_{i}_max')}")

        st.divider()

    # ================= QA DATA =================
    st.subheader("QA Details")

    st.write(f"Randomness: {row.get('Randomness')}")
    st.write(f"Calibration: {row.get('Time Calibration')}")
    st.write(f"Verification: {row.get('Verify Time')}")
    st.write(f"Marker Test: {row.get('Marker Test')}")
    st.write(f"Cleaning: {row.get('Cleaning Agent')}")
    st.write(f"Chamfering: {row.get('Chamfering')}")
    st.write(f"Foot Mark: {row.get('Foot Mark')}")
    st.write(f"Bump: {row.get('Bump Standard')}")
    st.write(f"Remarks: {row.get('Remarks')}")

    st.divider()

    # ================= APPROVAL =================
    role = st.session_state.user

    col1, col2 = st.columns(2)

    if col1.button("✅ Approve"):
        df.loc[st.session_state.selected_row, role] = "Yes"
        df.to_csv(CSV_PATH, index=False)
        st.success("Approved ✅")

    if col2.button("❌ Reject"):
        df.drop(st.session_state.selected_row, inplace=True)
        df.to_csv(CSV_PATH, index=False)
        st.error("Rejected ❌")

    if st.button("Back"):
        st.session_state.page = "history"

# ===================================================
# APPROVAL PAGE
# ===================================================
elif st.session_state.page == "approval":

    df = pd.read_csv(CSV_PATH)

    for i,row in df.iterrows():
        st.write(row["Batch"], row["Design"])

        if st.button("Approve", key=f"a{i}"):
            df.loc[i,st.session_state.user]="Yes"
            df.to_csv(CSV_PATH,index=False)
            st.rerun()
