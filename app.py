import streamlit as st
import pandas as pd
from datetime import datetime
import os

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="QA Logbook", layout="wide")
CSV_PATH = "data/qa_logbook.csv"

# -------------------------------
# USERS
# -------------------------------
USERS = {
    "qa_sup": "QA_SUP",
    "qa_head": "QA_HEAD",
    "qc_head": "QC_HEAD",
    "sort_head": "SORT_HEAD",
    "gm": "GM"
}
PASSWORD = "123"

# -------------------------------
# STYLE
# -------------------------------
st.markdown("""
<style>
.stApp { background:#FFE5D4; }
* { color:black !important; }
.card {
    background:white; padding:30px; border-radius:16px;
    text-align:center; height:200px; border:2px solid #ccc;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# SESSION
# -------------------------------
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user" not in st.session_state:
    st.session_state.user = None

# -------------------------------
# SAVE
# -------------------------------
def save_data(record):
    os.makedirs("data", exist_ok=True)

    df_new = pd.DataFrame([record])

    if os.path.exists(CSV_PATH):
        df_old = pd.read_csv(CSV_PATH)
        df = pd.concat([df_old, df_new])
    else:
        df = df_new

    df.to_csv(CSV_PATH, index=False)

# -------------------------------
# LOGIN PAGE ✅
# -------------------------------
if st.session_state.page == "login":

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
            st.error("Invalid credentials")

# -------------------------------
# DASHBOARD ✅
# -------------------------------
elif st.session_state.page == "home":

    role = st.session_state.user

    st.title(f"Dashboard ({role})")

    cols = st.columns(4 if role != "QA_SUP" else 3)

    # Tile 1
    with cols[0]:
        st.markdown('<div class="card">📝<br>New Logbook</div>', unsafe_allow_html=True)
        if st.button("Open Entry"):
            st.session_state.page = "entry"

    # Tile 2
    with cols[1]:
        st.markdown('<div class="card">📥<br>Download</div>', unsafe_allow_html=True)
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH,"rb") as f:
                st.download_button("Download CSV", f, "logbook.csv")

    # Tile 3
    with cols[2]:
        st.markdown('<div class="card">📜<br>Records</div>', unsafe_allow_html=True)
        if st.button("Open Records"):
            st.session_state.page = "history"

    # Tile 4 (Approval)
    if role != "QA_SUP":
        with cols[3]:
            st.markdown('<div class="card">✅<br>Approvals</div>', unsafe_allow_html=True)
            if st.button("Open Approvals"):
                st.session_state.page = "approval"

# -------------------------------
# ENTRY PAGE ✅
# -------------------------------
elif st.session_state.page == "entry":

    st.header("New Logbook Entry")

    data = {}

    data["Date"] = st.date_input("Date")
    data["Batch"] = st.text_input("Batch No")
    data["Design"] = st.text_input("Design")
    data["Size"] = st.text_input("Size")

    data["Result"] = st.selectbox(
        "Result", ["Accepted","Rejected","Accepted under Deviation"]
    )

    if st.button("Save"):
        # ✅ approval flags default
        data["QA_HEAD"] = "No"
        data["QC_HEAD"] = "No"
        data["SORT_HEAD"] = "No"
        data["GM"] = "No"

        save_data(data)

        st.success("Saved ✅")
        st.session_state.page = "home"

# -------------------------------
# HISTORY PAGE ✅
# -------------------------------
elif st.session_state.page == "history":

    st.header("All Records")

    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df.insert(0, "S.No", range(1, len(df)+1))
        st.dataframe(df)

    if st.button("Back"):
        st.session_state.page = "home"

# -------------------------------
# APPROVAL PAGE ✅
# -------------------------------
elif st.session_state.page == "approval":

    st.header("Approval Records")

    role = st.session_state.user

    if not os.path.exists(CSV_PATH):
        st.warning("No records available")
        st.stop()

    df = pd.read_csv(CSV_PATH)

    # ---------------- FILTER LOGIC ----------------
    if role == "QA_HEAD":
        df = df[df["QA_HEAD"] == "No"]

    elif role == "QC_HEAD":
        df = df[(df["QA_HEAD"] == "Yes") & (df["QC_HEAD"] == "No")]

    elif role == "SORT_HEAD":
        df = df[(df["QC_HEAD"] == "Yes") & (df["SORT_HEAD"] == "No")]

    elif role == "GM":
        df = df[(df["SORT_HEAD"] == "Yes") & (df["GM"] == "No")]

    # ---------------- DISPLAY ----------------
    for i, row in df.iterrows():
        st.write(f"Batch: {row['Batch']} | Design: {row['Design']}")

        col1, col2 = st.columns(2)

        # APPROVE
        if col1.button("Approve", key=f"a{i}"):
            full_df = pd.read_csv(CSV_PATH)

            if role == "QA_HEAD":
                full_df.loc[i,"QA_HEAD"] = "Yes"
            elif role == "QC_HEAD":
                full_df.loc[i,"QC_HEAD"] = "Yes"
            elif role == "SORT_HEAD":
                full_df.loc[i,"SORT_HEAD"] = "Yes"
            elif role == "GM":
                full_df.loc[i,"GM"] = "Yes"

            full_df.to_csv(CSV_PATH, index=False)
            st.success("Approved ✅")
            st.experimental_rerun()

        # REJECT
        if col2.button("Reject", key=f"r{i}"):
            full_df = pd.read_csv(CSV_PATH)
            full_df.drop(i, inplace=True)
            full_df.to_csv(CSV_PATH, index=False)
            st.error("Rejected ❌")
            st.experimental_rerun()

    if st.button("Back"):
        st.session_state.page = "home"
