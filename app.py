import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Electricity Consumption Dashboard", page_icon="⚡", layout="wide")

@st.cache_data
def make_data():
    dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    homes = [("H001","Pune","2BHK"),("H002","Pune","3BHK"),
             ("H003","Mumbai","2BHK"),("H004","Nashik","1BHK")]
    appliances = {"Air Conditioner":3.2,"Refrigerator":1.2,
                  "Washing Machine":0.8,"Lighting":0.5,"Television":0.15}
    rng = np.random.default_rng(42)
    rows = []
    for date in dates:
        for hid, city, house_type in homes:
            for appliance, base in appliances.items():
                units = rng.uniform(0.1, base)
                if appliance == "Air Conditioner" and date.month not in [3,4,5,6,7,8,9]:
                    units = rng.uniform(0, 0.3)
                rate = 7.5
                rows.append([date,hid,city,house_type,appliance,
                             round(units,2),rate,round(units*rate,2)])
    return pd.DataFrame(rows, columns=[
        "Date","Household_ID","City","House_Type","Appliance",
        "Consumption_kWh","Rate_per_kWh_INR","Electricity_Bill_INR"
    ])

df = make_data()
st.title("⚡ Electricity Consumption Dashboard")
st.caption("Interactive analysis of sample household electricity usage for 2025.")
st.info("Academic demo using simulated data, not live meter readings or actual utility bills.")

st.sidebar.header("Filters")
city = st.sidebar.selectbox("City", ["All"] + sorted(df.City.unique().tolist()))
home = st.sidebar.selectbox("Household", ["All"] + sorted(df.Household_ID.unique().tolist()))
appliance = st.sidebar.selectbox("Appliance", ["All"] + sorted(df.Appliance.unique().tolist()))

data = df.copy()
if city != "All":
    data = data[data.City == city]
if home != "All":
    data = data[data.Household_ID == home]
if appliance != "All":
    data = data[data.Appliance == appliance]

if data.empty:
    st.warning("No data matches these filters.")
    st.stop()

total = data.Consumption_kWh.sum()
bill = data.Electricity_Bill_INR.sum()
days = data.Date.nunique()
avg = total / days if days else 0
homes_count = data.Household_ID.nunique()

c1,c2,c3,c4 = st.columns(4)
c1.metric("Total consumption", f"{total:,.2f} kWh")
c2.metric("Estimated bill", f"₹{bill:,.2f}")
c3.metric("Average daily usage", f"{avg:,.2f} kWh")
c4.metric("Households", str(homes_count))

data["Month"] = data.Date.dt.month_name()
data["Month_Number"] = data.Date.dt.month
monthly = data.groupby(["Month_Number","Month"], as_index=False).Consumption_kWh.sum().sort_values("Month_Number")
monthly_bill = data.groupby(["Month_Number","Month"], as_index=False).Electricity_Bill_INR.sum().sort_values("Month_Number")
by_appliance = data.groupby("Appliance", as_index=False).Consumption_kWh.sum().sort_values("Consumption_kWh", ascending=False)
by_city = data.groupby("City", as_index=False).Consumption_kWh.sum()
by_home = data.groupby("Household_ID", as_index=False).Consumption_kWh.sum()

left,right = st.columns(2)
with left:
    st.subheader("Monthly consumption")
    st.plotly_chart(px.line(monthly, x="Month", y="Consumption_kWh", markers=True), use_container_width=True)
with right:
    st.subheader("Monthly electricity bill")
    st.plotly_chart(px.bar(monthly_bill, x="Month", y="Electricity_Bill_INR"), use_container_width=True)

left,right = st.columns(2)
with left:
    st.subheader("Appliance-wise consumption")
    st.plotly_chart(px.bar(by_appliance, x="Appliance", y="Consumption_kWh", color="Appliance"), use_container_width=True)
with right:
    st.subheader("Appliance distribution")
    st.plotly_chart(px.pie(by_appliance, names="Appliance", values="Consumption_kWh"), use_container_width=True)

left,right = st.columns(2)
with left:
    st.subheader("City-wise consumption")
    st.plotly_chart(px.bar(by_city, x="City", y="Consumption_kWh", color="City"), use_container_width=True)
with right:
    st.subheader("Household-wise consumption")
    st.plotly_chart(px.bar(by_home, x="Household_ID", y="Consumption_kWh"), use_container_width=True)

st.subheader("Filtered dataset")
st.dataframe(data, use_container_width=True, hide_index=True)
st.download_button("Download filtered data (CSV)", data.to_csv(index=False).encode("utf-8"),
                   file_name="electricity_consumption_filtered.csv", mime="text/csv")

highest = monthly.loc[monthly.Consumption_kWh.idxmax()]
lowest = monthly.loc[monthly.Consumption_kWh.idxmin()]
st.subheader("Quick observations")
st.write(f"Highest consumption month: **{highest.Month}**.")
st.write(f"Lowest consumption month: **{lowest.Month}**.")
st.caption("Illustrative flat electricity rate: ₹7.50 per kWh. Replace with your actual tariff for real bill estimates.")
