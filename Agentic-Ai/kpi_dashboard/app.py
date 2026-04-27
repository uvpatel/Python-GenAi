import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page configuration
st.set_page_config(page_title='Student Performance KPI', layout='wide')

# Load data
df = pd.read_csv('students_marks.csv')

st.title('📊 Student Performance Dashboard')
st.markdown('### Key Performance Indicators for Students across various subjects')

# Sidebar for filtering
student_list = df['Student'].tolist()
selected_student = st.sidebar.selectbox('Select a Student', ['All'] + student_list)

# KPI Metrics
col1, col2, col3 = st.columns(3)
if selected_student == 'All':
    avg_marks = df.iloc[:, 1:].mean().mean()
    top_student = df.loc[df.iloc[:, 1:].sum(axis=1).idxmax(), 'Student']
    max_score = df.iloc[:, 1:].max().max()
else:
    student_data = df[df['Student'] == selected_student].iloc[:, 1:]
    avg_marks = student_data.values.mean()
    top_student = selected_student
    max_score = student_data.values.max()

col1.metric("Average Marks", f"{avg_marks:.2f}")
col2.metric("Top Performer", top_student)
col3.metric("Highest Score", int(max_score))

st.divider()

# Visualizations
if selected_student == 'All':
    # Subplots for all students
    st.subheader('Subject-wise Performance Comparison')
    subjects = df.columns[1:]
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, subject in enumerate(subjects):
        sns.barplot(x='Student', y=subject, data=df, ax=axes[i], palette='viridis')
        axes[i].set_title(f'{subject} Marks')
        axes[i].set_ylim(0, 100)
        axes[i].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    st.pyplot(fig)
else:
    # Visualization for selected student
    st.subheader(f'Performance Analysis for {selected_student}')
    student_row = df[df['Student'] == selected_student].melt(id_vars=['Student'], var_name='Subject', value_name='Marks')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='Subject', y='Marks', data=student_row, palette='magma', ax=ax)
    ax.set_title(f'Marks Breakdown for {selected_student}')
    ax.set_ylim(0, 100)
    for p in ax.patches:
        ax.annotate(format(p.get_height(), '.1f'), (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 9), textcoords='offset points')
    
    st.pyplot(fig)

# Data Table
st.subheader('Raw Data View')

st.dataframe(df.style.highlight_max(axis=0, subset=df.columns[1:]))