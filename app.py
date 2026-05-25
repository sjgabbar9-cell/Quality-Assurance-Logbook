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

# ===================================================
# SAVE
# ===================================================
def save_data(data):
    os.makedirs("data", exist_ok=True)

    df_new = pd.DataFrame([data])

    if os.path.exists(CSV_PATH):
        df_old = pd.read_csv(CSV_PATH)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_csv(CSV_PATH, index=False)

# ===================================================
# PAGE 1: DASHBOARD
# ===================================================
if st.session_state.page == "home":

    col_logo, col_title = st.columns([1,6])
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
# PAGE 2: ENTRY PART 1
# ===================================================
elif st.session_state.page == "entry":

    st.header("Logbook Entry")

    data = st.session_state.data

    data["Date"] = st.date_input("Date")
    data["Batch"] = st.text_input("Batch No")
    data["Design"] = st.text_input("Design Name")
    data["Shade"] = st.text_input("Shade No")
    data["Prod Boxes"] = st.number_input("Production Boxes")
    data["Checked Boxes"] = st.number_input("Boxes Checked")
    data["Stamping"] = st.selectbox("Stamping/Box Packing", ["OK","NOT OK"])
    data["Size"] = st.text_input("Tile Size")

    # ================= TABLE =================
    st.subheader("Measurement Table")

    table = st.data_editor(
        pd.DataFrame({
            "Size(mm)": [0,0,0,0,0],
            "Diag Min": [0,0,0,0,0],
            "Diag Max": [0,0,0,0,0],
            "Gloss": ["","","","",""]
        }),
        num_rows="dynamic"
    )

    # Auto calc
    table["Diag Var"] = table["Diag Max"] - table["Diag Min"]

    st.dataframe(table)

    if len(table)>0:
        st.write("Min Size:", table["Size(mm)"].min())
        st.write("Max Size:", table["Size(mm)"].max())

        st.write("Min Diagonal:", table["Diag Min"].min())
        st.write("Max Diagonal:", table["Diag Max"].max())

        st.write("Diagonal Variation:",
                 table["Diag Max"].max() - table["Diag Min"].min())

    # ===================================================
    # PLANARITY GRID (SIMPLIFIED)
    # ===================================================
    st.subheader("Planarity Grid")

    cols = st.columns(4)
    for i in range(4):
        with colsst.markdown('<div class="box">Grid '+str(i+1)+'</div>', unsafe_allow_html=True)
            st.number_input(f"P{i}_1", key=f"p{i}_1")
            st.number_input(f"P{i}_2", key=f"p{i}_2")

    data["SS Min"] = st.number_input("S/S Min")
    data["SS Max"] = st.number_input("S/S Max")
    data["CC Min"] = st.number_input("C/C Min")
    data["CC Max"] = st.number_input("C/C Max")

    data["Result"] = st.selectbox(
        "Final Result",
        ["Accepted","Rejected","Accepted under deviation"]
    )

    if st.button("Next"):
        st.session_state.page = "qa"

# ===================================================
# PAGE 3: QA PARAMETERS
# ===================================================
elif st.session_state.page == "qa":

    st.header("QA Parameters")

    d = st.session_state.data

    d["Randomness"] = st.selectbox(
        "Randomness", ["Standard","Uniform","Slightly","Moderately","Distinctly"]
    )
    d["Time Calibration"] = st.text_input("Time Calibration")
    d["Verify Time"] = st.selectbox("Verification", ["OK","NOT OK"])
    d["Marker"] = st.selectbox("Marker Test", ["Normal Water","Hot Water"])
    d["Cleaning"] = st.text_input("Cleaning Agent")
    d["Chamfer"] = st.selectbox("Chamfering", ["OK","NOT OK"])
    d["Inspection"] = st.text_area("Visual Inspection")
    d["Foot Mark"] = st.text_area("Foot Mark")
    d["Bump"] = st.text_input("Bump Standard")

    if st.button("SAVE"):
        save_data(d)
        st.success("Saved successfully ✅")
        st.session_state.page = "home"

# ===================================================
# PAGE: HISTORY
# ===================================================
elif st.session_state.page == "history":

    st.header("Previous Records")

    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        st.dataframe(df)
    else:
        st.warning("No records yet")

    if st.button("⬅ Back"):
        st.session_state.page = "home"
