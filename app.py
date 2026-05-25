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

# ===================================================
# SAVE FUNCTION
# ===================================================
def save_data(data):
    os.makedirs("data", exist_ok=True)

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
# PAGE 1: DASHBOARD
# ===================================================
if st.session_state.page == "home":

    col_logo, col_title = st.columns([1, 6])

    with col_logo:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=80)

    with col_title:
        st.markdown("## QA Physical Parameter Logbook")

    st.divider()

    c1, c2, c3 = st.columns(3)

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

# ===================================================
# PAGE 2: ENTRY
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
            "Size(mm)": [0,0,0],
            "Diag Min": [0,0,0],
            "Diag Max": [0,0,0],
            "Gloss": ["","",""]
        }),
        num_rows="dynamic"
    )

    if not table.empty:
        table["Diag Var"] = table["Diag Max"] - table["Diag Min"]

        st.dataframe(table)

        st.write("Min Size:", table["Size(mm)"].min())
        st.write("Max Size:", table["Size(mm)"].max())

        st.write("Min Diagonal:", table["Diag Min"].min())
        st.write("Max Diagonal:", table["Diag Max"].max())

        st.write("Diagonal Variation:",
                 table["Diag Max"].max() - table["Diag Min"].min())

    # ================= PLANARITY =================
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
# PAGE 3: QA PARAMETERS ✅ FIXED
# ===================================================
elif st.session_state.page == "qa":

    st.header("QA Parameters")

    d = st.session_state.data

    d["Randomness"] = st.selectbox(
        "Randomness",
        ["Standard","Uniform","Slightly","Moderately","Distinctly"]
    )

    d["Time Calibration"] = st.text_input("Time of Calibration")

    d["Verify Time"] = st.selectbox(
        "Verification of Time",
        ["OK","NOT OK"]
    )

    d["Marker Test"] = st.selectbox(
        "Marker Test",
        ["Normal Water","Hot Water"]
    )

    d["Cleaning Agent"] = st.text_input("Cleaning Agent")

    d["Chamfering"] = st.selectbox("Chamfering", ["OK","NOT OK"])

    d["Visual Inspection"] = st.text_area("Visual Inspection")

    d["Foot Mark"] = st.text_area("Foot Mark")

    d["Bump Standard"] = st.text_input("Bump Standard")

    if st.button("Save"):
        save_data(d)
        st.session_state.saved = True

    if st.session_state.saved:
        st.success("Saved successfully ✅")

        if st.button("Go to Dashboard"):
            st.session_state.page = "home"
            st.session_state.saved = False
            st.session_state.data = {}

# ===================================================
# PAGE 4: HISTORY
# ===================================================
elif st.session_state.page == "history":

    st.header("Previous Records")

    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        st.dataframe(df)
    else:
        st.warning("No records found")

    if st.button("Back"):
        st.session_state.page = "home"
