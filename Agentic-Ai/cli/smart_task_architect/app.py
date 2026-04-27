import streamlit as st
from logic import TaskManager
import pandas as pd

# Page Config
st.set_page_config(
    page_title="Smart Task Architect",
    page_icon="🏗️",
    layout="wide"
)

# Initialize Logic
manager = TaskManager()

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# Header Section
st.title("🏗️ Smart Task Architect")
st.caption("Production-grade task orchestration dashboard")

# Metrics Row
tasks_df = manager.get_tasks()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Tasks", len(tasks_df))
with col2:
    st.metric("High Priority", len(tasks_df[tasks_df['Priority'] == 'High']))
with col3:
    st.metric("Completion Status", "0%" if tasks_df.empty else f"{int((len(tasks_df[tasks_df['Status'] == 'Done'])/len(tasks_df))*100)}%")

st.divider()

# Layout: Sidebar for Input, Main for List
with st.sidebar:
    st.header("🛠️ Task Engineering")
    with st.form("task_form", clear_on_submit=True):
        task_desc = st.text_input("Objective Description")
        priority = st.select_slider("Priority Level", options=["Low", "Medium", "High"])
        submitted = st.form_submit_button("Deploy Task")
        
        if submitted:
            if task_desc:
                manager.add_task(task_desc, priority)
                st.success("Task deployed successfully!")
                st.rerun()
            else:
                st.error("Objective cannot be empty.")

    st.markdown("--- ")
    st.subheader("Dangerous Zone")
    if st.button("Purge Data", type="primary"):
        manager.tasks_df = manager._get_empty_df()
        manager.save_tasks()
        st.rerun()

# Main Dashboard
st.subheader("📋 Active Workload")
if not tasks_df.empty:
    # Display Task Table
    edited_df = st.data_editor(
        tasks_df, 
        hide_index=True, 
        use_container_width=True,
        disabled=["ID"]
    )
    
    # Task Management Actions
    st.subheader("🔧 Operations")
    del_col1, del_col2 = st.columns([1, 4])
    with del_col1:
        task_to_delete = st.number_input("Enter Task ID to Delete", min_value=1, step=1)
    with del_col2:
        st.write(" ") # Spacer
        st.write(" ")
        if st.button("Decommission Task"):
            manager.delete_task(task_to_delete)
            st.rerun()
else:
    st.info("System standby. No active tasks detected in the architect layer.")"