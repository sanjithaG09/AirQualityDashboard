🌍 Air Quality Monitoring Dashboard :
A real-time interactive web dashboard built using Python and Streamlit to monitor air quality metrics such as PM2.5, PM10, CO, NO₂, SO₂, and O₃.
The application fetches live air quality data from the OpenAQ API and presents it in a clean, visual, and easy-to-understand format. Implemented address-based geocoding to locate nearby monitoring stations,displayed latest pollutant readings by parameter, and plotted daily air quality trends over a user-selected date range using interactive charts.
How it Works :
1.The app sends API requests to OpenAQ to fetch pollutant concentration data.
2.Data is processed using Pandas for cleaning and aggregation.
3.Streamlit widgets allow users to select cities and pollutants.
4.Visualizations help users understand current air quality levels and trends.
Tech: Python, Streamlit, OpenAQ API, pandas, Plotly, Geopy 
