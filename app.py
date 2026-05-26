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
.box {
    border:2px solid #aaa;
    padding:10px;
    border-radius:10px;
    text-align:center;
    margin-bottom:10px;
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

# ✅ ADDITION ONLY
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
# SAVE
# ===================================================
def save_data(data):
    os.makedirs("data", exist_ok=True)

    data["QA_HEAD"] = "No"
    data["QC_HEAD"] = "No"
    data["SORT_HEAD"] = "No"
    data["GM"] = "No"

    new_df = pd.DataFrame([data])

    if os.path.exists(CSV_PATH):
        old_df = pd.read_csv(CSV_PATH)
        df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        df = new_df

    df.to_csv(CSV_PATH, index=False)

# ===================================================
# DASHBOARD
# ===================================================
if st.session_state.page == "home":

    role = st.session_state.user

    cols = st.columns(3 if role == "QA_SUP" else 4)

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
            st.markdown('<div class="card">✅<h3>Approval Records</h3></div>', unsafe_allow_html=True)
            if st.button("Open Approvals"):
                st.session_state.page = "approval"

# ===================================================
# ENTRY PAGE (UNCHANGED)
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

    # ================= PLANARITY + IMAGES =================
    for tile in range(1,7):

        st.markdown(f"### Tile {tile}")

        st.image("assets/plc.png")
        for i in range(1,7):
            st.number_input(f"PLC{tile}_{i}_MIN", key=f"plc{tile}_{i}_min")
            st.number_input(f"PLC{tile}_{i}_MAX", key=f"plc{tile}_{i}_max")

        st.image("assets/pwc.png")
        for i in range(1,13):
            st.number_input(f"PWC{tile}_{i}_MIN", key=f"pwc{tile}_{i}_min")
            st.number_input(f"PWC{tile}_{i}_MAX", key=f"pwc{tile}_{i}_max")

        st.image("assets/diagonal.png")
        for i in range(1,4):
            st.number_input(f"D1{tile}_{i}_MIN", key=f"d1{tile}_{i}_min")
            st.number_input(f"D1{tile}_{i}_MAX", key=f"d1{tile}_{i}_max")

        for i in range(1,4):
            st.number_input(f"D2{tile}_{i}_MIN", key=f"d2{tile}_{i}_min")
            st.number_input(f"D2{tile}_{i}_MAX", key=f"d2{tile}_{i}_max")

    if st.button("Next"):
        st.session_state.page = "qa"

# ===================================================
# QA PAGE (FULL — RESTORED)
# ===================================================
elif st.session_state.page == "qa":

    st.header("QA Parameters")

    d = st.session_state.data

    d["Randomness"] = st.selectbox("Randomness", ["Standard","Uniform","Slightly","Moderately","Distinctly"])
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
# ✅ HISTORY TABLE (ADDED)
# ===================================================
elif st.session_state.page == "history":

    st.header("Previous Records")

    df = pd.read_csv(CSV_PATH)

    df.insert(0, "S.No", range(1, len(df)+1))

    st.dataframe(df)

    selected = st.selectbox("Select Record", df["S.No"])

    if st.button("Open Record"):
        st.session_state.selected_row = selected - 1
        st.session_state.page = "view_record"

    if st.button("Back"):
        st.session_state.page = "home"

# ===================================================
# ✅ FULL RECORD VIEW (ADDED)
# ===================================================
elif st.session_state.page == "view_record":

    df = pd.read_csv(CSV_PATH)
    row = df.loc[st.session_state.selected_row]

    st.header("Full Logbook Record")

    st.write(row)

    role = st.session_state.user

    if st.button("Approve"):
        df.loc[st.session_state.selected_row, role] = "Yes"
        df.to_csv(CSV_PATH, index=False)
        st.success("Approved ✅")

    if st.button("Reject"):
        df.drop(st.session_state.selected_row, inplace=True)
        df.to_csv(CSV_PATH, index=False)
        st.error("Rejected ❌")

    if st.button("Back"):
        st.session_state.page = "history"

# ===================================================
# APPROVAL (UNCHANGED)
# ===================================================
elif st.session_state.page == "approval":
    df = pd.read_csv(CSV_PATH)
    st.dataframe(df)
