import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import time

# Konfigurasi Halaman (Biar Lebar)
st.set_page_config(page_title="Crypto Arbitrage Hunter", layout="wide")

# Koneksi DB
DB_URL = st.secrets["db_url"]
engine = create_engine(DB_URL)

st.title("💰 Real-Time Arbitrage Monitor")

# --- QUERY 1: UNTUK GRAFIK (Ambil Data Banyak tapi Ringan) ---
def get_chart_data():
    query = """
    SELECT DISTINCT ON (timestamp) 
        timestamp, 
        profit_pct 
    FROM dbt_analytics.arbitrage_opportunities 
    ORDER BY timestamp DESC, profit_pct DESC
    LIMIT 200 -- Ambil 200 titik data biar grafik kelihatan panjang
    """
    return pd.read_sql(query, engine)

# --- QUERY 2: UNTUK TABEL (Ambil Sedikit tapi Detail) ---
def get_table_data():
    query = """
    SELECT DISTINCT ON (timestamp) * 
    FROM dbt_analytics.arbitrage_opportunities 
    ORDER BY timestamp DESC, profit_pct DESC
    LIMIT 10
    """
    return pd.read_sql(query, engine)

# Auto refresh
placeholder = st.empty()

while True:
    df_chart = get_chart_data()
    df_table = get_table_data()
    
    with placeholder.container():
        # KPI Cards (Pakai data terbaru dari tabel)
        if not df_table.empty:
            best_opp = df_table.iloc[0]
            
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Best Profit", f"{best_opp['profit_pct']:.2f}%")
            kpi2.metric("Buy At", best_opp['buy_exchange'].upper())
            kpi3.metric("Sell At", best_opp['sell_exchange'].upper())

            # --- GRAFIK (Dikecilkan pakai kolom) ---
            st.subheader("Profit Trend (Last 200 Data Points)")
            # Kita urutkan ulang biar grafik jalan dari kiri ke kanan
            chart_data = df_chart.sort_values('timestamp').set_index('timestamp')
            st.line_chart(chart_data, height=250) # Height 250 biar gak kegedean

            # --- TABEL ---
            st.subheader("Latest Opportunities")
            format_dict = {
                "buy_price": "${:,.2f}",
                "sell_price": "${:,.2f}",
                "gross_profit": "${:,.2f}",
                "profit_pct": "{:.2f}%"
            }
            st.dataframe(df_table.style.format(format_dict).highlight_max(axis=0, color='green'))
            
        else:
            st.warning("Waiting for data...")
            
        time.sleep(5)