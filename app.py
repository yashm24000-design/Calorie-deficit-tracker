import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

st.set_page_config(page_title="Weight Tracker Pro", layout="wide")

# Initialize data in session state
if 'df' not in st.session_state:
    # Creating a sample starting row based on your current progress
    st.session_state.df = pd.DataFrame(columns=['Date', 'Intake', 'Gym', 'Deficit'])

st.title("📉 Weight Loss Dashboard")

# --- SIDEBAR: ADD NEW ENTRY ---
with st.sidebar:
    st.header("Log Daily Entry")
    with st.form("entry_form", clear_on_submit=True):
        entry_date = st.date_input("Date", date.today())
        intake = st.number_input("Calorie Intake (kcal)", min_value=0, value=2000)
        gym_visit = st.checkbox("Gym Session?")
        submit = st.form_submit_button("Add Entry")
        
        if submit:
            tdee = 2700 if gym_visit else 2500
            new_row = pd.DataFrame([{
                'Date': entry_date, 
                'Intake': intake, 
                'Gym': gym_visit, 
                'Deficit': tdee - intake
            }])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.rerun()

# --- MAIN DISPAY ---
df = st.session_state.df

if not df.empty:
    # 1. METRICS
    total_deficit = df['Deficit'].sum()
    col1, col2 = st.columns(2)
    col1.metric("Total Cumulative Deficit", f"{total_deficit} kcal")
    col2.metric("Est. Weight Loss", f"{total_deficit / 7700:.2f} kg")

    # 2. WATERFALL CHART
    fig = go.Figure(go.Waterfall(
        name="Deficit", orientation="v",
        measure=["relative"] * len(df),
        x=df.index, # Using index so dates can repeat if needed
        y=df['Deficit'],
        decreasing={"marker": {"color": "#EF553B"}},
        increasing={"marker": {"color": "#00CC96"}},
    ))
    fig.update_layout(title="Progress Waterfall", xaxis_title="Entry Number")
    st.plotly_chart(fig, use_container_width=True)

    # 3. EDIT & DELETE SECTION
    st.subheader("Edit or Delete Entries")
    st.write("Double-click any cell to edit. The 'Deficit' will auto-recalculate.")
    
    # Data Editor - this allows direct editing
    edited_df = st.data_editor(
        df, 
        num_rows="dynamic", # Allows you to delete rows by selecting them
        use_container_width=True,
        key="data_editor"
    )

    # Recalculate deficit if intake or gym status changed in the editor
    if not edited_df.equals(df):
        edited_df['Deficit'] = edited_df.apply(
            lambda x: (2700 if x['Gym'] else 2500) - x['Intake'], axis=1
        )
        st.session_state.df = edited_df
        st.rerun()
else:
    st.info("No data yet. Use the sidebar to log your first meal!")
