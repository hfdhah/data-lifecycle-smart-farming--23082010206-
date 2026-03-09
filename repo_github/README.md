Smart Farming Sensor Dashboard
---
Pada proyek kali ini memvisualisasikan data sensor smart farming pada tahun 2024 
dengan tujuan memantau kondisi lahan secara real-time, mendeteksi anomali, dan menganalisis
faktor-faktor yang dapat memengaruhi hasil panen.

Dataset
---
- Sumber: Smart Farming Sensor data for Yield Prediction - Kaggle
- Link: https://www.kaggle.com/datasets/atharvasoundankar/smart-farming-sensor-data-for-yield-prediction/code
- Jumlah Data: 500 baris, 22 kolom
- Periode: Januari-Agustus 2024

Kolom Utama
---
Soil_Moisture_%, Temperature_C, Humadity_%, Soil_pH, dan Yield_kg_per_hectare.

Fitur Dashboard
---
1. Time Series: Untuk tren rata-rata sensor per bulan
2. Gauge Meter: Untuk status kondisi sensor saat ini yang memiliki indikator warna
3. Heatmap Korelasi: Untuk hubungan antar variabel sensor dan yield
4. Alert System: Untuk deteksi otomatis data yang melanggar threshold

Link streamlit yang dapat dijalankan
---
https://data-lifecyle-smart-farming-23082010206.streamlit.app/
