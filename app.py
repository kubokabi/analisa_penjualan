import matplotlib
from matplotlib.ticker import FuncFormatter
matplotlib.use('Agg')  # Menggunakan backend non-GUI agar Matplotlib dapat berjalan di server tanpa antarmuka grafis

from flask import Flask, request, jsonify, render_template
import pandas as pd
import matplotlib.pyplot as plt
import io, base64
from flask_cors import CORS
import logging

# Inisialisasi aplikasi Flask dan aktifkan CORS
app = Flask(__name__)
CORS(app)  # Mengizinkan semua origin, namun bisa dibatasi untuk domain tertentu jika diperlukan

# Konfigurasi logging untuk debugging dan pelaporan error
logging.basicConfig(level=logging.INFO)

# Route untuk menampilkan halaman upload file
@app.route('/')
def index():
    return render_template('upload.html')  # Menampilkan formulir untuk mengunggah file

# Route untuk menangani unggahan file
@app.route('/upload', methods=['POST'])
def upload_file():
    # Periksa apakah file ada di request
    if 'file' not in request.files:
        logging.error("Tidak ada file yang diunggah.")
        return jsonify({"error": "Tidak ada file yang diunggah"}), 400  # Jika tidak ada file yang diunggah

    file = request.files['file']

    # Periksa apakah file yang diunggah berformat CSV
    if not file.filename.endswith('.csv'):
        logging.error("Format file tidak valid. Diharapkan file CSV.")
        return jsonify({"error": "Format file tidak valid. Harap unggah file CSV."}), 400  # Jika file bukan CSV

    try:
        # Membaca file CSV ke dalam DataFrame pandas
        df = pd.read_csv(file)

        # Memastikan bahwa semua kolom yang dibutuhkan tersedia
        required_columns = {'tanggal', 'produk', 'total_penjualan', 'jumlah_terjual', 'harga'}
        if not required_columns.issubset(df.columns):
            logging.error(f"Kolom yang dibutuhkan hilang. Kolom yang diperlukan: {required_columns}")
            return jsonify({"error": f"Kolom hilang. Kolom yang diperlukan: {required_columns}"}), 400  # Jika kolom tidak lengkap

        # Mengonversi kolom 'tanggal' ke format datetime
        df['tanggal'] = pd.to_datetime(df['tanggal'], format='%Y-%m-%d', errors='coerce')
        if df['tanggal'].isnull().any():  # Jika ada tanggal yang tidak valid
            logging.error("Beberapa baris memiliki tanggal tidak valid di kolom 'tanggal'.")
            return jsonify({"error": "Beberapa baris memiliki tanggal tidak valid di kolom 'tanggal'. Pastikan format tanggal adalah 'YYYY-MM-DD'."}), 400

        # Menghapus baris dengan tanggal tidak valid
        df = df.dropna(subset=['tanggal'])

        # Menghapus duplikat berdasarkan 'tanggal' dan 'produk'
        df = df.drop_duplicates(subset=['tanggal', 'produk'])

        # Menghitung tren penjualan berdasarkan tanggal dan produk (fokus pada jumlah_terjual)
        trend_sales = df.groupby(['tanggal', 'produk']).agg(
            jumlah_terjual=('jumlah_terjual', 'sum'),
            harga=('harga', 'mean')  # Menghitung rata-rata harga per produk
        ).reset_index()

        # Format data menjadi format ribuan
        trend_sales['jumlah_terjual'] = trend_sales['jumlah_terjual'].apply(lambda x: f"{int(x):,}")
        trend_sales['harga'] = trend_sales['harga'].apply(lambda x: f"{int(x):,}")

        # Konversi data tren ke format dictionary setelah diformat
        trend_data = trend_sales.to_dict(orient='records')

        # Log data penjualan yang diformat untuk debugging
        logging.info(f"Data Tren (diformat): {trend_data}")

        # Menghitung produk dengan jumlah terjual tertinggi, tengah, dan terendah
        total_sales_values = df.groupby('produk')['jumlah_terjual'].sum().to_dict()
        highest_sale = max(total_sales_values.values())
        lowest_sale = min(total_sales_values.values())
        median_sale = pd.Series(total_sales_values.values()).median()

        highest_product = [product for product, sales in total_sales_values.items() if sales == highest_sale]
        lowest_product = [product for product, sales in total_sales_values.items() if sales == lowest_sale]
        median_product = [product for product, sales in total_sales_values.items() if sales == median_sale]

        # Membuat grafik tren jumlah terjual
        plt.figure(figsize=(10, 5))
        plt.plot(trend_sales['tanggal'], trend_sales['jumlah_terjual'].apply(lambda x: int(x.replace(",", ""))),
                 marker='o', linestyle='-', color='b')

        # Format sumbu y ke format ribuan
        formatter = FuncFormatter(lambda x, _: f'{int(x):,}')
        plt.gca().yaxis.set_major_formatter(formatter)

        # Sesuaikan sumbu x untuk menampilkan nama produk dan tanggal
        labels = [f"{row['produk']} ({row['tanggal'].strftime('%Y-%m-%d')})" for _, row in trend_sales.iterrows()]
        plt.xticks(trend_sales['tanggal'], labels, rotation=45, ha='right')

        plt.title('Tren Jumlah Terjual')
        plt.xlabel('Produk dan Tanggal')
        plt.ylabel('Jumlah Terjual')
        plt.grid(True)

        # Simpan grafik ke buffer dalam format PNG
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')  # bbox_inches='tight' untuk mengurangi ruang kosong
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()  # Konversi gambar ke string base64 untuk ditampilkan di HTML

        # Tampilkan template hasil dengan data penjualan, grafik, dan analisis tren produk
        return render_template('result.html', trend_data=trend_data,
                               graph_url=f"data:image/png;base64,{graph_url}", highest_product=highest_product,
                               lowest_product=lowest_product, median_product=median_product)

    except pd.errors.EmptyDataError:
        # Tangani jika file CSV kosong
        logging.error("File CSV yang diunggah kosong.")
        return jsonify({"error": "File CSV yang diunggah kosong."}), 400
    except KeyError as e:
        # Tangani jika kolom yang diperlukan hilang
        logging.error(f"Kolom yang hilang: {e}")
        return jsonify({"error": f"Kolom yang hilang: {e}"}), 400
    except Exception as e:
        # Tangani error lainnya yang tidak terduga
        logging.error(f"Error tidak terduga: {e}")
        return jsonify({"error": f"Terjadi error yang tidak terduga: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)  # Jalankan aplikasi Flask dalam mode debug untuk pengembangan
