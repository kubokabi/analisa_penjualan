from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Fungsi untuk melakukan scraping (Contoh: Scraping daftar buku dari books.toscrape.com)
def scrape_data(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        data = []
        
        # Logika scraping spesifik untuk books.toscrape.com sebagai demo
        products = soup.find_all('article', class_='product_pod')
        
        for product in products:
            title = product.h3.a['title'] if product.h3 and product.h3.a else 'N/A'
            price_elem = product.find('p', class_='price_color')
            price = price_elem.text if price_elem else 'N/A'
            avail_elem = product.find('p', class_='instock availability')
            availability = avail_elem.text.strip() if avail_elem else 'N/A'
            rating = product.p['class'][1] if product.p and len(product.p.get('class', [])) > 1 else 'No Rating'
            
            data.append({
                'Judul': title,
                'Harga': price,
                'Ketersediaan': availability,
                'Rating': rating
            })
            
        return data, None
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    
    if not url:
        flash('URL wajib diisi!', 'danger')
        return redirect(url_for('index'))
    
    # Default ke situs demo jika tidak valid
    if not url.startswith('http'):
        url = 'http://books.toscrape.com/'

    data, error = scrape_data(url)
    
    if error:
        flash(f'Gagal mengambil data: {error}', 'danger')
        return redirect(url_for('index'))
    
    if not data:
        flash('Tidak ada data yang ditemukan di URL tersebut.', 'warning')
        return redirect(url_for('index'))
    
    df = pd.DataFrame(data)
    table_data = df.to_dict(orient='records')
    columns = df.columns.tolist()
    
    return render_template('result.html', data=table_data, columns=columns, source_url=url)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
