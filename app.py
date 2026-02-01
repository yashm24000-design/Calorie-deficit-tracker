import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

st.set_page_config(page_title="Weight Loss Tracker", layout="wide")

# Initialize session state to store data if not using a database yet
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['Date', 'Intake', 'Gym', 'Deficit'])

st.title("📉 Weight Loss Dashboard")

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("Log Daily Entry")
    entry_date = st.date_input("Date", date.today())
    intake = st.number_input("Calorie Intake", min_value=0, value=2000, step=50)
    gym_visit = st.checkbox("Did you go to the gym?")
    
    if st.button("Add Entry"):
        # Logic: 2700 if gym, 2500 if no gym
        tdee = 2700 if gym_visit else 2500
        daily_deficit = tdee - intake
        
        new_entry = pd.DataFrame({
            'Date': [entry_date], 
            'Intake': [intake], 
            'Gym': [gym_visit], 
            'Deficit': [daily_deficit]
        })
        st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
        st.success("Entry Saved!")

# --- DASHBOARD METRICS ---
df = st.session_state.data
if not df.empty:
    total_deficit = df['Deficit'].sum()
    # Approx 7700 kcal = 1kg weight loss
    est_weight_loss = total_deficit / 7700 
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Entries", len(df))
    col2.metric("Total Deficit", f"{total_deficit} kcal")
    col3.metric("Est. Weight Loss", f"{est_weight_loss:.2f} kg")

    # --- WATERFALL CHART ---
    fig = go.Figure(go.Waterfall(
        name="Deficit",
        orientation="v",
        measure=["relative"] * len(df),
        x=df['Date'],
        y=df['Deficit'],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#EF553B"}}, # Red for negative deficit (overeating)
        increasing={"marker": {"color": "#00CC96"}}, # Green for positive deficit
    ))

    fig.update_layout(title="Cumulative Deficit Progress", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Show Raw Data
    st.subheader("History")
    st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
else:
    st.info("Start by adding your first entry in the sidebar!")
