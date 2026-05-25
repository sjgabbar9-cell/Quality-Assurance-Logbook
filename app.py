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

    col_logo, col_title = st.columns([1, 6])

    with col_logo:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=80)

    with col_title:
        st.markdown("## QA Physical Parameter Logbook")

    st.divider()

    if role == "QA_SUP":
        c1, c2, c3 = st.columns(3)
    else:
        c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown('<div class="card">📝<br><h3>New Logbook</h3></div>', unsafe_allow_html=True)
        if st.button("Open", key="new"):
            st.session_state.page = "entry"

    with c2:
        st.markdown('<div class="card">📥<br><h3>Download</h3></div>', unsafe_allow_html=True)
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH,"rb") as f:
                st.download_button("Download CSV", f, "qa_logbook.csv")

    with c3:
        st.markdown('<div class="card">📜<br><h3>Previous Records</h3></div>', unsafe_allow_html=True)
        if st.button("View Records"):
            st.session_state.page = "history"

    if role != "QA_SUP":
        with c4:
            st.markdown('<div class="card">✅<br><h3>Approval Records</h3></div>', unsafe_allow_html=True)
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

    # ===================================================
    # ✅ UPDATED MEASUREMENT TABLE
    # ===================================================
    st.subheader("Measurement Table")

    table = st.data_editor(
        pd.DataFrame({
            "Size(mm)": ["", "", ""],
            "Diag Min": [0.0, 0.0, 0.0],
            "Diag Max": [0.0, 0.0, 0.0],
            "Gloss": ["","",""]
        }),
        num_rows="dynamic"
    )

    # ---- SIZE PARSER ----
    def parse_size(x):
        try:
            x = str(x).lower().replace("x","*")
            a, b = x.split("*")
            return float(a)*float(b)
        except:
            return None

    if not table.empty:

        table["Diag Var"] = table["Diag Max"] - table["Diag Min"]
        st.dataframe(table)

        # SIZE CALC
        sizes = table["Size(mm)"].apply(parse_size).dropna()

        if not sizes.empty:
            st.write("✅ Min Size :", sizes.min())
            st.write("✅ Max Size :", sizes.max())
        else:
            st.warning("Enter Size like 600*1200")

        # DIAGONAL CALC
        min_diag = table["Diag Min"].min()
        max_diag = table["Diag Max"].max()

        st.write("✅ Min Diagonal:", min_diag)
        st.write("✅ Max Diagonal:", max_diag)
        st.write("✅ Diagonal Variation:", max_diag - min_diag)

    # ===================================================
    # ✅ STANDARD PLANARITY (ADDED BACK)
    # ===================================================
    st.subheader("Standard Planarity")

    col1, col2 = st.columns(2)
    with col1:
        cc_neg = st.number_input("C/C -ve value")
    with col2:
        cc_pos = st.number_input("C/C +ve value")

    col3, col4 = st.columns(2)
    with col3:
        ss_neg = st.number_input("S/S -ve value")
    with col4:
        ss_pos = st.number_input("S/S +ve value")

    # ===================================================
    # PLANARITY GRID (UNCHANGED)
    # ===================================================
    st.subheader("Planarity Grid")

    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            st.markdown(f'<div class="box">Grid {i+1}</div>', unsafe_allow_html=True)
            st.number_input("Point 1", key=f"p{i}_1")
            st.number_input("Point 2", key=f"p{i}_2")

    d["SS Min"] = st.number_input("S/S Min")
    d["SS Max"] = st.number_input("S/S Max")
    d["CC Min"] = st.number_input("C/C Min")
    d["CC Max"] = st.number_input("C/C Max")

    d["Result"] = st.selectbox(
        "Final Result",
        ["Accepted","Rejected","Accepted under deviation"]
    )

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
    d["Verify Time"] = st.selectbox("Verification of Time", ["OK","NOT OK"])
    d["Marker Test"] = st.selectbox("Marker Test", ["Normal Water","Hot Water"])
    d["Cleaning Agent"] = st.text_input("Cleaning Agent")
    d["Chamfering"] = st.selectbox("Chamfering", ["OK","NOT OK"])
    d["Visual Inspection"] = st.text_area("Visual Inspection")
    d["Foot Mark"] = st.text_area("Foot Mark")
    d["Bump Standard"] = st.text_input("Bump Standard")

    if st.button("Save"):
        save_data(d)
        st.success("Saved ✅")

# ===================================================
# HISTORY
# ===================================================
elif st.session_state.page == "history":

    st.header("Previous Records")

    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df.insert(0, "S.No", range(1, len(df)+1))
        st.dataframe(df)

    if st.button("Back"):
        st.session_state.page = "home"

# ===================================================
# APPROVAL
# ===================================================
elif st.session_state.page == "approval":

    st.header("Approval Records")

    role = st.session_state.user

    if not os.path.exists(CSV_PATH):
        st.warning("No records")
        st.stop()

    df = pd.read_csv(CSV_PATH)

    if role == "QA_HEAD":
        df = df[df["QA_HEAD"] == "No"]
    elif role == "QC_HEAD":
        df = df[(df["QA_HEAD"] == "Yes") & (df["QC_HEAD"] == "No")]
    elif role == "SORT_HEAD":
        df = df[(df["QC_HEAD"] == "Yes") & (df["SORT_HEAD"] == "No")]
    elif role == "GM":
        df = df[(df["SORT_HEAD"] == "Yes") & (df["GM"] == "No")]

    for i, row in df.iterrows():

        st.write(f"Batch: {row['Batch']} | Design: {row['Design']}")

        c1, c2 = st.columns(2)

        if c1.button("Approve", key=f"a{i}"):

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
            st.experimental_rerun()

        if c2.button("Reject", key=f"r{i}"):

            full_df = pd.read_csv(CSV_PATH)
            full_df.drop(i, inplace=True)
            full_df.to_csv(CSV_PATH, index=False)
            st.experimental_rerun()

    if st.button("Back"):
        st.session_state.page = "home"
