import streamlit as st
import pandas as pd
import os

# ================= CONFIG =================
st.set_page_config("QA Physical Logbook", layout="wide")
CSV_PATH = "data/QA_Logbook_Master_Template(Sheet1).csv"

# ================= USERS =================
USERS = {
    "qa_sup": "QA_SUP",
    "qa_head": "QA_HEAD",
    "qc_head": "QC_HEAD",
    "sort_head": "SORT_HEAD",
    "gm": "GM"
}
PASSWORD = "123"

# ================= STYLE =================
st.markdown("""
<style>
.stApp { background:#FFE5D4; }
.card {background:white; padding:30px; border-radius:16px; text-align:center;}
</style>
""", unsafe_allow_html=True)

# ================= SESSION =================
if "page" not in st.session_state:
    st.session_state.page="login"
if "user" not in st.session_state:
    st.session_state.user=None
if "data" not in st.session_state:
    st.session_state.data={}
if "selected_row" not in st.session_state:
    st.session_state.selected_row=None

# ================= LOGIN =================
if st.session_state.user is None:

    st.title("QA Logbook Login")
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)

    uid=st.text_input("User ID")
    pwd=st.text_input("Password", type="password")

    if st.button("Login"):
        if uid in USERS and pwd==PASSWORD:
            st.session_state.user=USERS[uid]
            st.session_state.page="home"
        else:
            st.error("Invalid")

    st.stop()

# ================= SAVE =================
def save_data(d):
    os.makedirs("data", exist_ok=True)

    df_new=pd.DataFrame([d])

    if os.path.exists(CSV_PATH):
        df_old=pd.read_csv(CSV_PATH)
        df=pd.concat([df_old, df_new], ignore_index=True)
    else:
        df=df_new

    df.to_csv(CSV_PATH,index=False)

# ================= DASHBOARD =================
if st.session_state.page=="home":

    col1,col2,col3=st.columns(3)

    with col1:
        st.markdown('<div class="card">📝 New Entry</div>', unsafe_allow_html=True)
        if st.button("Open Entry"):
            st.session_state.page="entry"

    with col2:
        st.markdown('<div class="card">📜 Records</div>', unsafe_allow_html=True)
        if st.button("View Records"):
            st.session_state.page="history"

    with col3:
        st.markdown('<div class="card">📥 Download</div>', unsafe_allow_html=True)
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH,"rb") as f:
                st.download_button("Download CSV", f, "logbook.csv")

# ================= ENTRY =================
elif st.session_state.page=="entry":

    d=st.session_state.data

    st.header("Logbook Entry")

    d["Date"]=st.date_input("Date")
    d["Batch"]=st.text_input("Batch")
    d["Design"]=st.text_input("Design")
    d["Size"]=st.text_input("Size")
    d["Surface"]=st.text_input("Surface")
    d["Matching"]=st.text_input("Matching")
    d["Production Boxes"] = st.number_input("Production Boxes", min_value=0)
    d["Checked Boxes"] = st.number_input("Checked Boxes", min_value=0)
    d["core"]=st.text_input("core")
    d["Stamping and box packing"]=st.number_input("Stamping and box packing", min_value=0)

    # -------- Measurement Table --------
   # -------- Measurement Table --------
    st.subheader("Measurement Table")

    table = st.data_editor(
        pd.DataFrame({
            "Size": ["600x600","600x1200","600x600"],
            "Diag Min": [0,0,0],
            "Diag Max": [0,0,0],
            "Gloss": ["","",""]
        }),
        num_rows="dynamic"
    )

    # ✅ STORE TABLE
    d["table_data"] = table.to_json()

    # ✅ AUTO CALC
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

        st.write("Min Size:", min_row["Size"])
        st.write("Max Size:", max_row["Size"])
        st.write("Min Diagonal:", table["Diag Min"].min())
        st.write("Max Diagonal:", table["Diag Max"].max())
        st.write(
            "Diagonal Variation:",
            table["Diag Max"].max() - table["Diag Min"].min()
        )
        
        d["SS Min"] = st.number_input("S/S Min", key="ss_min")
        d["SS Max"] = st.number_input("S/S Max", key="ss_max")

        d["CC Min"] = st.number_input("C/C Min", key="cc_min")
        d["CC Max"] = st.number_input("C/C Max", key="cc_max")


    # -------- PLANARITY ✅ BACK HERE --------
    st.subheader("Planarity Measurement")

    for tile in range(1,7):

        st.markdown(f"### Tile {tile}")

        st.image("assets/plc.png")
        for i in range(1,7):
            d[f"plc{tile}_{i}_min"] = st.number_input(f"PLC{i} Min", key=f"plc{tile}m{i}")
            d[f"plc{tile}_{i}_max"] = st.number_input(f"PLC{i} Max", key=f"plc{tile}x{i}")

        st.image("assets/pwc.png")
        for i in range(1,13):
            d[f"pwc{tile}_{i}_min"] = st.number_input(f"PWC{i} Min", key=f"pwc{tile}m{i}")
            d[f"pwc{tile}_{i}_max"] = st.number_input(f"PWC{i} Max", key=f"pwc{tile}x{i}")

        st.image("assets/diagonal.png")
        for i in range(1,4):
            d[f"d1{tile}_{i}_min"] = st.number_input(f"D1_{i} Min", key=f"d1{tile}m{i}")
            d[f"d1{tile}_{i}_max"] = st.number_input(f"D1_{i} Max", key=f"d1{tile}x{i}")

        for i in range(1,4):
            d[f"d2{tile}_{i}_min"] = st.number_input(f"D2_{i} Min", key=f"d2{tile}m{i}")
            d[f"d2{tile}_{i}_max"] = st.number_input(f"D2_{i} Max", key=f"d2{tile}x{i}")

    if st.button("Next"):
        st.session_state.page="qa"

