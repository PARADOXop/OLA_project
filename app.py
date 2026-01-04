import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Ride Analytics Dashboard",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
df = pd.read_csv("./dataset/OLA_clean.csv")

df['Date'] = pd.to_datetime(df['Date'])
df['Hour'] = pd.to_datetime(df['Time']).dt.hour
df['ride_status'] = df['ride_status'].str.lower()

# ---------------- FILTERS (TOP RIGHT, BIG) ----------------
st.markdown("## 🔍 Filters")

f1, f2, f3, f4 = st.columns([3, 3, 2, 2])

with f1:
    vehicle_filter = st.multiselect(
        "Vehicle Type",
        df['Vehicle_Type'].unique(),
        default=df['Vehicle_Type'].unique()
    )

with f2:
    status_filter = st.multiselect(
        "Ride Status",
        df['ride_status'].unique(),
        default=df['ride_status'].unique()
    )

with f3:
    start_date = st.date_input("Start Date", df['Date'].min())

with f4:
    end_date = st.date_input("End Date", df['Date'].max())

# Convert dates properly (FIXES YOUR ERROR)
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

filtered_df = df[
    (df['Vehicle_Type'].isin(vehicle_filter)) &
    (df['ride_status'].isin(status_filter)) &
    (df['Date'] >= start_date) &
    (df['Date'] <= end_date)
]

st.divider()

# ---------------- KPIs ----------------
total = len(filtered_df)
completed = (filtered_df['ride_status'] == 'complete').sum()
incomplete = (filtered_df['ride_status'] == 'incomplete').sum()
rate = round((incomplete / total) * 100, 2) if total else 0
revenue = filtered_df['Booking_Value'].sum()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Bookings", total)
k2.metric("Completed", completed)
k3.metric("Incomplete", incomplete)
k4.metric("Incomplete Rate (%)", rate)
k5.metric("Total Revenue(in Millions)", int(revenue)/1000000)

st.divider()

# ---------------- ROW 1 ----------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Ride Status Distribution")
    fig = px.pie(
        filtered_df,
        names='ride_status',
        height=1000
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Bookings by Hour")
    hourly = filtered_df.groupby('Hour').size().reset_index(name='Bookings')
    fig = px.bar(
        hourly,
        x='Hour',
        y='Bookings',
        height=1000
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- ROW 2 ----------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Avg Booking Value by Distance")
    dist = filtered_df.groupby('distance_cat')['Booking_Value'].mean().reset_index()
    fig = px.bar(
        dist,
        x='distance_cat',
        y='Booking_Value',
        height=1000
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Avg Booking Value by Vehicle")
    veh = filtered_df.groupby('Vehicle_Type')['Booking_Value'].mean().reset_index()
    fig = px.bar(
        veh,
        x='Vehicle_Type',
        y='Booking_Value',
        height=1000
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- ROW 3 ----------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Vehicle TAT Distribution")
    fig = px.histogram(
        filtered_df,
        x='V_TAT',
        nbins=25,
        height=1000
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Customer TAT Distribution")
    fig = px.histogram(
        filtered_df,
        x='C_TAT',
        nbins=25,
        height=1000
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- ROW 4 ----------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Driver Ratings")
    fig = px.histogram(
        filtered_df,
        x='Driver_Ratings',
        nbins=10,
        height=1000
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Customer Ratings")
    fig = px.histogram(
        filtered_df,
        x='Customer_Rating',
        nbins=10,
        height=1000
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- FINAL ----------------
st.subheader("Incomplete Ride Reasons")

inc_df = filtered_df[filtered_df['ride_status'] == 'incomplete']
reason_counts = inc_df['cancellation_reason'].value_counts().reset_index()
reason_counts.columns = ['Reason', 'Count']

if not reason_counts.empty:
    fig = px.bar(
        reason_counts,
        x='Reason',
        y='Count',
        height=1000
    )
    st.plotly_chart(fig, use_container_width=True)

lost_rev = inc_df['Booking_Value'].sum()
st.metric("Estimated Revenue Lost(in Million)", int(lost_rev) / 1000000)
