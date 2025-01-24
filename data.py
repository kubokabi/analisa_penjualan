import pandas as pd
import random
from datetime import datetime, timedelta

# Fungsi untuk menghasilkan data penjualan
def generate_sales_data(num_records):
    products = [
        "Kemeja", "Celana Cinos", "Topi", "Jaket Bomber", 
        "Sepatu Nike", "Jas Formal", "Kemeja Putih", 
        "Baju Olahraga", "Sepatu Reebok", "Sandal Swallo"
    ]
    
    data = []
    start_date = datetime(2025, 1, 1)
    
    for i in range(num_records):
        date = start_date + timedelta(days=random.randint(0, 30))  # Random date within 30 days
        product = random.choice(products)
        quantity_sold = random.randint(1, 20)  # Random quantity sold
        price = random.randint(5000, 20000)  # Random price
        total_sales = quantity_sold * price
        
        data.append([date.strftime('%Y-%m-%d'), product, quantity_sold, price, total_sales])
    
    return data

# Generate 100,000 records
sales_data = generate_sales_data(50)

# Create a DataFrame
df = pd.DataFrame(sales_data, columns=["tanggal", "produk", "jumlah_terjual", "harga", "total_penjualan"])

# Save to CSV
df.to_csv("data_penjualan.csv", index=False)