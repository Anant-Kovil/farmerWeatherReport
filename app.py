import streamlit as st
import scipy.constants as constants
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, date
import requests
import streamlit as st
from dotenv import load_dotenv
import os
load_dotenv()

brazil = os.getenv('brazil')
iowa = os.getenv('iowa')

option = st.selectbox(
   "Which Farm Location?",
   ("Brazil", "Iowa"),
   index=None,
   placeholder="Select location...",
)

st.write('You selected:', option)

def main(api_url):
  response = requests.get(api_url)
  weather_anticipate = response.json()
  df = pd.DataFrame(weather_anticipate)
  df['date'] = pd.to_datetime(df['dt'], unit='s')
  df['rain'].fillna(0, inplace=True)
  df['rain'] = df['rain'].apply(lambda x: x['3h'] if isinstance(x, dict) else x)
  df['clouds'] = df['clouds'].apply(lambda x: x['all'] if isinstance(x, dict) else x)
  df = df.join(df['main'].apply(pd.Series))
  df["temp"] = constants.convert_temperature(df['temp'], 'Kelvin', 'Fahrenheit')
  df = df.drop(columns=["dt", "weather", "wind", "clouds", "main", "feels_like", "temp_min","temp_max", "pressure", "sea_level", "grnd_level", "temp_kf"])
  # Convert 'date' to datetime and extract the date component
  df['date'] = pd.to_datetime(df['date']).dt.date
  # Group by the extracted date and aggregate
  daily_data = df.groupby('date').agg({
      'rain': lambda x: 1 if any(x > 0) else 0,
      'temp': 'mean',
      'humidity': 'mean'
  }).reset_index()
  # Rename the columns appropriately
  daily_data.columns = ['Date', 'Rain', 'Average Temperature', 'Average Humidity']
  reports = []
  for index, row in daily_data.iterrows():
      date = row['Date']
      rain = "rain is expected" if row['Rain'] == 1 else "no rain is expected"
      avg_temp = row['Average Temperature']
      avg_humidity = row['Average Humidity']

      report = (f"On {date}, {rain}. The average temperature is expected to be {avg_temp:.2f}°F with an average "
                f"humidity of {avg_humidity:.2f}%.")
      reports.append(report)
  
  final_report = " ".join(reports)
  return final_report

if st.button('Get Weather Report'):
  if (option == "Brazil"):
    st.write(main(brazil))
  elif (option == "Iowa"):
    st.write(main(iowa))
