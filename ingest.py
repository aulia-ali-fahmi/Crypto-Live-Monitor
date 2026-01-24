import ccxt
import pandas as pd
from sqlalchemy import create_engine
import time
from datetime import datetime


# Link ambil dari neon > connection string
DB_URL = "postgresql://neondb_owner:npg_sPqRlkjmQ04J@ep-gentle-king-a1yepbkv-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require" 
engine = create_engine(DB_URL)

# Konfigurasi exchange
exchanges = {
    'binance': ccxt.binance({
        'options': {
            'defaultType': 'spot', # Ditambah ini biar fokus ambil nilai spot
        },
        'timeout': 30000, # Tambah waktu tunggu 30 detik biar gak gampang putus
    }),
    'kraken': ccxt.kraken(),
    'coinbase': ccxt.coinbase()
}

symbol = 'BTC/USDT' # Fokus 1 pasangan dulu

def fetch_prices():
    data_list = []
    
    for name, exchange in exchanges.items():
        try:
            # Ambil data ticker (harga saat ini)
            ticker = exchange.fetch_ticker(symbol)
            
            # Ambil Bid (Harga orang mau beli) dan Ask (Harga orang mau jual)
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
        # Ambil data
        prices = fetch_prices()
        
        if prices:
            # Ubah ke dataframe/tabel
            df = pd.DataFrame(prices)
            
            # Masukkan ke database (table: raw_prices)
            # if_exists='append' artinya nambah data terus ke bawah
            df.to_sql('raw_prices', engine, if_exists='append', index=False)
            print(f"Data tersimpan jam {datetime.now()}")
        
        # Tunggu 60 detik sebelum ambil lagi (biar gak kena ban)
        time.sleep(60)

if __name__ == "__main__":
    main()