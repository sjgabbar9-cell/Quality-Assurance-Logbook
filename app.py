import streamlit as st
import pandas as pd
import os

# ================= CONFIG =================
st.set_page_config("QA Physical Logbook", layout="wide")
CSV_PATH = "data/qa_logbook.csv"

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
# ================= LOGIN =================
if st.session_state.user is None:

    st.title("QA Logbook Login")

    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)

    uid = st.text_input("User ID")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if uid in USERS and pwd == PASSWORD:
            st.session_state.user = USERS[uid]
            st.session_state.page = "home"
            st.rerun()   # ✅ IMPORTANT
        else:
            st.error("Invalid")

    st.stop()

# ================= SAVE =================
def save_data(d):
    os.makedirs("data", exist_ok=True)

    df_new = pd.DataFrame([d])

    if os.path.exists(CSV_PATH):
        try:
            df_old = pd.read_csv(CSV_PATH)
            df = pd.concat([df_old, df_new], ignore_index=True)
        except:
            df = df_new
    else:
        df = df_new

    df.to_csv(CSV_PATH, index=False)

# ================= HOME =================
# ================= DASHBOARD =================
if st.session_state.page=="home":

    # ✅ LOGO ON TOP
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)

    st.markdown("## 📊 QA Logbook Dashboard")

    # ✅ TILE STYLE
    st.markdown("""
    <style>
    .tile {
        background: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        font-size: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .tile:hover {
        transform: scale(1.05);
        transition: 0.3s;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # ✅ TILE 1
    with col1:
        st.markdown('<div class="tile">📝<br><b>New Logbook</b></div>', unsafe_allow_html=True)
        if st.button("Open New Entry"):
            st.session_state.page="entry"

    # ✅ TILE 2
    with col2:
        st.markdown('<div class="tile">📜<br><b>Records</b></div>', unsafe_allow_html=True)
        if st.button("View Records"):
            st.session_state.page="history"

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
    d["Production Boxes"]=st.number_input("Production Boxes")
    d["Checked Boxes"]=st.number_input("Checked Boxes")
    d["core"]=st.text_input("core")
    d["Stamping and box packing"]=st.number_input("Stamping and box packing")
    d["Supervisor"]=st.text_input("Supervisor")
    # ✅ MEASUREMENT TABLE
    st.subheader("Measurement Table")

    table = st.data_editor(
        pd.DataFrame({
            "Size": ["600x600","600x1200","600x600"],
            "Diag Min": [0.00,0.00,0.00],
            "Diag Max": [0.00,0.00,0.00],
            "Gloss": ["","",""]
        }),
        num_rows="dynamic"
    )

    d["table_data"]=table.to_json()

    # ✅ AUTO CALC
    def size_to_area(size):
        try:
            w,h=size.split("x")
            return float(w)*float(h)
        except:
            return 0

    if not table.empty:
        table["Area"]=table["Size"].apply(size_to_area)

        min_row=table.loc[table["Area"].idxmin()]
        max_row=table.loc[table["Area"].idxmax()]

        st.write("Min Size:", min_row["Size"])
        st.write("Max Size:", max_row["Size"])
        st.write("Min Diagonal:", table["Diag Min"].min())
        st.write("Max Diagonal:", table["Diag Max"].max())
        st.write("Diagonal Variation:", table["Diag Max"].max()-table["Diag Min"].min())

    d["SS Min"]=st.number_input("SS Min")
    d["SS Max"]=st.number_input("SS Max")
    d["CC Min"]=st.number_input("CC Min")
    d["CC Max"]=st.number_input("CC Max")

    # ✅ PLANARITY
    st.subheader("Planarity Measurement")

    for tile in range(1,7):
        st.markdown(f"### Tile {tile}")

        st.image("assets/plc.png")
        for i in range(1,7):
            d[f"plc{tile}_{i}_min"]=st.number_input(f"PLC{i} Min", key=f"plc{tile}m{i}")
            d[f"plc{tile}_{i}_max"]=st.number_input(f"PLC{i} Max", key=f"plc{tile}x{i}")

        st.image("assets/pwc.png")
        for i in range(1,13):
            d[f"pwc{tile}_{i}_min"]=st.number_input(f"PWC{i} Min", key=f"pwc{tile}m{i}")
            d[f"pwc{tile}_{i}_max"]=st.number_input(f"PWC{i} Max", key=f"pwc{tile}x{i}")

        st.image("assets/diagonal.png")
        for i in range(1,4):
            d[f"d1{tile}_{i}_min"]=st.number_input(f"D1{i} Min", key=f"d1{tile}m{i}")
            d[f"d1{tile}_{i}_max"]=st.number_input(f"D1{i} Max", key=f"d1{tile}x{i}")

            d[f"d2{tile}_{i}_min"]=st.number_input(f"D2{i} Min", key=f"d2{tile}m{i}")
            d[f"d2{tile}_{i}_max"]=st.number_input(f"D2{i} Max", key=f"d2{tile}x{i}")

    if st.button("Next"):
        st.session_state.page="qa"

# ================= QA =================
elif st.session_state.page=="qa":

    d=st.session_state.data

    st.header("QA Page")

    d["Randomness"]=st.selectbox("Randomness",
        ["Standard","Uniform","Slightly","Moderately","Distinctly"])
    d["Time Calibration"]=st.text_input("Time Calibration")
    d["Verify Time"]=st.selectbox("Verify",["OK","NOT OK"])
    d["Cleaning"]=st.text_input("Cleaning")
    d["Chamfering"]=st.selectbox("Chamfering",["OK","NOT OK"])
    d["Foot"]=st.text_area("Foot")
    d["Remarks"]=st.text_area("Remarks")

    if st.button("Save"):
        save_data(d)
        st.success("Saved")
        st.session_state.page="home"
        st.session_state.data={}

# ================= HISTORY =================
elif st.session_state.page=="history":

    if not os.path.exists(CSV_PATH):
        st.warning("No records yet")
        st.stop()

    df=pd.read_csv(CSV_PATH)

    if df.empty:
        st.warning("No data")
        st.stop()

    df.insert(0,"S.No", range(1,len(df)+1))
    st.dataframe(df)

    s=st.selectbox("Select record", df["S.No"])

    if st.button("Open"):
        st.session_state.selected_row=s-1
        st.session_state.page="view"

# ================= VIEW =================
elif st.session_state.page=="view":

    df=pd.read_csv(CSV_PATH)
    row=df.loc[st.session_state.selected_row]

    st.header("Logbook Entry")

    # ✅ BASIC
    st.write("Date:",row["Date"])
    st.write("Batch:",row["Batch"])
    st.write("Design:",row["Design"])
    st.write("Size:",row["Size"])
    st.write("Surface:",row["Surface"])
    st.write("Matching:",row["Matching"])
    st.write("Supervisor:",row["Supervisor"])
    # ✅ TABLE + AUTO
    st.subheader("Measurement Table")

    try:
        table=pd.read_json(row["table_data"])
        st.dataframe(table)

        def size_to_area(size):
            w,h=size.split("x")
            return float(w)*float(h)

        table["Area"]=table["Size"].apply(size_to_area)

        min_row=table.loc[table["Area"].idxmin()]
        max_row=table.loc[table["Area"].idxmax()]

        st.write("Min Size:",min_row["Size"])
        st.write("Max Size:",max_row["Size"])

        st.write("Min Diagonal:",table["Diag Min"].min())
        st.write("Max Diagonal:",table["Diag Max"].max())
        st.write("Diagonal Variation:",table["Diag Max"].max()-table["Diag Min"].min())

    except:
        pass

    st.write("SS Min:",row.get("SS Min"))
    st.write("SS Max:",row.get("SS Max"))
    st.write("CC Min:",row.get("CC Min"))
    st.write("CC Max:",row.get("CC Max"))

    # ✅ FULL PLANARITY
    st.subheader("Planarity Measurement")

    for tile in range(1,7):
        st.markdown(f"### Tile {tile}")

        st.image("assets/plc.png")
        for i in range(1,7):
            st.write("PLC",row.get(f"plc{tile}_{i}_min"),row.get(f"plc{tile}_{i}_max"))

        st.image("assets/pwc.png")
        for i in range(1,13):
            st.write("PWC",row.get(f"pwc{tile}_{i}_min"),row.get(f"pwc{tile}_{i}_max"))

        st.image("assets/diagonal.png")
        for i in range(1,4):
            st.write("D1",row.get(f"d1{tile}_{i}_min"),row.get(f"d1{tile}_{i}_max"))
            st.write("D2",row.get(f"d2{tile}_{i}_min"),row.get(f"d2{tile}_{i}_max"))

    # ✅ QA DETAILS
    st.subheader("QA Details")

    st.write("Randomness:",row["Randomness"])
    st.write("Time Calibration:",row["Time Calibration"])
    st.write("Verify:",row["Verify Time"])
    st.write("Cleaning:",row["Cleaning"])
    st.write("Chamfering:",row["Chamfering"])
    st.write("Foot:",row["Foot"])
    st.write("Remarks:",row["Remarks"])

    # ✅ HIERARCHY
    role=st.session_state.user

    qa=row.get("QA_HEAD","No")
    qc=row.get("QC_HEAD","No")
    sort=row.get("SORT_HEAD","No")
    gm=row.get("GM","No")

    allow=False

    if role=="QA_HEAD":
        allow=True
    elif role=="QC_HEAD" and qa=="Yes":
        allow=True
    elif role=="SORT_HEAD" and qc=="Yes":
        allow=True
    elif role=="GM" and sort=="Yes":
        allow=True

    if role not in df.columns:
        df[role]="No"

    st.divider()

    col1,col2=st.columns(2)

    if col1.button("Approve"):
        if allow:
            df.loc[st.session_state.selected_row,role]="Yes"
            df.to_csv(CSV_PATH,index=False)
            st.success("Approved")
            st.session_state.page="history"
            st.rerun()
        else:
            st.error("Follow approval hierarchy")

    if col2.button("Reject"):
        df.drop(st.session_state.selected_row,inplace=True)
        df.reset_index(drop=True,inplace=True)
        df.to_csv(CSV_PATH,index=False)
        st.error("Rejected")
        st.session_state.page="history"
        st.rerun()

    if st.button("Back"):
        st.session_state.page="history"
