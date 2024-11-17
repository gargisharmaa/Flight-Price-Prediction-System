import pandas as pd
from datetime import datetime

# Load the dataset
input_file = "goibibo_flights_data.csv"  # Input CSV file
output_file = "goibibo_flights_data_updated.csv"  # Output CSV file

# Load the CSV file
try:
    data = pd.read_csv(input_file)
    print(f"Loaded {input_file} successfully!")
except FileNotFoundError:
    print(f"Error: File '{input_file}' not found!")
    exit()

# Rename columns for consistency
data.rename(columns={
    'flight date': 'departure_date',
    'from': 'departure_city',
    'to': 'arrival_city',
    'dep_time': 'departure_time'
}, inplace=True)

# 1. Ensure `price` column is numeric
if 'price' in data.columns:
    data['price'] = data['price'].replace('[^\d.]', '', regex=True).astype(float)
else:
    print("Error: 'price' column is missing from the dataset.")
    exit()

# 2. Add `Days_To_Departure` column
if 'departure_date' in data.columns:
    data['departure_date'] = pd.to_datetime(data['departure_date'], format='%d-%m-%Y', errors='coerce')
    today = datetime.now()
    data['Days_To_Departure'] = (data['departure_date'] - today).dt.days
else:
    print("Warning: 'departure_date' column is missing. Skipping 'Days_To_Departure' calculation.")

# 3. Add `Season` column
def assign_season(date):
    if pd.isna(date):
        return None
    month = date.month
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Autumn'

if 'departure_date' in data.columns:
    data['Season'] = data['departure_date'].apply(assign_season)
else:
    print("Warning: 'departure_date' column is missing. Skipping 'Season' calculation.")

# 4. Add `Departure_Time` column
def assign_time_of_day(time):
    if pd.isna(time):
        return None
    hour = time.hour
    if 5 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 17:
        return 'Afternoon'
    elif 17 <= hour < 21:
        return 'Evening'
    else:
        return 'Night'

if 'departure_time' in data.columns:
    data['departure_time'] = pd.to_datetime(data['departure_time'], format='%H:%M', errors='coerce')
    data['Departure_Time'] = data['departure_time'].apply(assign_time_of_day)
else:
    print("Warning: 'departure_time' column is missing. Skipping 'Departure_Time' calculation.")

# 5. Add `route` column
if 'departure_city' in data.columns and 'arrival_city' in data.columns:
    data['route'] = data['departure_city'] + '-' + data['arrival_city']
else:
    print("Warning: 'departure_city' or 'arrival_city' column is missing. Skipping 'route' calculation.")

# Save the updated dataset
data.to_csv(output_file, index=False)
print(f"Updated dataset saved to {output_file}.")
