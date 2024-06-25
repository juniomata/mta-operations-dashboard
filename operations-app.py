import streamlit as st
import pandas as pd
import altair as alt
import requests

# Streamlit page configuration
st.set_page_config(page_title="MTA Statement of Operations", layout="wide")

# Title and Description
st.title("MTA Statement of Operations Analysis")
st.write("This dashboard allows users to explore financial operation data for various MTA agencies.")

# Loading the data
data_url = "https://data.ny.gov/resource/yg77-3tkj.json?$query=SELECT%0A%20%20%60fiscal_year%60%2C%0A%20%20%60month%60%2C%0A%20%20%60scenario%60%2C%0A%20%20%60financial_plan_year%60%2C%0A%20%20%60expense_type%60%2C%0A%20%20%60agency%60%2C%0A%20%20%60type%60%2C%0A%20%20%60subtype%60%2C%0A%20%20%60general_ledger%60%2C%0A%20%20%60amount%60%0AWHERE%20%60fiscal_year%60%20%3E%3D%202023%0AORDER%20BY%20%60scenario%60%20ASC%20NULL%20LAST%2C%20%60month%60%20DESC%20NULL%20FIRST"  

response = requests.get(data_url)
operations_df = response.json()

# Read in Pandas dataframe
operations_df = pd.DataFrame.from_dict(operations_df)
operations_df['date'] = pd.to_datetime(operations_df['month'])

# Convert 'amount' column from string to numeric
operations_df['amount'] = pd.to_numeric(operations_df['amount'], errors='coerce')

col1, col2 = st.columns(2)

# Display raw data (optional)
if st.checkbox('Show raw data'):
    st.dataframe(operations_df)

with col1:
    # Filtering data based on agency selection
    agency_list = list(operations_df['agency'].unique())
    selected_agency = st.multiselect("Select an Agency", options=agency_list, default=['NYCT', 'LIRR', 'MTAHQ'])

    # Filtering data based on type
    type_list = operations_df['type'].dropna().unique()
    selected_type = st.selectbox("Select Type of Operation", options=type_list)

    # Apply filters
    filtered_data = operations_df[(operations_df['agency'].isin(selected_agency)) &
                                (operations_df['type'] == selected_type)]

with col2:
    # Date range selector
    min_date, max_date = operations_df['date'].min(), operations_df['date'].max()
    selected_date_range = st.date_input("Select Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    selected_date_range = pd.to_datetime(selected_date_range)

    # Further filter data based on selected date range
    filtered_data = filtered_data[filtered_data['date'].between(selected_date_range[0], selected_date_range[1])]

# Generate Altair chart
chart = alt.Chart(filtered_data).mark_line(point=True).encode(
    x=alt.X('date:T', title='Date'),
    y=alt.Y('sum(amount):Q', title='Amount ($)'),
    color="agency",
    tooltip=[
        alt.Tooltip('date:T', title='Date'), 
        alt.Tooltip('sum(amount):Q', title='Amount ($)'),
        alt.Tooltip('agency', title='Agency'),
        ]
).properties(
    title=f"Financial Trends for {selected_agency} - {selected_type}",
    width=800,
    height=400
)

# Display the chart
st.altair_chart(chart, use_container_width=True)

# Download button for filtered data
st.download_button("Download Filtered Data", data=filtered_data.to_csv(index=False), file_name="filtered_operations_data.csv")
print(min_date, max_date)
