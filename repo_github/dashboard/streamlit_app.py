import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# ─────────────────────────────────────────
# untuk konfigurasi
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Smart Farming Dashboard",
    layout="wide"
)

st.title("Smart Farming Sensor Dashboard")
st.markdown("Monitoring Soil Moisture, Temperature, Humidity, pH & Yield — 2024")

# ─────────────────────────────────────────
# untuk load data
# ─────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('Smart_Farming_Crop_Yield_2024.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['month'] = df['timestamp'].dt.to_period('M').astype(str)
    return df

df = load_data()

# Kolom utama
main_cols = ['soil_moisture_%', 'temperature_C', 'humidity_%', 'soil_pH', 'yield_kg_per_hectare']

# ─────────────────────────────────────────
# untuk filter di sidebar
# ─────────────────────────────────────────
st.sidebar.header("Filter Data")
crop_filter = st.sidebar.multiselect(
    "Pilih Crop Type:",
    options=df['crop_type'].unique(),
    default=df['crop_type'].unique()
)
df = df[df['crop_type'].isin(crop_filter)]

# ─────────────────────────────────────────
# untuk alert system
# ─────────────────────────────────────────
THRESHOLD_MOISTURE  = 25.0   # %
THRESHOLD_HUMIDITY  = 55.0   # %
THRESHOLD_TEMP      = 35.0   # °C
THRESHOLD_PH_LOW    = 5.5
THRESHOLD_PH_HIGH   = 7.5

# ─────────────────────────────────────────
# metrics card
# ─────────────────────────────────────────
latest = df.sort_values('timestamp').iloc[-1]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Soil Moisture", f"{latest['soil_moisture_%']:.1f}%")
col2.metric("Temperature",   f"{latest['temperature_C']:.1f}°C")
col3.metric("Humidity",      f"{latest['humidity_%']:.1f}%")
col4.metric("Soil pH",       f"{latest['soil_pH']:.2f}")
col5.metric("Yield",         f"{latest['yield_kg_per_hectare']:.0f} kg/ha")

st.markdown("---")

# ═══════════════════════════════════════════
# VISUALISASI 1: TIME SERIES TREN SENSOR
# ═══════════════════════════════════════════
st.subheader("1. Time Series — Tren Sensor per Bulan")

monthly = df.groupby('month')[main_cols].mean().reset_index()

sensor_choice = st.selectbox(
    "Pilih sensor untuk ditampilkan:",
    options=main_cols,
    format_func=lambda x: x.replace('_', ' ').title()
)

fig_ts = px.line(
    monthly, x='month', y=sensor_choice,
    markers=True,
    title=f"Tren Rata-rata {sensor_choice.replace('_',' ').title()} per Bulan",
    labels={'month': 'Bulan', sensor_choice: sensor_choice},
    color_discrete_sequence=['#2ecc71']
)
fig_ts.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_ts, use_container_width=True)

st.markdown("---")

# ═══════════════════════════════════════════
# VISUALISASI 2: GAUGE METER — KELEMBABAN
# ═══════════════════════════════════════════
st.subheader("2. Gauge Meter — Kondisi Sensor Saat Ini")

g1, g2, g3 = st.columns(3)

def make_gauge(value, title, threshold, max_val, unit):
    color = "red" if value < threshold else "green"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': f"{title}<br><span style='font-size:0.8em'>Threshold: {threshold}{unit}</span>"},
        gauge={
            'axis': {'range': [0, max_val]},
            'bar':  {'color': color},
            'steps': [
                {'range': [0, threshold],       'color': '#ffcccc'},
                {'range': [threshold, max_val], 'color': '#ccffcc'},
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': threshold
            }
        }
    ))
    fig.update_layout(height=300)
    return fig

with g1:
    st.plotly_chart(
        make_gauge(latest['humidity_%'],     "Humidity",      THRESHOLD_HUMIDITY, 100, "%"),
        use_container_width=True
    )
