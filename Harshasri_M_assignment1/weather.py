import streamlit as st
import requests
import os
from dotenv import load_dotenv

#load environmental variables
load_dotenv()
#Functiion to get weather data
def get_weather(city,api_key):
    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct"
        geo_params = {"q":city,'limit':1,'appid':api_key}

        #Get city coordinates
        geo_response = requests.get(geo_url,params=geo_params)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

       # print(geo_data)


        if not geo_data:
            return None,"City not found"
        lat,long = geo_data[0]["lat"],geo_data[0]["lon"]

        #Weather api url
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        weather_params = {"lat":lat,"lon":long,"appid":api_key,"units":"metric"}

        #Get weather data
        weather_response = requests.get(weather_url,weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        #print(weather_data)

        return weather_data,None
    except requests.exceptions.RequestException as e:
        return None,str(e)
#streamlitapp
def main():
    st.title("Weather App⛅☀️🔆 ")
    st.write("Get real time weather information for any city")

    #Input for city
    city = st.text_input("Enter the city name  ",placeholder="eg : london")

    #Open Weather api Key
    api_key = os.getenv("API_KEY")#Load api key from .env file
    #When the button is clicked
    if (st.button("Get Weather")):
        if(city):
            weather_data,error = get_weather(city,api_key)
            if(error):
                st.error(f"Error:{error}")
            else:
                #display Weather
                st.success(f"weather in {weather_data["name"]}:")
                st.write(f"**Temperature:** {weather_data["main"]["temp"]} °C")
                st.write(f"**Weather:** {weather_data["weather"][0]['description'].capitalize()}")
                st.write(f"**Humidity:** {weather_data["main"]["humidity"]}")
                st.write(f"**Wind Speed:** {weather_data["wind"]["speed"]}m/s")
        else:
            st.warning("please enter a city name")
if __name__ == "__main__":
    main()





