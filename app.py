import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Connect to SQLite database
def get_data_from_db(province):
    conn = sqlite3.connect('population_data.db')
    cursor = conn.cursor()

    # Fetch population data for a specific province
    cursor.execute('''
    SELECT indicator, value, percentage FROM Population WHERE province = ?
    ''', (province,))
    population_data = cursor.fetchall()

    # Fetch administrative units data for the specific province
    cursor.execute('''
    SELECT division, population, percentage FROM AdministrativeUnits WHERE province = ?
    ''', (province,))
    admin_units_data = cursor.fetchall()

    # Fetch housing data for the specific province
    cursor.execute('''
    SELECT category, units, percentage FROM Housing WHERE province = ?
    ''', (province,))
    housing_data = cursor.fetchall()

    conn.close()

    # Convert fetched data to DataFrame
    population_df = pd.DataFrame(population_data, columns=["Indicator", "Value", "Percentage"])
    admin_units_df = pd.DataFrame(admin_units_data, columns=["Division", "Population", "Percentage"])
    housing_df = pd.DataFrame(housing_data, columns=["Category", "Units", "Percentage"])

    return population_df, admin_units_df, housing_df

# Function to plot comparison graphs using Plotly
def plot_comparison(df1, df2, column_name, title):
    # Print columns to debug and check for discrepancies
    df1['Province'] = "Province 1"
    df2['Province'] = "Province 2"
    
    # Check columns to ensure we're selecting the right ones
    print("Columns in df1:", df1.columns)
    print("Columns in df2:", df2.columns)

    # Handle missing columns and select based on the available column names
    if 'Category' in df1.columns and 'Category' in df2.columns:
        combined_df = pd.concat([df1[['Province', 'Category', column_name]], df2[['Province', 'Category', column_name]]])
        x_axis = 'Category'
    elif 'Indicator' in df1.columns and 'Indicator' in df2.columns:
        combined_df = pd.concat([df1[['Province', 'Indicator', column_name]], df2[['Province', 'Indicator', column_name]]])
        x_axis = 'Indicator'
    else:
        st.error("Both DataFrames must have either 'Category' or 'Indicator' columns.")
        return

    # Create the bar plot using Plotly
    fig = px.bar(
        combined_df,
        x=x_axis, 
        y=column_name,
        color="Province",
        barmode='group',
        labels={'x': x_axis, 'y': column_name},
        title=title
    )
    st.plotly_chart(fig)

# Function to display provincial data as graphs or tables
def display_provincial_data(province):
    population_df, _, housing_df = get_data_from_db(province)

    st.subheader(f"{province} Population Data")
    st.write(population_df)

    st.subheader(f"{province} Housing Data")
    st.write(housing_df)

    # Plot Population and Housing data for the selected province
    st.subheader(f"{province} Population Graph")
    fig = px.bar(population_df, x="Indicator", y="Value", title=f"Population Data for {province}")
    st.plotly_chart(fig)

    st.subheader(f"{province} Housing Graph")
    fig = px.bar(housing_df, x="Category", y="Units", title=f"Housing Data for {province}")
    st.plotly_chart(fig)

# Streamlit app layout
st.title("Province Data Viewer - 2017")
st.sidebar.header("Select Mode")

# Mode Selector: Display Mode or Comparison Mode
mode = st.sidebar.radio("Select Mode", ["Display Mode", "Comparison Mode"])

# Dropdown menu for selecting provinces
province_list = ["Punjab", "Sindh", "KPK", "FATA", "Balochistan"]  # Add more provinces as needed
province1 = st.sidebar.selectbox("Select Province", province_list)

if mode == "Display Mode":
    # Display data for only one province in graphs and tables
    display_provincial_data(province1)

elif mode == "Comparison Mode":
    # Dropdown for selecting the second province for comparison
    province2 = st.sidebar.selectbox("Select Province for Comparison", province_list)

    # Load data for comparison (no administrative units)
    population_df1, _, housing_df1 = get_data_from_db(province1)
    population_df2, _, housing_df2 = get_data_from_db(province2)

    # Allow user to select which data to compare
    comparison_type = st.selectbox("Select comparison type", ["Population", "Housing"])

    # Compare Population Data
    if comparison_type == "Population":
        st.subheader(f"Population Comparison between {province1} and {province2}")
        plot_comparison(population_df1, population_df2, "Value", "Total Population Comparison")

    # Compare Housing Data
    elif comparison_type == "Housing":
        st.subheader(f"Housing Units Comparison between {province1} and {province2}")
        plot_comparison(housing_df1, housing_df2, "Units", "Housing Units Comparison")