with g2:
    st.plotly_chart(
        make_gauge(latest['soil_moisture_%'], "Soil Moisture", THRESHOLD_MOISTURE, 100, "%"),
        use_container_width=True
    )
with g3:
    st.plotly_chart(
        make_gauge(latest['temperature_C'],  "Temperature",   THRESHOLD_TEMP,     50,  "°C"),
        use_container_width=True
    )

st.markdown("---")

# ═══════════════════════════════════════════
# VISUALISASI 3: HEATMAP KORELASI
# ═══════════════════════════════════════════
st.subheader("3. Heatmap — Korelasi Antar Sensor")

fig_heat, ax = plt.subplots(figsize=(8, 5))
corr = df[main_cols].corr()
sns.heatmap(
    corr, annot=True, fmt='.2f',
    cmap='coolwarm', linewidths=0.5,
    ax=ax
)
ax.set_title('Korelasi: Soil Moisture, Temperature, Humidity, pH, Yield')
plt.tight_layout()
st.pyplot(fig_heat)

st.markdown("---")

# ═══════════════════════════════════════════
# VISUALISASI 4: ALERT SYSTEM
# ═══════════════════════════════════════════
st.subheader("4. Alert System — Deteksi Data di Bawah Threshold")

# Tandai baris yang bermasalah
df['alert_moisture'] = df['soil_moisture_%'] < THRESHOLD_MOISTURE
df['alert_humidity'] = df['humidity_%']      < THRESHOLD_HUMIDITY
df['alert_temp']     = df['temperature_C']   > THRESHOLD_TEMP
df['alert_pH']       = (df['soil_pH'] < THRESHOLD_PH_LOW) | (df['soil_pH'] > THRESHOLD_PH_HIGH)
df['alert_any']      = df[['alert_moisture','alert_humidity','alert_temp','alert_pH']].any(axis=1)

total_alert = df['alert_any'].sum()
pct_alert   = total_alert / len(df) * 100

# Summary box
if total_alert > 0:
    st.error(f"Ditemukan **{total_alert} baris ({pct_alert:.1f}%)** data yang melanggar threshold!")
else:
    st.success("Semua data dalam kondisi normal.")

# Detail per alert type
a1, a2, a3, a4 = st.columns(4)
a1.metric("Low Moisture",  df['alert_moisture'].sum(), help=f"< {THRESHOLD_MOISTURE}%")
a2.metric("Low Humidity",  df['alert_humidity'].sum(), help=f"< {THRESHOLD_HUMIDITY}%")
a3.metric("High Temp",    df['alert_temp'].sum(),     help=f"> {THRESHOLD_TEMP}°C")
a4.metric("pH Abnormal",   df['alert_pH'].sum(),       help=f"< {THRESHOLD_PH_LOW} atau > {THRESHOLD_PH_HIGH}")

# Bar chart jumlah alert per bulan
alert_monthly = df.groupby('month')['alert_any'].sum().reset_index()
alert_monthly.columns = ['month', 'jumlah_alert']

fig_alert = px.bar(
    alert_monthly, x='month', y='jumlah_alert',
    color='jumlah_alert',
    color_continuous_scale=['green', 'yellow', 'red'],
    title='Jumlah Alert per Bulan',
    labels={'month': 'Bulan', 'jumlah_alert': 'Jumlah Alert'}
)
fig_alert.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_alert, use_container_width=True)

# Tabel data alert (merah)
with st.expander("Lihat Data yang Trigger Alert"):
    st.dataframe(
        df[df['alert_any']][
            ['timestamp','crop_type','soil_moisture_%','temperature_C',
             'humidity_%','soil_pH','yield_kg_per_hectare']
        ].style.applymap(
            lambda v: 'background-color: #ffcccc', 
            subset=['soil_moisture_%','temperature_C','humidity_%','soil_pH']
        ),
        use_container_width=True
    )

st.markdown("---")
st.caption("Smart Farming Dashboard © 2024 | Data: Smart_Farming_Crop_Yield_2024.csv")