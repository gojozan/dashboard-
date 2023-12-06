import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.express as px

#helper function
def get_AQI_category(x):
    if x <= 50:
        return "Good"
    elif x <= 100:
        return "Moderate"
    elif x <= 150:
        return "Unhealthy for Sensitive Groups"
    elif x <= 200:
        return "Unhealthy"
    elif x <= 300:
        return "Very Unhealthy"
    elif x > 300:
        return "Hazardous"
    else:
        return np.NaN
    
def create_aqi_daily(df):
  aqi_daily = df.groupby(by='date')['avg_AQI'].mean().reset_index()
  aqi_daily.columns = ['date', 'avg_AQI']
  aqi_daily['avg_AQI'] = round(aqi_daily['avg_AQI'])
  aqi_daily['AQI_category'] = aqi_daily["avg_AQI"].apply(lambda x: get_AQI_category(x))

  return aqi_daily

def create_pollutants_daily(df):
  pollutants = ['PM2_5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
  pollutants_daily = df.groupby('date')[pollutants].mean().reset_index()
  pollutants_daily.columns = ['date', 'PM2_5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
  pollutants_daily[pollutants] = round(pollutants_daily[pollutants])

  return pollutants_daily

def create_aqi_ranking(df):
  aqi_station_ranking = df.groupby(by='station')['avg_AQI'].mean().reset_index()
  aqi_station_ranking.columns = ['station', 'avg_AQI']
  aqi_station_ranking['avg_AQI'] = round(aqi_station_ranking['avg_AQI'])
  aqi_station_ranking['AQI_category'] = aqi_station_ranking["avg_AQI"].apply(lambda x: get_AQI_category(x))

  return aqi_station_ranking
    

#load cleaned data
all_df = pd.read_csv("all_data.csv")

#pembuatan filter
all_df["date" ] = pd.to_datetime(all_df["date"])
min_date = all_df["date"].min()
max_date = all_df["date"].max()

with st.sidebar:

  start_date, end_date = st.date_input(
      label = 'Rentang Waktu', min_value=min_date,
      max_value = max_date,
      value=[min_date, max_date]
  )

#data yang sudah difilter
main_df = all_df[(all_df["date"] >= str(start_date)) & (all_df["date"] <= str(end_date))]

aqi_daily = create_aqi_daily(main_df)
pollutants_daily = create_pollutants_daily(main_df)
aqi_station_ranking = create_aqi_ranking(main_df)

st.header('Air Quality Dashboard 💨')
st.text("")
st.subheader('Air Quality Index (AQI) Ranking: Stations from Worst to Best')

print(aqi_station_ranking['avg_AQI'].isnull().sum())
aqi_station_ranking = aqi_station_ranking.sort_values(by='avg_AQI')

color_mapping = {
    'Good': 'green',
    'Moderate': 'yellow',
    'Unhealthy for Sensitive Groups': 'orange',
    'Unhealthy': 'red',
    'Very Unhealthy': 'purple',
    'Hazardous': 'maroon'
}

aqi_station_ranking['Color'] = aqi_station_ranking['AQI_category'].map(color_mapping)


# Creating a horizontal bar chart with colors based on AQI categories
plt.figure(figsize=(15, 6))
bars = plt.barh(aqi_station_ranking['station'], aqi_station_ranking['avg_AQI'], color=aqi_station_ranking['Color'])
plt.xlabel('AQI')
plt.ylabel('Stasiun')

# Adding value labels next to each bar
for bar, value in zip(bars, aqi_station_ranking['avg_AQI']):
    plt.text(bar.get_width() + 2, bar.get_y() + bar.get_height() / 2, str(value), va='center', color='black')

plt.tight_layout()

st.pyplot(plt)


#memberi space secara vertikal
st.text("")


st.subheader('Daily AQI')

col1, col2 = st.columns(2)

with col1:
    avg_aqi = round(aqi_daily['avg_AQI'].mean())
    st.markdown(
        f"""
        <div style="text-align: center; font-size: small;">
            <p style="font-size: larger; font-weight: bold;">Average AQI</p>
            <p style="font-weight: bold;font-size: 30px">{avg_aqi}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    avg_aqi_category = get_AQI_category(avg_aqi)
    st.markdown(
        f"""
        <div style="text-align: center; font-size: small;">
            <p style="font-size: larger;font-weight: bold;">AQI Category</p>
            <p>{avg_aqi_category}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Daily AQI 
aqi_daily['date'] = pd.to_datetime(aqi_daily['date'].astype(str) + ' 00:00:00')

# Create a Plotly Express line chart with hover tooltips
fig = px.line(aqi_daily, x='date', y='avg_AQI', line_shape='linear', labels={'avg_AQI': 'AQI'},
              title='Tren Data AQI dari Waktu ke Waktu', template='plotly_white',
              hover_data={'AQI_category': True, 'avg_AQI': ':'})

# Add shaded areas for different AQI categories
fig.add_shape(type='rect', x0=aqi_daily['date'].iloc[0], x1=aqi_daily['date'].iloc[-1], y0=0, y1=50, fillcolor='green', opacity=0.7, layer='below', line_width=0)
fig.add_shape(type='rect', x0=aqi_daily['date'].iloc[0], x1=aqi_daily['date'].iloc[-1], y0=50, y1=100, fillcolor='yellow', opacity=0.7, layer='below', line_width=0)
fig.add_shape(type='rect', x0=aqi_daily['date'].iloc[0], x1=aqi_daily['date'].iloc[-1], y0=100, y1=150, fillcolor='orange', opacity=0.7, layer='below', line_width=0)
fig.add_shape(type='rect', x0=aqi_daily['date'].iloc[0], x1=aqi_daily['date'].iloc[-1], y0=150, y1=200, fillcolor='red', opacity=0.7, layer='below', line_width=0)
fig.add_shape(type='rect', x0=aqi_daily['date'].iloc[0], x1=aqi_daily['date'].iloc[-1], y0=200, y1=300, fillcolor='purple', opacity=0.7, layer='below', line_width=0)
fig.add_shape(type='rect', x0=aqi_daily['date'].iloc[0], x1=aqi_daily['date'].iloc[-1], y0=300, y1=400, fillcolor='maroon', opacity=0.7, layer='below', line_width=0)

# Display the Plotly chart in Streamlit app
st.plotly_chart(fig)


categories = ["Good", "Moderate", "Unhealthy for Sensitive Groups", "Unhealthy", "Very Unhealthy", "Hazardous"]
colors = ["green", "yellow", "orange", "red", "purple", "maroon"]

legend_html = """
    <style>
        .legend-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .legend-table th, .legend-table td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .color-box {
            width: 20px;
            height: 20px;
            display: inline-block;
            margin-right: 5px;
        }
    </style>
    <table class="legend-table">
        <tr>
            <th>Category</th>
            <th style="text-align: center;">Color</th>
        </tr>
        """ + "".join(f"<tr><td>{category}</td><td style='text-align: center;'><div class='color-box' style='background-color: {color};'>&nbsp;</div></td></tr>" for category, color in zip(categories, colors)) + """
    </table>
"""
# Display the legend using Streamlit markdown
st.markdown(legend_html, unsafe_allow_html=True)


#memberi space secara vertikal
st.text("")


#Daily Pollutants Concentration
st.subheader('Daily Pollutants Concentration')
st.markdown('<h5 style="text-align: center;">Average Pollutants Concentration</h5>', unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    avg_pm_25 = round(pollutants_daily['PM2_5'].mean())
    st.metric("PM 2.5", value=avg_pm_25)
with col2:
    avg_pm10 = round(pollutants_daily['PM10'].mean())
    st.metric("PM 10", value=avg_pm10)
with col3:
    avg_so2 = round(pollutants_daily['SO2'].mean())
    st.metric("SO2", value=avg_so2)
with col4:
    avg_no2 = round(pollutants_daily['NO2'].mean())
    st.metric("NO2", value=avg_no2)
with col5:
    avg_co = round(pollutants_daily['CO'].mean())
    st.metric("CO", value=avg_co)
with col6:
    avg_o3 = round(pollutants_daily['O3'].mean())
    st.metric("O3", value=avg_o3)


#Visualisasi Data Polutan Secara Interaktif
plt.figure(figsize=(12, 8))

pollutants = ['PM2_5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']

plot_data_list = []

for pollutant in pollutants:
    data = {'date': pollutants_daily['date'], 'pollutant': pollutant, 'concentration': pollutants_daily[pollutant]}
    plot_data_list.append(pd.DataFrame(data))

plot_data = pd.concat(plot_data_list, ignore_index=True)

fig = px.line(plot_data, x='date', y='concentration', color='pollutant', labels={'concentration': 'Concentration'}, title='Pollutant Concentrations Over Time')

st.plotly_chart(fig)