# ================= QA =================
elif st.session_state.page=="qa":

    d=st.session_state.data

    st.header("QA Page")

    d["Randomness"]=st.selectbox("Randomness",
        ["Standard","Uniform","Slightly","Moderately","Distinctly"])
    d["Time Calibration"]=st.text_input("Calibration")
    d["Verify Time"]=st.selectbox("Verify",["OK","NOT OK"])
    d["Cleaning"]=st.text_input("Cleaning Agent")
    d["Chamfering"]=st.selectbox("Chamfering",["OK","NOT OK"])
    d["Foot"]=st.text_area("Foot Mark")
    d["Remarks"]=st.text_area("Remarks")

    if st.button("Save"):
        save_data(d)
        st.success("Saved")
        st.session_state.page="home"
        st.session_state.data={}

# ================= HISTORY =================
elif st.session_state.page=="history":

    df=pd.read_csv(CSV_PATH)

    df.insert(0,"S.No", range(1,len(df)+1))

    st.dataframe(df)

    s=st.selectbox("Select record", df["S.No"])

    if st.button("Open"):
        st.session_state.selected_row=s-1
        st.session_state.page="view"

# ================= VIEW (IMPORTANT FIX ✅) =================
elif st.session_state.page=="view":

    df = pd.read_csv(CSV_PATH)

    if st.session_state.selected_row is None:
        st.error("No record selected")
        st.stop()

    row = df.loc[st.session_state.selected_row]
# ================= BASIC DETAILS =================
st.subheader("Logbook Entry")

 st.text_input("Date", value=row.get("Date"), disabled=True)
 st.text_input("Batch", value=row.get("Batch"), disabled=True)
 st.text_input("Design", value=row.get("Design"), disabled=True)
 st.text_input("Size", value=row.get("Size"), disabled=True)
 st.text_input("Surface", value=row.get("Surface"), disabled=True)
 st.text_input("Matching", value=row.get("Matching"), disabled=True)

 st.number_input("Production Boxes", value=int(row.get("Production Boxes",0)), disabled=True)
 st.number_input("Checked Boxes", value=int(row.get("Checked Boxes",0)), disabled=True)

 st.text_input("Core", value=row.get("core"), disabled=True)
 st.number_input("Stamping and box packing", value=int(row.get("Stamping and box packing",0)), disabled=True)

# ================= MEASUREMENT TABLE =================
st.subheader("Measurement Table")

try:
    table = pd.read_json(row["table_data"])
    st.dataframe(table, use_container_width=True)
except:
    st.warning("No table data")

st.write("S/S Min:", row.get("SS Min"))
st.write("S/S Max:", row.get("SS Max"))
st.write("C/C Min:", row.get("CC Min"))
st.write("C/C Max:", row.get("CC Max"))

# ================= PLANARITY =================
st.subheader("Planarity Measurement")

for tile in range(1,7):

    st.markdown(f"### Tile {tile}")

    st.image("assets/plc.png")
    for i in range(1,7):
        st.write(
            f"PLC{i}",
            row.get(f"plc{tile}_{i}_min"),
            row.get(f"plc{tile}_{i}_max")
        )

    st.image("assets/pwc.png")
    for i in range(1,13):
        st.write(
            f"PWC{i}",
            row.get(f"pwc{tile}_{i}_min"),
            row.get(f"pwc{tile}_{i}_max")
        )

    st.image("assets/diagonal.png")
    for i in range(1,4):
        st.write(
            f"D1_{i}",
            row.get(f"d1{tile}_{i}_min"),
            row.get(f"d1{tile}_{i}_max")
        )
    for i in range(1,4):
        st.write(
            f"D2_{i}",
            row.get(f"d2{tile}_{i}_min"),
            row.get(f"d2{tile}_{i}_max")
        )

# ================= QA PAGE =================
st.subheader("QA Details")

st.text_input("Randomness", value=row.get("Randomness"), disabled=True)
st.text_input("Time Calibration", value=row.get("Time Calibration"), disabled=True)
st.text_input("Verify", value=row.get("Verify Time"), disabled=True)
st.text_input("Cleaning", value=row.get("Cleaning"), disabled=True)
st.text_input("Chamfering", value=row.get("Chamfering"), disabled=True)
st.text_area("Foot", value=row.get("Foot"), disabled=True)
st.text_area("Remarks", value=row.get("Remarks"), disabled=True)

st.divider()

# ================= APPROVAL =================
role = st.session_state.user

col1, col2 = st.columns(2)

if col1.button("✅ Approve"):
    df = pd.read_csv(CSV_PATH)
    df.loc[st.session_state.selected_row, role] = "Yes"
    df.to_csv(CSV_PATH, index=False)
    st.success("Approved ✅")

if col2.button("❌ Reject"):
    df = pd.read_csv(CSV_PATH)
    df.drop(st.session_state.selected_row, inplace=True)
    df.to_csv(CSV_PATH, index=False)
    st.error("Rejected ❌")

if st.button("⬅ Back"):
    st.session_state.page="history"
