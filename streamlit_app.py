import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np

# Set page config
st.set_page_config(
    page_title="JC Index Monitoring System",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .stMetric .css-1wivap2 {
        background-color: rgba(28, 131, 225, 0.1);
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stAlert {
        padding: 1rem;
        margin-top: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for data storage
if 'measurements' not in st.session_state:
    st.session_state.measurements = {}

# Calculate risk level
def calculate_risk(jc_index):
    if jc_index >= 4.0:
        return "HIGH"
    elif jc_index >= 3.5:
        return "MEDIUM"
    return "LOW"

# Save measurement
def save_measurement(data):
    if data['patient_id'] not in st.session_state.measurements:
        st.session_state.measurements[data['patient_id']] = []
    
    data['risk_level'] = calculate_risk(data['jc_index'])
    st.session_state.measurements[data['patient_id']].append(data)

# Load measurements
def load_measurements(patient_id):
    if patient_id not in st.session_state.measurements:
        return pd.DataFrame()
    
    df = pd.DataFrame(st.session_state.measurements[patient_id])
    df['scan_date'] = pd.to_datetime(df['scan_date'])
    return df.sort_values('scan_date')

# Title and patient selection
st.title("JC Index Monitoring System")

# Sidebar
with st.sidebar:
    st.header("Patient Information")
    patient_id = st.text_input("Patient ID", "Patient 001")
    st.markdown("---")
    st.markdown("""
    ### Risk Levels
    - 🟢 Low: < 3.5
    - 🟡 Medium: 3.5 - 4.0
    - 🔴 High: > 4.0
    """)

# Main layout
col1, col2, col3 = st.columns(3)

# Load patient data
df = load_measurements(patient_id)

if not df.empty:
    latest = df.iloc[-1]
    
    # Current JC Index
    with col1:
        st.metric(
            label="Current JC Index",
            value=f"{latest['jc_index']:.1f}",
            delta=f"{latest['jc_index'] - df.iloc[-2]['jc_index']:.1f}" if len(df) > 1 else None,
            delta_color="inverse"
        )

    # Lesion Count
    with col2:
        st.metric(
            label="Total Lesions",
            value=int(latest['total_lesions']),
            delta=int(latest['new_lesions'])
        )

    # Risk Level
    with col3:
        risk_color = {
            "LOW": "green",
            "MEDIUM": "yellow",
            "HIGH": "red"
        }
        st.markdown(f"""
        <div style='padding: 1rem; border-radius: 0.5rem; 
        background-color: {risk_color[latest['risk_level']]}33; 
        color: {risk_color[latest['risk_level']]}; text-align: center;'>
        <h3>Risk Level</h3>
        <h2>{latest['risk_level']}</h2>
        </div>
        """, unsafe_allow_html=True)

    # Trend Chart
    st.subheader("JC Index Trend")
    fig = px.line(
        df, 
        x='scan_date', 
        y='jc_index',
        markers=True,
        title='JC Index Over Time'
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="JC Index",
        yaxis_range=[0, 8],
        hovermode='x unified',
        showlegend=False
    )
    fig.add_hline(y=4.0, line_dash="dash", line_color="red", annotation_text="High Risk")
    fig.add_hline(y=3.5, line_dash="dash", line_color="yellow", annotation_text="Medium Risk")
    st.plotly_chart(fig, use_container_width=True)

# Data Entry Form
st.subheader("Enter New Measurement")
with st.form("measurement_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        scan_date = st.date_input(
            "Scan Date",
            datetime.now()
        )
        jc_index = st.number_input(
            "JC Index",
            min_value=0.0,
            max_value=10.0,
            step=0.1,
            format="%.1f"
        )
        
    with col2:
        total_lesions = st.number_input(
            "Total Lesions",
            min_value=0,
            step=1
        )
        new_lesions = st.number_input(
            "New Lesions",
            min_value=0,
            step=1
        )
    
    notes = st.text_area("Additional Notes")
    
    submitted = st.form_submit_button("Save Measurement")
    
    if submitted:
        if jc_index > 0 and total_lesions >= 0:
            new_data = {
                'patient_id': patient_id,
                'scan_date': scan_date,
                'jc_index': jc_index,
                'total_lesions': total_lesions,
                'new_lesions': new_lesions,
                'notes': notes
            }
            save_measurement(new_data)
            st.success("✅ Measurement saved successfully!")
            st.rerun()
        else:
            st.error("❌ Please enter valid measurements.")

# Data Management Section
st.markdown("---")
st.subheader("Data Management")
col1, col2 = st.columns(2)

with col1:
    if st.checkbox("Show raw data"):
        st.dataframe(df)

with col2:
    if not df.empty:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name=f"jc_index_data_{patient_id}.csv",
            mime="text/csv"
        )
