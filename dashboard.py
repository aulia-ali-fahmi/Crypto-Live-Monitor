import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import time

# --- KONFIGURASI ---
# Gunakan link neon yang sama
DB_URL = "postgresql://neondb_owner:npg_sPqRlkjmQ04J@ep-gentle-king-a1yepbkv-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DB_URL)

st.set_page_config(page_title="Crypto Arbitrage Hunter", layout="wide")
st.title("💰 Real-Time Arbitrage Monitor")

# Fungsi ambil data
def get_data():
    # Ambil data dari tabel hasil olahan dbt
    # Pastikan nama schema 'dbt_analytics' sesuai yang di profiles.yml
    query = "SELECT * FROM dbt_analytics.arbitrage_opportunities"
    return pd.read_sql(query, engine)

# Auto Refresh logic sederhana
placeholder = st.empty()

while True:
    df = get_data()
    
    with placeholder.container():
        # KPI Cards
        kpi1, kpi2, kpi3 = st.columns(3)
        
        if not df.empty:
            best_opp = df.iloc[0] # Ambil baris pertama (paling untung)
            
            kpi1.metric(
                label="Best Opportunity", 
                value=f"{best_opp['profit_pct']:.2f}%",
                delta="Profit Bersih"
            )
            kpi2.metric(
                label="Buy At", 
                value=best_opp['buy_exchange'].upper()
            )
            kpi3.metric(
                label="Sell At", 
                value=best_opp['sell_exchange'].upper()
            )

            st.subheader("Detail Peluang Saat Ini")
            # Format kolom harga dan profit agar ada $ dan 2 desimal
            format_dict = {
                "buy_price": "${:,.2f}",
                "sell_price": "${:,.2f}",
                "gross_profit": "${:,.2f}",
                "profit_pct": "{:.2f}%"
            }
            # Warnai tabel
            st.dataframe(df.style.format(format_dict).highlight_max(axis=0, color='green'))
        else:
            st.warning("Belum ada peluang arbitrase yang profit saat ini.")
            
        time.sleep(5) # Refresh tampilan tiap 5 detik