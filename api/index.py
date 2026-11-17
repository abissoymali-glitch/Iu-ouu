from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import re
import urllib.request
import ssl

# Admin Şifresi
ADMIN_KEY = "ziyapurna1010"

# Geçici Hafıza (RAM'de tutulur)
STOKLAR = []
STOK_SAYACI = 0

UYGULAMALAR = ["WhatsApp", "Facebook", "Instagram", "Telegram", "Bip", "Twitter", "TikTok", "Discord", "Google"]
ULKELER = ["Türkiye", "Rusya", "ABD", "Almanya", "Fransa", "İngiltere", "Hindistan", "Brezilya", "Endonezya", "Nijerya", "Mısır", "Pakistan", "Bangladeş", "Meksika"]

def get_formatted_stocks():
    grouped = {}
    for data in STOKLAR:
        app = data.get('platform', 'Bilinmeyen')
        country = data.get('country', 'Bilinmeyen')
        if app not in grouped:
            grouped[app] = {}
        if country not in grouped[app]:
            grouped[app][country] = 0
        grouped[app][country] += 1
    return grouped

class handler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        global STOKLAR, STOK_SAYACI
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)
        key = query.get('key', [''])[0]

        # FAVICON HATASINI ÇÖZÜMÜ
        if path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-Type', 'image/x-icon')
            self.end_headers()
            return

        # ANA DİZİN
        if path == '/' or path == '/api/index':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"mesaj": "OTP API Calisiyor", "stok_sayisi": len(STOKLAR)}, ensure_ascii=False, indent=4).encode('utf-8'))
            return

        # ADMIN PANELİ
        if path == '/admin':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            if key != ADMIN_KEY:
                self.wfile.write("<h1>Yetkisiz Erişim</h1>".encode('utf-8'))
                return
            html = f"""
            <html><head><title>OTP Admin Panel</title><meta charset="utf-8"></head>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #1e1e1e; color: #fff;">
                <h2>🛠️ Admin Panel</h2>
                <form action="/admin_islem" method="GET">
                    <input type="hidden" name="key" value="{key}">
                    <button type="submit" name="islem" value="listele" style="padding: 10px; margin: 5px; background: #3498db; color: white; border: none; border-radius: 5px;">📋 Stok Listesi</button>
                    <button type="submit" name="islem" value="ekle_sayfa" style="padding: 10px; margin: 5px; background: #2ecc71; color: white; border: none; border-radius: 5px;">➕ Stok Ekle</button>
                    <button type="submit" name="islem" value="sil" style="padding: 10px; margin: 5px; background: #e74c3c; color: white; border: none; border-radius: 5px;">🗑️ Tüm Stokları Sil</button>
                </form>
            </body></html>
            """
            self.wfile.write(html.encode('utf-8'))
            return

        # ADMIN İŞLEMLERİ
        if path == '/admin_islem':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            if key != ADMIN_KEY:
                self.wfile.write("<h1>Yetkisiz Erişim</h1>".encode('utf-8'))
                return
            islem = query.get('islem', [''])[0]

            if islem == "listele":
                stocks = get_formatted_stocks()
                html = f"<h2>📋 Stok Listesi</h2><ul>"
                for app, countries in stocks.items():
                    html += f"<li><b>{app}</b><ul>"
                    for c, count in countries.items():
                        html += f"<li>{c}: {count} numara</li>"
                    html += "</ul></li>"
                html += f"</ul><br><a href='/admin?key={key}' style='color: #3498db;'>🔙 Geri Dön</a>"
                self.wfile.write(html.encode('utf-8'))
                return

            elif islem == "sil":
                STOKLAR.clear()
                self.wfile.write(f"<h2>🗑️ Tüm Stoklar Silindi!</h2><br><a href='/admin?key={key}' style='color: #3498db;'>🔙 Geri Dön</a>".encode('utf-8'))
                return

            elif islem == "ekle_sayfa":
                html = f"""
                <h2>➕ Stok Ekle</h2>
                <form action="/admin_islem" method="GET">
                    <input type="hidden" name="key" value="{key}">
                    <input type="hidden" name="islem" value="ekle_kaydet">
                    <label>Uygulama Seçin:</label><br>
                    <select name="app">
                """
                for u in UYGULAMALAR:
                    html += f"<option value='{u}'>{u}</option>"
                html += "</select><br><br><label>Ülke Seçin:</label><br><select name='country'>"
                for u in ULKELER:
                    html += f"<option value='{u}'>{u}</option>"
                html += """
                    </select><br><br>
                    <label>Numaraları yapıştırın:</label><br>
                    <textarea name="numbers" rows="10" cols="30"></textarea><br><br>
                    <button type="submit" style="padding: 10px; background: #2ecc71; color: white; border: none; border-radius: 5px;">Kaydet</button>
                </form>
                <br><a href='/admin?key={key}' style='color: #3498db;'>🔙 Geri Dön</a>
                """
                self.wfile.write(html.encode('utf-8'))
                return

            elif islem == "ekle_kaydet":
                app = query.get('app', [''])[0]
                country = query.get('country', [''])[0]
                numbers_text = query.get('numbers', [''])[0]
                if app and country and numbers_text:
                    raw_nums = re.split(r'[,\s]+', numbers_text)
                    valid_nums = [re.sub(r"\D", "", n) for n in raw_nums if 8 <= len(re.sub(r"\D", "", n)) <= 15]
                    for num in valid_nums:
                        STOK_SAYACI += 1
                        STOKLAR.append({"id": STOK_SAYACI, "number": num, "platform": app, "country": country})
                    self.wfile.write(f"<h2>✅ {len(valid_nums)} numara eklendi.</h2><br><a href='/admin?key={key}' style='color: #3498db;'>🔙 Geri Dön</a>".encode('utf-8'))
                else:
                    self.wfile.write("<h2>❌ Eksik bilgi girdiniz.</h2>".encode('utf-8'))
                return
            return

        # STOK DURUMU (Herkese Açık)
        if path == '/stok_durumu':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            stocks = get_formatted_stocks()
            self.wfile.write(json.dumps(stocks, ensure_ascii=False, indent=4).encode('utf-8'))
            return

        # NUMARA ALMA
        if path == '/numara_al':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            app = query.get('app', [''])[0]
            country = query.get('country', [''])[0]
            count = int(query.get('adet', ['1'])[0])
            if count > 20: count = 20
            if not app or not country:
                self.wfile.write(json.dumps({"hata": "Uygulama ve ülke belirtmelisiniz."}, ensure_ascii=False).encode('utf-8'))
                return
            matching_stocks = [s for s in STOKLAR if s['platform'].lower() == app.lower() and s['country'].lower() == country.lower()]
            if not matching_stocks:
                self.wfile.write(json.dumps({"hata": "Stok bulunamadı."}, ensure_ascii=False).encode('utf-8'))
                return
            if len(matching_stocks) < count: count = len(matching_stocks)
            selected_stocks = matching_stocks[:count]
            for stock in selected_stocks:
                STOKLAR.remove(stock)
            self.wfile.write(json.dumps({"durum": "basarili", "verilen_adet": count, "numaralar": [s['number'] for s in selected_stocks]}, ensure_ascii=False, indent=4).encode('utf-8'))
            return

        # OTOMATİK KOD ÇEKME
        if path == '/kod_cek':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request("http://194.238.28.236:8000/container", headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                    data = response.read().decode('utf-8')
                    parsed_data = json.loads(data)
                    new_added = 0
                    if isinstance(parsed_data, list):
                        for item in parsed_data:
                            exists = any(s.get('number') == item.get('number') and s.get('otp') == item.get('otp') for s in STOKLAR)
                            if not exists:
                                STOK_SAYACI += 1
                                STOKLAR.append({"id": STOK_SAYACI, "number": item.get('number'), "otp": item.get('otp'), "platform": item.get('platform', 'Bilinmeyen'), "country": item.get('country', 'Bilinmeyen'), "sms": item.get('sms', ''), "time": item.get('time', '')})
                                new_added += 1
                    self.wfile.write(json.dumps({"durum": "basarili", "yeni_eklenen": new_added, "toplam_stok": len(STOKLAR)}, ensure_ascii=False, indent=4).encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({"hata": str(e)}, ensure_ascii=False).encode('utf-8'))
            return

        # 404
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"mesaj": "Gecersiz endpoint"}).encode('utf-8'))
        return
