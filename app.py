import sqlite3
import streamlit as st
from PIL import Image
from ultralytics import YOLO
import plotly.express as px

st.set_page_config(page_title="Hardware QC & Diagnostics Hub", layout="wide")

def query_error_db(search_term, selected_board):
    conn = sqlite3.connect("hardware_errors.db")
    cursor = conn.cursor()
    
    query = "SELECT board, error_code, error_message, meaning, possible_reasons, alternatives FROM error_logs WHERE 1=1"
    params = []
    
    if selected_board != "All Boards":
        query += " AND board = ?"
        params.append(selected_board)
        
    if search_term:
        query += " AND (error_code LIKE ? OR error_message LIKE ? OR meaning LIKE ?)"
        term = f"%{search_term}%"
        params.extend([term, term, term])
        
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

if "history" not in st.session_state:
    st.session_state.history = []
if "current_image" not in st.session_state:
    st.session_state.current_image = None
if "current_results" not in st.session_state:
    st.session_state.current_results = None
if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = None

st.sidebar.title("QC & Diagnostic Hub")
page = st.sidebar.radio("Navigation", [
    " Visual PCB Inspection", 
    " System Error Diagnostics", 
    " Batch Analytics"
])

@st.cache_resource
def load_model():
    return YOLO("best.pt")

model = load_model()

# --- MODULE 1: VISUAL INSPECTION ---
if page == " Visual PCB Inspection":
    st.title("AI Visual PCB Defect Inspection")
    st.markdown("Automated surface defect detection using fine-tuned computer vision.")
    
    conf_thresh = st.sidebar.slider("Detection Confidence Threshold", 0.01, 0.50, 0.05, 0.01)
    uploaded_file = st.file_uploader("Upload PCB Board Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        if st.session_state.last_uploaded_name != uploaded_file.name:
            st.session_state.current_image = Image.open(uploaded_file)
            st.session_state.last_uploaded_name = uploaded_file.name
            st.session_state.current_results = None

    if st.session_state.current_image is not None:
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Original Image")
            st.image(st.session_state.current_image, use_container_width=True)
            
        if st.button("Detect Defects") or st.session_state.current_results is not None:
            if st.session_state.current_results is None:
                results = model(st.session_state.current_image, conf=conf_thresh)
                st.session_state.current_results = results[0]
                
                boxes = results[0].boxes
                detected_classes = [model.names[int(box.cls[0])] for box in boxes]
                
                st.session_state.history.append({
                    "file_name": st.session_state.last_uploaded_name,
                    "count": len(boxes),
                    "defects": detected_classes
                })
            
            res = st.session_state.current_results
            res_plotted = res.plot()
            
            with c2:
                st.subheader("Inspection Result")
                st.image(res_plotted, caption="Visual Defect Analysis", use_container_width=True)
                
            boxes = res.boxes
            st.subheader("Defect Summary Report")
            if len(boxes) > 0:
                st.error(f"Detected {len(boxes)} defect(s) on board.")
                for box in boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    st.write(f"- **Defect Class:** {model.names[cls_id]} | **Confidence:** {conf:.2%}")
            else:
                st.success("No visual defects detected on this board.")

# --- MODULE 2: SYSTEM ERROR DIAGNOSTICS ---
elif page == " System Error Diagnostics":
    st.title(" Hardware & Board Log Diagnostics Engine")
    st.markdown("Search terminal logs, error codes, or kernel dumps for instant root-cause analysis.")
    
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        board_filter = st.selectbox("Target Board Architecture", [
            "All Boards", 
            "NVIDIA Jetson Nano", 
            "Raspberry Pi / Embedded Board", 
            "Generic PCB / Microcontroller", 
            "ESP32 / Embedded Wireless"
        ])
    
    with col_b:
        search_query = st.text_input("Enter Error Message or Code (e.g., 'OUT_OF_MEMORY', 'under-voltage')", "")
        
    st.divider()
    
    matched_errors = query_error_db(search_query, board_filter)
    
    if matched_errors:
        st.subheader(f"Found {len(matched_errors)} Diagnostic Match(es):")
        for err in matched_errors:
            board, code, msg, meaning, reasons, fixes = err
            
            with st.expander(f"🔴 [{board}] {code if code else 'Error'} - {msg[:60]}...", expanded=True):
                st.markdown(f"**Target Architecture:** `{board}`")
                st.markdown(f"**Error Code:** `{code}`")
                st.markdown(f"**Raw Message:** `{msg}`")
                st.markdown("---")
                
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.info("💡 **Meaning of Error**")
                    st.write(meaning)
                with col_m2:
                    st.warning("⚠️ **Possible Root Causes**")
                    st.write(reasons)
                with col_m3:
                    st.success("🛠️ **Fixes & Alternatives**")
                    st.write(fixes)
    else:
        st.error("No matching records found. Try broader terms like 'memory', 'power', or 'voltage'.")

# --- MODULE 3: BATCH ANALYTICS ---
elif page == " Batch Analytics":
    st.title("Quality Control Analytics Dashboard")
    st.markdown("Real-time yield ratios and defect class breakdown.")
    
    if len(st.session_state.history) == 0:
        st.info("No inspection data logged yet. Run detections in **Visual PCB Inspection** first!")
    else:
        total_boards = len(st.session_state.history)
        defective_boards = sum(1 for item in st.session_state.history if item["count"] > 0)
        passed_boards = total_boards - defective_boards
        total_defects = sum(item["count"] for item in st.session_state.history)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Boards Analyzed", total_boards)
        m2.metric("Passed Boards", passed_boards)
        m3.metric("Defective Boards", defective_boards)
        m4.metric("Total Defects Found", total_defects)
        
        st.divider()
        
        all_defects = []
        for item in st.session_state.history:
            all_defects.extend(item["defects"])
            
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Pass vs. Defective Yield Ratio")
            yield_data = {"Status": ["Pass", "Defective"], "Count": [passed_boards, defective_boards]}
            fig1 = px.pie(yield_data, values="Count", names="Status", color="Status",
                          color_discrete_map={"Pass": "#00CC96", "Defective": "#EF553B"},
                          title="Board Quality Ratio")
            st.plotly_chart(fig1, use_container_width=True)
            
        with col2:
            st.subheader("Defect Class Frequency")
            if all_defects:
                fig2 = px.histogram(x=all_defects, title="Defect Frequencies",
                                    labels={'x': 'Defect Type', 'y': 'Occurrences'},
                                    color_discrete_sequence=['#636EFA'])
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.success("All analyzed boards have been defect-free so far!")