import ccxt
import pandas as pd
from sqlalchemy import create_engine
import time
from datetime import datetime

# --- KONFIGURASI DATABASE ---
# Ganti dengan Connection String dari Neon.tech Anda
# Pastikan formatnya dimulai dengan postgresql:// (bukan postgres://)
# Kalau dari Neon tulisannya postgres://, tambahkan 'ql' jadi postgresql://
DB_URL = "postgresql://neondb_owner:npg_sPqRlkjmQ04J@ep-gentle-king-a1yepbkv-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require" 
engine = create_engine(DB_URL)

# --- KONFIGURASI EXCHANGE ---
exchanges = {
    'binance': ccxt.binance({
        'options': {
            'defaultType': 'spot', # Cukup ini saja. Jangan tambah URLs aneh-aneh.
        },
        'timeout': 30000, # Tambah waktu tunggu jadi 30 detik biar gak gampang putus
    }),
    'kraken': ccxt.kraken(),
    'coinbase': ccxt.coinbase()
}

symbol = 'BTC/USDT' # Kita fokus 1 pasangan dulu

def fetch_prices():
    data_list = []
    
    for name, exchange in exchanges.items():
        try:
            # Ambil data ticker (harga saat ini)
            ticker = exchange.fetch_ticker(symbol)
            
            # Kita butuh Bid (Harga orang mau beli) dan Ask (Harga orang mau jual)
            data = {
                'timestamp': datetime.now(),
                'exchange': name,
                'symbol': symbol,
                'bid_price': ticker['bid'],
                'ask_price': ticker['ask']
            }
            data_list.append(data)
            print(f"Sukses ambil data {name}: Bid {data['bid_price']} | Ask {data['ask_price']}")
            
        except Exception as e:
            print(f"Gagal ambil data {name}: {e}")
    
    return data_list

def main():
    print("Mulai Monitoring Harga...")
    while True:
        # 1. Ambil Data
        prices = fetch_prices()
        
        if prices:
            # 2. Ubah ke DataFrame (Tabel)
            df = pd.DataFrame(prices)
            
            # 3. Masukkan ke Database (Table: raw_prices)
            # if_exists='append' artinya nambah data terus ke bawah
            df.to_sql('raw_prices', engine, if_exists='append', index=False)
            print(f"Data tersimpan jam {datetime.now()}")
        
        # 4. Tunggu 60 detik sebelum ambil lagi (biar gak kena ban)
        time.sleep(60)

if __name__ == "__main__":
    main()