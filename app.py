import streamlit as st
import pandas as pd
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
# SESSION
# ===================================================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "data" not in st.session_state:
    st.session_state.data = {}
if "user" not in st.session_state:
    st.session_state.user = None
if "selected_row" not in st.session_state:
    st.session_state.selected_row = None

# ===================================================
# LOGIN
# ===================================================
if st.session_state.user is None:

    st.title("QA Logbook Login")

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

    st.title("QA Logbook")

    if st.button("New Entry"):
        st.session_state.page = "entry"

    if st.button("View Records"):
        st.session_state.page = "history"

# ===================================================
# ENTRY (UNCHANGED BASIC)
# ===================================================
elif st.session_state.page == "entry":

    d = st.session_state.data

    d["Date"] = st.date_input("Date")
    d["Batch"] = st.text_input("Batch")
    d["Design"] = st.text_input("Design")
    d["Size"] = st.text_input("Size")

    if st.button("Next"):
        st.session_state.page = "qa"

# ===================================================
# QA PAGE (FULL ✅ RESTORED)
# ===================================================
elif st.session_state.page == "qa":

    d = st.session_state.data

    d["Randomness"] = st.selectbox("Randomness", ["Standard","Uniform","Slightly","Moderately","Distinctly"])
    d["Time Calibration"] = st.text_input("Time Calibration")
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
        st.session_state.page = "home"

# ===================================================
# HISTORY (TABLE VIEW ✅)
# ===================================================
elif st.session_state.page == "history":

    st.header("Records")

    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df.insert(0, "S.No", range(1, len(df)+1))

        st.dataframe(df, use_container_width=True)

        selected = st.selectbox("Select S.No", df["S.No"])

        if st.button("Open Record"):
            st.session_state.selected_row = selected - 1
            st.session_state.page = "view_record"

    if st.button("Back"):
        st.session_state.page = "home"

# ===================================================
# ✅ FULL RECORD VIEW (COMPLETE ✅)
# ===================================================
elif st.session_state.page == "view_record":

    df = pd.read_csv(CSV_PATH)
    row = df.loc[st.session_state.selected_row]

    st.header("Full Logbook Record")

    # BASIC DETAILS
    st.subheader("Basic Details")
    st.write(f"Date: {row.get('Date')}")
    st.write(f"Batch: {row.get('Batch')}")
    st.write(f"Design: {row.get('Design')}")
    st.write(f"Size: {row.get('Size')}")

    st.divider()

    # PLANARITY SUMMARY
    st.subheader("Planarity Summary")
    st.write(f"S/S Min: {row.get('SS Min')}")
    st.write(f"S/S Max: {row.get('SS Max')}")
    st.write(f"C/C Min: {row.get('CC Min')}")
    st.write(f"C/C Max: {row.get('CC Max')}")

    st.divider()

    # ALL 6 TILES
    for tile in range(1,7):

        st.markdown(f"### Tile {tile}")

        for i in range(1,7):
            st.write(f"PLC{i}: {row.get(f'plc{tile}_{i}_min')} / {row.get(f'plc{tile}_{i}_max')}")

        for i in range(1,13):
            st.write(f"PWC{i}: {row.get(f'pwc{tile}_{i}_min')} / {row.get(f'pwc{tile}_{i}_max')}")

        for i in range(1,4):
            st.write(f"D1{i}: {row.get(f'd1{tile}_{i}_min')} / {row.get(f'd1{tile}_{i}_max')}")

        for i in range(1,4):
            st.write(f"D2{i}: {row.get(f'd2{tile}_{i}_min')} / {row.get(f'd2{tile}_{i}_max')}")

    st.divider()

    # QA DETAILS (FULL ✅)
    st.subheader("QA Parameters")

    st.write(f"Randomness: {row.get('Randomness')}")
    st.write(f"Calibration Time: {row.get('Time Calibration')}")
    st.write(f"Verification: {row.get('Verify Time')}")
    st.write(f"Marker Test: {row.get('Marker Test')}")
    st.write(f"Cleaning Agent: {row.get('Cleaning Agent')}")
    st.write(f"Chamfering: {row.get('Chamfering')}")
    st.write(f"Visual Inspection: {row.get('Visual Inspection')}")
    st.write(f"Foot Mark: {row.get('Foot Mark')}")
    st.write(f"Bump Standard: {row.get('Bump Standard')}")
    st.write(f"Remarks: {row.get('Remarks')}")

    st.divider()

    # APPROVAL
    role = st.session_state.user

    col1, col2 = st.columns(2)

    if col1.button("Approve"):
        df.loc[st.session_state.selected_row, role] = "Yes"
        df.to_csv(CSV_PATH, index=False)
        st.success("Approved ✅")

    if col2.button("Reject"):
        df.drop(st.session_state.selected_row, inplace=True)
        df.to_csv(CSV_PATH, index=False)
        st.error("Rejected ❌")

    if st.button("Back"):
        st.session_state.page = "history"
``
