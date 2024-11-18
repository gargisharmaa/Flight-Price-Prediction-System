import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import datetime

# Load and preprocess the dataset
@st.cache_data
def load_data():
    data = pd.read_csv("goibibo_flights_data_updated.csv")
    data['price'] = pd.to_numeric(data['price'], errors='coerce')
    data.dropna(subset=['price'], inplace=True)
    return data

# Load the trained model
@st.cache_resource
def load_model():
    with open("flight_price_model.pkl", "rb") as file:
        return pickle.load(file)

# Load data and model
data = load_data()
model = load_model()

# Title
st.title("Flight Price Insights and Predictions")
st.write("Insights about flight prices and predicting flight costs based on custom inputs.")

# Sidebar for navigation
sidebar_selection = st.sidebar.radio("Select a Section", ["Insights", "Price Prediction"])

# Insights Section
if sidebar_selection == "Insights":
    st.header("Key Insights About Flight Prices")

    # **1. Airline Influence**
    st.subheader("1. Airline Influence on Prices")
    airline_prices = data.groupby('airline')['price'].mean().sort_values()
    fig1, ax1 = plt.subplots(figsize=(10, 6))  # Adjust the figure size for better readability
    sns.barplot(x=airline_prices, y=airline_prices.index, ax=ax1)
    ax1.set_title("Average Price by Airline")

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45, ha="right")  # Rotate labels and align them to the right
    st.pyplot(fig1)


    # # **2. Stops and Price**
    # st.subheader("2. Impact of Stops on Price")

    # # Calculate average prices for each stop category
    # stops_prices = data.groupby('stops')['price'].mean()

    # # Extract prices for non-stop (0 stops) and one-stop (1 stop) flights
    # if 0 in stops_prices.index and 1 in stops_prices.index:
    #     non_stop_price = stops_prices[0]
    #     one_stop_price = stops_prices[1]
        
    #     # Calculate percentage difference between non-stop and one-stop flights
    #     percentage_difference = ((non_stop_price - one_stop_price) / one_stop_price) * 100
        
    #     # Display the calculated percentage difference
    #     st.write(f"On average, non-stop flights are {percentage_difference:.2f}% more expensive than one-stop flights.")
        
    # else:
    #     st.warning("Data for non-stop or one-stop flights is missing.")

    # # Plotting the price by number of stops
    # fig2, ax2 = plt.subplots()
    # sns.barplot(x=stops_prices.index, y=stops_prices.values, ax=ax2)
    # ax2.set_title("Price by Number of Stops")
    # st.pyplot(fig2)

    # # **2. Impact of Travel Dates**
    # st.subheader("2. Price Variance by Booking Date")
    # if 'Days_To_Departure' in data.columns:
    #     fig3, ax3 = plt.subplots()
    #     sns.lineplot(data=data, x='Days_To_Departure', y='price', ax=ax3)
    #     ax3.set_title("Price Trend Based on Days to Departure")
    #     st.pyplot(fig3)
    # else:
    #     st.warning("Missing 'Days_To_Departure' column in data.")

    # **3. Class of Service**
    st.subheader("2. Class of Service and Pricing")
    class_prices = data.groupby('class')['price'].mean()
    fig4, ax4 = plt.subplots()
    sns.barplot(x=class_prices.index, y=class_prices.values, ax=ax4)
    ax4.set_title("Average Price by Class of Service")
    st.pyplot(fig4)

    # # **5. Seasonal Trends**
    # st.subheader("5. Seasonal Price Trends")
    # if 'Season' in data.columns:
    #     season_prices = data.groupby('Season')['price'].mean()
    #     fig5, ax5 = plt.subplots()
    #     sns.barplot(x=season_prices.index, y=season_prices.values, ax=ax5)
    #     ax5.set_title("Average Price by Season")
    #     st.pyplot(fig5)
    # else:
    #     st.warning("Missing 'Season' column in data.")

    # **4. Departure Time**
    st.subheader("3. Pricing based on Departure Time")
    if 'Departure_Time' in data.columns:
        dep_time_prices = data.groupby('Departure_Time')['price'].mean()
        fig6, ax6 = plt.subplots()
        sns.barplot(x=dep_time_prices.index, y=dep_time_prices.values, ax=ax6)
        ax6.set_title("Price by Departure Time")
        st.pyplot(fig6)
    else:
        st.warning("Missing 'Departure_Time' column in data.")

# Price Prediction Section
if sidebar_selection == "Price Prediction":
    st.header("Predict Flight Prices")
    st.write("Input or select flight details to predict the price.")

    # Input Features
    airline = st.selectbox("Airline", data['airline'].unique())
    flight_class = st.selectbox("Class", ["economy", "business"])
    departure_location = st.selectbox("Departure Location", data['departure_city'].unique())
    destination_location = st.selectbox("Destination Location", data['arrival_city'].unique())
    duration = st.slider("Duration (in minutes)", min_value=30, max_value=360, step=10, value=120)

    # Date input
    journey_date = st.date_input("Flight Date", value=datetime.date.today())
    #departure_time = st.time_input("Departure Time")
    #arrival_time = st.time_input("Arrival Time")

    # Extracting date and time components
    journey_day = journey_date.day
    journey_month = journey_date.month
    journey_year = journey_date.year
    #dep_hour = departure_time.hour
    #dep_min = departure_time.minute
    #arr_hour = arrival_time.hour
    #arr_min = arrival_time.minute

    # One-hot encoding
    def encode_feature(value, categories):
        return [1 if value == category else 0 for category in categories]

    input_data = np.array([ 
        duration, journey_day, journey_month, journey_year
    ] + encode_feature(airline, data['airline'].unique()) +
        encode_feature(flight_class, ["economy", "business"]) +
        encode_feature(departure_location, data['departure_city'].unique()) +
        encode_feature(destination_location, data['arrival_city'].unique())).reshape(1, -1)

    # Predict Price
    if st.button("Predict Price"):
        predicted_price = model.predict(input_data)
        st.success(f"Predicted Flight Price: ₹{np.exp(predicted_price[0]):,.2f}")
