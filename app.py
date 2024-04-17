import streamlit as st
import scipy.constants as constants
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, date
import requests
import streamlit as st
from dotenv import load_dotenv
import os
import streamlit as st
from streamlit_folium import st_folium
import folium
load_dotenv()

st.image('Kissan Dost Logo.png')
st.title("Kisaan Dost")

brazil = os.getenv('brazil')
iowa = os.getenv('iowa')

option = st.selectbox(
   "Which Farm Location?",
   ("Taquara Farm in Rio de Janeiro - Brazil", "Susan's Sweet Potatoes Farm - Iowa", "Custom"),
   index=None,
   placeholder="Select location...",
)

optionCrop = st.selectbox(
   "What type of crop is being produced?",
   ("Potatoes", "Corn", "Sweet Potatos", "Carrots", "Watermelon", "Custom"),
   index=None,
   placeholder="Select Crop...",
)

if (optionCrop == "Custom"):
  custom_crop = st.text_input("Crop", value="")

st.write('You selected:', option)

if (option == "Custom"):
  DEFAULT_LATITUDE = 42.35
  DEFAULT_LONGITUDE = -71.08

  m = folium.Map(location=[DEFAULT_LATITUDE, DEFAULT_LONGITUDE], zoom_start=10)

  # The code below will be responsible for displaying 
  # the popup with the latitude and longitude shown
  m.add_child(folium.LatLngPopup())

  f_map = st_folium(m, width=725)

  selected_latitude = DEFAULT_LATITUDE
  selected_longitude = DEFAULT_LONGITUDE

  if f_map.get("last_clicked"):
      selected_latitude = f_map["last_clicked"]["lat"]
      selected_longitude = f_map["last_clicked"]["lng"]
  custom_lat = st.text_input("latitude", value=0.0)
  custom_long = st.text_input("longitude", value=0.0)


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
  
  final_report_unmerged = " ".join(reports)
  final_report_weather = "The weather forecast for the next 5 days is as follows:\n\n" + final_report_unmerged + "\n\n"
  final_report_soil = "The soil conditions are as follows:\n\n" + "The upcoming week's soil conditions are expected to undergo significant changes due to varied weather patterns. With several days of rain forecasted, the soil will likely retain higher moisture levels, which can be beneficial for water-dependent crops but may pose challenges for drainage-sensitive ones. The consistent rainfall until April 20 suggests that the soil will be highly saturated, increasing the risk of soil erosion and nutrient leaching, especially on slopes and in poorly drained areas. However, the break in precipitation by April 21 and 22 could allow the top layers of soil to dry out slightly, reducing the risk of anaerobic conditions which harm root growth. This period of no rain, combined with relatively stable temperatures, may offer an ideal window for planting or applying soil amendments, as the conditions allow for easier working of the soil and better root establishment." + "\n\n"
  final_report_market_conditions = "Produce conditions are as follows:\n\n" + "Prices are experiencing moderate fluctuations due to an increased global demand for biofuels and animal feed, which corn is a primary component of. However, farmers are facing cost pressures from rising prices for fertilizers and pesticides, which are crucial for maintaining high yields. The weather has also played a critical role; recent unpredictable patterns have led to concerns about yield variability. Domestically, there's a strong competition from soybeans, with some farmers opting to switch due to better profitability and less intensive water requirements, impacting corn supply levels. Internationally, trade tensions continue to create uncertainty, influencing export markets and price stability." + "\n\n"
  final_report = final_report_weather + final_report_soil + final_report_market_conditions + "\n\n"

  return final_report

def main_custom_location(lat, lon):
  return main(f"https://api.agromonitoring.com/agro/1.0/weather/forecast?lat={lat}&lon={lon}&appid={os.getenv('api_key')}")

if st.button('Get Report'):
  if (option == "Taquara Farm in Rio de Janeiro - Brazil", "Susan's Sweet Potatoes Farm - Iowa"):
    st.write(main(brazil))
  elif (option == "Susan's Sweet Potatoes Farm - Iowa"):
    st.write(main(iowa))
  elif (option == "Custom"):
    st.write(main_custom_location(custom_lat, custom_long))