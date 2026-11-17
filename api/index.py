from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import re
import urllib.request
import urllib.error
import ssl
from datetime import datetime, timedelta
import os
import traceback

def get_kv_creds():
    url = os.environ.get("KV_REST_API_URL") or os.environ.get("STORAGE_REST_API_URL") or os.environ.get("UPSTASH_REDIS_REST_URL")
    token = os.environ.get("KV_REST_API_TOKEN") or os.environ.get("STORAGE_REST_API_TOKEN") or os.environ.get("UPSTASH_REDIS_REST_TOKEN")
    if url: url = url.strip().rstrip('/')
    if token: token = token.strip()
    return url, token

def redis_req(*args):
    url, token = get_kv_creds()
    if not url or not token:
        return {"error": "Vercel'de Redis bağlantı değişkenleri EKSİK!"}
    try:
        data = json.dumps(args).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=5) as response:
            res = json.loads(response.read().decode('utf-8'))
            if 'error' in res: return {"error": f"Redis Hatası: {res['error']}"}
            return res.get('result')
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        return {"error": f"Upstash Hatası: {err_body}"}
    except Exception as e:
        return {"error": f"Bağlantı Hatası: {str(e)}"}

# SCAN ile stok anahtarlarını güvenli çekme fonksiyonu
def get_all_stock_keys():
    keys = []
    cursor = "0"
    while True:
        res = redis_req("SCAN", cursor, "MATCH", "stok:*", "COUNT", "1000")
        if isinstance(res, dict) and "error" in res:
            return res
        if not res or len(res) < 2:
            break
        cursor = str(res[0])
        keys.extend(res[1])
        if cursor == "0":
            break
    return keys

ADMIN_KEY = "ziyapurna1010"
UYGULAMALAR = ["WhatsApp", "Facebook", "Instagram", "Telegram", "Bip", "Twitter", "TikTok", "Discord", "Google"]

ULKE_KODLARI = {
    "1": "Amerika Birleşik Devletleri / Kanada", "7": "Rusya / Kazakistan", "20": "Mısır", "27": "Güney Afrika",
    "30": "Yunanistan", "31": "Hollanda", "32": "Belçika", "33": "Fransa", "34": "İspanya", "36": "Macaristan",
    "39": "İtalya", "40": "Romanya", "41": "İsviçre", "43": "Avusturya", "44": "İngiltere", "45": "Danimarka",
    "46": "İsveç", "47": "Norveç", "48": "Polonya", "49": "Almanya", "51": "Peru", "52": "Meksika", "53": "Küba",
    "54": "Arjantin", "55": "Brezilya", "56": "Şili", "57": "Kolombiya", "58": "Venezuela", "60": "Malezya",
    "61": "Avustralya", "62": "Endonezya", "63": "Filipinler", "64": "Yeni Zelanda", "65": "Singapur",
    "66": "Tayland", "81": "Japonya", "82": "Güney Kore", "84": "Vietnam", "86": "Çin", "90": "Türkiye",
    "91": "Hindistan", "92": "Pakistan", "93": "Afganistan", "94": "Sri Lanka", "95": "Myanmar", "98": "İran",
    "211": "Güney Sudan", "212": "Fas", "213": "Cezayir", "216": "Tunus", "218": "Libya", "220": "Gambiya",
    "221": "Senegal", "222": "Moritanya", "223": "Mali", "224": "Gine", "225": "Fildişi Sahili",
    "226": "Burkina Faso", "227": "Nijer", "228": "Togo", "229": "Benin", "230": "Mauritius", "231": "Liberya",
    "232": "Sierra Leone", "233": "Gana", "234": "Nijerya", "235": "Çad", "236": "Orta Afrika Cumhuriyeti",
    "237": "Kamerun", "238": "Cape Verde", "239": "Sao Tome ve Principe", "240": "Ekvator Ginesi",
    "241": "Gabon", "242": "Kongo", "243": "Demokratik Kongo Cumhuriyeti", "244": "Angola", "245": "Gine-Bissau",
    "246": "İngiliz Hint Okyanusu", "248": "Seyşeller", "249": "Sudan", "250": "Ruanda", "251": "Etiyopya",
    "252": "Somali", "253": "Cibuti", "254": "Kenya", "255": "Tanzanya", "256": "Uganda", "257": "Burundi",
    "258": "Mozambik", "260": "Zambiya", "261": "Madagaskar", "262": "Reunion", "263": "Zimbabve",
    "264": "Namibya", "265": "Malavi", "266": "Lesotho", "267": "Botsvana", "268": "Esvatini",
    "269": "Komorlar", "290": "Saint Helena", "291": "Eritre", "297": "Aruba", "298": "Faroe Adaları",
    "299": "Grönland", "350": "Cebelitarık", "351": "Portekiz", "352": "Lüksemburg", "353": "İrlanda",
    "354": "İzlanda", "355": "Arnavutluk", "356": "Malta", "357": "Kıbrıs", "358": "Finlandiya",
    "359": "Bulgaristan", "370": "Litvanya", "371": "Letonya", "372": "Estonya", "373": "Moldova",
    "374": "Ermenistan", "375": "Belarus", "376": "Andorra", "377": "Monako", "378": "San Marino",
    "380": "Ukrayna", "381": "Sırbistan", "382": "Karadağ", "383": "Kosova", "385": "Hırvatistan",
    "386": "Slovenya", "387": "Bosna-Hersek", "389": "Kuzey Makedonya", "420": "Çekya", "421": "Slovakya",
    "423": "Lihtenştayn", "500": "Falkland Adaları", "501": "Belize", "502": "Guatemala", "503": "El Salvador",
    "504": "Honduras", "505": "Nikaragua", "506": "Kosta Rika", "507": "Panama", "509": "Haiti",
    "590": "Guadeloupe", "591": "Bolivya", "592": "Guyana", "593": "Ekvador", "594": "Fransız Guyanası",
    "595": "Paraguay", "596": "Martinik", "597": "Surinam", "598": "Uruguay", "599": "Hollanda Antilleri",
    "670": "Doğu Timor", "672": "Norfolk Adası", "673": "Brunei", "674": "Nauru", "675": "Papua Yeni Gine",
    "676": "Tonga", "677": "Solomon Adaları", "678": "Vanuatu", "679": "Fiji", "680": "Palau",
    "681": "Wallis ve Futuna", "682": "Cook Adaları", "683": "Niue", "685": "Samoa", "686": "Kiribati",
    "687": "Yeni Kaledonya", "688": "Tuvalu", "689": "Fransız Polinezyası", "690": "Tokelau",
    "691": "Mikronezya", "692": "Marshall Adaları", "850": "Kuzey Kore", "852": "Hong Kong", "853": "Makao",
    "855": "Kamboçya", "856": "Laos", "880": "Bangladeş", "886": "Tayvan", "960": "Maldivler",
    "961": "Lübnan", "962": "Ürdün", "963": "Suriye", "964": "Irak", "965": "Kuveyt", "966": "Suudi Arabistan",
    "967": "Yemen", "968": "Umman", "970": "Filistin", "971": "Birleşik Arap Emirlikleri", "972": "İsrail",
    "973": "Bahreyn", "974": "Katar", "975": "Bhutan", "976": "Moğolistan", "977": "Nepal", "992": "Tacikistan",
    "993": "Türkmenistan", "994": "Azerbaycan", "995": "Gürcistan", "996": "Kırgızistan", "998": "Özbekistan"
}

def numara_ulke_bul(numara):
    numara = re.sub(r"\D", "", numara)
    for uzunluk in [3, 2, 1]:
        prefix = numara[:uzunluk]
        if prefix in ULKE_KODLARI:
            return ULKE_KODLARI[prefix]
    return "Bilinmeyen Ülke"

def fetch_source_codes():
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request("http://194.238.28.236:8000/container", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            data = response.read().decode('utf-8')
            parsed_data = json.loads(data)
            return parsed_data if isinstance(parsed_data, list) else []
    except Exception:
        return []

def get_formatted_stocks():
    keys = get_all_stock_keys()
    if isinstance(keys, dict) and "error" in keys: return keys 
    
    grouped = {}
    if not keys: return grouped
    
    for k in keys:
        val = redis_req("GET", k)
        if val and not (isinstance(val, dict) and "error" in val):
            try:
                data = json.loads(val)
                app = data.get('platform', 'Bilinmeyen')
                country = data.get('country', 'Bilinmeyen')
                if app not in grouped: grouped[app] = {}
                if country not in grouped[app]: grouped[app][country] = 0
                grouped[app][country] += 1
            except:
                pass
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
        try:
            self._handle_get()
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            error_trace = traceback.format_exc()
            self.wfile.write(f"<h2>Hata Oluştu!</h2><p>{str(e)}</p><pre style='background:#eee;padding:10px;'>{error_trace}</pre>".encode('utf-8'))

    def do_POST(self):
        try:
            self._handle_post()
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            error_trace = traceback.format_exc()
            self.wfile.write(f"<h2>Hata Oluştu!</h2><p>{str(e)}</p><pre style='background:#eee;padding:10px;'>{error_trace}</pre>".encode('utf-8'))

    def _handle_get(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)
        key = query.get('key', [''])[0]

        if path == '/favicon.ico':
            self.send_response(200); self.send_header('Content-Type', 'image/x-icon'); self.end_headers(); return

        if path == '/' or path == '/api/index':
            self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
            html = """
            <html><head><title>Yxce OTP API</title><meta charset="utf-8"></head>
            <body style="font-family: Arial, sans-serif; background-color: #121212; color: #e0e0e0; padding: 30px;">
                <h1 style="color: #2ecc71; text-align: center;">🚀 Yxce OTP API Servisi</h1>
                <p style="text-align: center; color: #aaa;">Sistem aktif ve çalışıyor.</p>
                <div style="max-width: 800px; margin: 0 auto; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                    <h3 style="border-bottom: 2px solid #333; padding-bottom: 10px;">📌 Mevcut Endpoint'ler</h3>
                    <div style="margin-bottom: 20px;"><h4 style="color: #3498db;">1. Canlı Trafik</h4><code style="background: #2a2a2a; padding: 5px; display: block; border-radius: 5px;">GET /live_trafik</code></div>
                    <div style="margin-bottom: 20px;"><h4 style="color: #3498db;">2. Kod Sorgulama</h4><code style="background: #2a2a2a; padding: 5px; display: block; border-radius: 5px;">GET /kod_sorgula?numara=905551234567</code></div>
                    <div style="margin-bottom: 20px;"><h4 style="color: #3498db;">3. Numara Alma</h4><code style="background: #2a2a2a; padding: 5px; display: block; border-radius: 5px;">GET /numara_al?app=WhatsApp&country=Kırgızistan&adet=5</code></div>
                    <div style="margin-bottom: 20px;"><h4 style="color: #3498db;">4. Stok Durumu</h4><code style="background: #2a2a2a; padding: 5px; display: block; border-radius: 5px;">GET /stok_durumu</code></div>
                </div>
            </body></html>
            """
            self.wfile.write(html.encode('utf-8'))
            return

        if path == '/live_trafik':
            self.send_response(200); self.send_header('Content-type', 'application/json; charset=utf-8'); self.end_headers()
            codes = fetch_source_codes()
            simdi = datetime.now()
            bes_dakika_once = simdi - timedelta(minutes=5)
            trafik_sayaci = {}
            for item in codes:
                zaman_str = item.get('time')
                if not zaman_str: continue
                try:
                    item_zaman = datetime.strptime(zaman_str, "%Y-%m-%d %H:%M:%S")
                    if item_zaman >= bes_dakika_once:
                        platform = str(item.get('platform', 'Bilinmeyen')).capitalize()
                        ulke = numara_ulke_bul(item.get('number', ''))
                        key_str = f"{ulke} {platform}"
                        if key_str not in trafik_sayaci: trafik_sayaci[key_str] = 0
                        trafik_sayaci[key_str] += 1
                except Exception: continue
            sirali_trafik = dict(sorted(trafik_sayaci.items(), key=lambda x: x[1], reverse=True))
            self.wfile.write(json.dumps({"son_5_dakika_trafik": sirali_trafik}, ensure_ascii=False, indent=4).encode('utf-8'))
            return

        if path == '/kod_sorgula':
            self.send_response(200); self.send_header('Content-type', 'application/json; charset=utf-8'); self.end_headers()
            aranan_numara = query.get('numara', [''])[0]
            if not aranan_numara:
                self.wfile.write(json.dumps({"hata": "Numara belirtilmedi."}, ensure_ascii=False).encode('utf-8')); return
            temiz_numara = re.sub(r"\D", "", aranan_numara)
            codes = fetch_source_codes()
            bulunan_kod = None
            for item in codes:
                num = re.sub(r"\D", "", str(item.get('number', '')))
                if num == temiz_numara:
                    bulunan_kod = item
                    break
            if bulunan_kod: self.wfile.write(json.dumps({"durum": "basarili", "veri": bulunan_kod}, ensure_ascii=False, indent=4).encode('utf-8'))
            else: self.wfile.write(json.dumps({"durum": "basarisiz", "mesaj": "Bu numaraya ait kod bulunamadi."}, ensure_ascii=False).encode('utf-8'))
            return

        if path == '/admin':
            self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
            if key != ADMIN_KEY: self.wfile.write("<h1>Yetkisiz Erişim</h1>".encode('utf-8')); return
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

        if path == '/admin_islem':
            self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
            if key != ADMIN_KEY: self.wfile.write("<h1>Yetkisiz Erişim</h1>".encode('utf-8')); return
            islem = query.get('islem', [''])[0]
            if islem == "listele":
                stocks = get_formatted_stocks()
                if isinstance(stocks, dict) and "error" in stocks:
                    self.wfile.write(f"<h2 style='color:red;'>Sistem Hatası!</h2><p>{stocks['error']}</p>".encode('utf-8'))
                    return
                html = f"<h2>📋 Stok Listesi</h2><ul>"
                for app, countries in stocks.items():
                    html += f"<li><b>{app}</b><ul>"
                    for c, count in countries.items(): html += f"<li>{c}: {count} numara</li>"
                    html += "</ul></li>"
                html += f"</ul><br><a href='/admin?key={key}' style='color: #3498db;'>🔙 Geri Dön</a>"
                self.wfile.write(html.encode('utf-8'))
                return
            elif islem == "sil":
                keys = get_all_stock_keys()
                if isinstance(keys, dict) and "error" in keys:
                    self.wfile.write(f"<h2 style='color:red;'>Hata: {keys['error']}</h2>".encode('utf-8')); return
                for k in keys: redis_req("DEL", k)
                self.wfile.write(f"<h2>🗑️ Tüm Stoklar Silindi!</h2><br><a href='/admin?key={key}' style='color: #3498db;'>🔙 Geri Dön</a>".encode('utf-8'))
                return
            elif islem == "ekle_sayfa":
                html = f"""
                <html><head><title>Stok Ekle</title><meta charset="utf-8"></head>
                <body style="font-family: Arial; padding: 20px; background-color: #1e1e1e; color: #fff;">
                <h2>➕ Stok Ekle (Dosya ile)</h2>
                <form action="/dosya_yukle_islem" method="POST" enctype="multipart/form-data">
                    <input type="hidden" name="key" value="{key}">
                    <label>Uygulama Seçin:</label><br>
                    <select name="app" style="padding: 5px;">
                """
                for u in UYGULAMALAR: html += f"<option value='{u}'>{u}</option>"
                html += f"""
                    </select><br><br>
                    <label>Numara Listesi (.txt) Seçin:</label><br>
                    <input type="file" name="dosya" accept=".txt"><br><br>
                    <button type="submit" style="padding: 10px 20px; background: #2ecc71; color: white; border: none; border-radius: 5px;">Dosyayı Yükle ve Ekle</button>
                </form>
                <br><a href='/admin?key={key}' style='color: #3498db;'>🔙 Geri Dön</a>
                </body></html>
                """
                self.wfile.write(html.encode('utf-8'))
                return

        if path == '/stok_durumu':
            self.send_response(200); self.send_header('Content-type', 'application/json; charset=utf-8'); self.end_headers()
            self.wfile.write(json.dumps(get_formatted_stocks(), ensure_ascii=False, indent=4).encode('utf-8'))
            return

        if path == '/numara_al':
            self.send_response(200); self.send_header('Content-type', 'application/json; charset=utf-8'); self.end_headers()
            app = query.get('app', [''])[0]
            country = query.get('country', [''])[0]
            count = int(query.get('adet', ['1'])[0])
            if count > 20: count = 20
            if not app or not country:
                self.wfile.write(json.dumps({"hata": "Uygulama ve ülke belirtmelisiniz."}, ensure_ascii=False).encode('utf-8')); return
            keys = get_all_stock_keys()
            if isinstance(keys, dict) and "error" in keys:
                self.wfile.write(json.dumps(keys, ensure_ascii=False).encode('utf-8')); return
            matching_keys = []
            for k in keys:
                val = redis_req("GET", k)
                if val and not (isinstance(val, dict) and "error" in val):
                    data = json.loads(val)
                    if data.get('platform', '').lower() == app.lower() and data.get('country', '').lower() == country.lower():
                        matching_keys.append(k)
            if not matching_keys:
                self.wfile.write(json.dumps({"hata": "Stok bulunamadı."}, ensure_ascii=False).encode('utf-8')); return
            if len(matching_keys) < count: count = len(matching_keys)
            selected_keys = matching_keys[:count]
            numaralar = []
            for k in selected_keys:
                val = redis_req("GET", k)
                if val and not (isinstance(val, dict) and "error" in val):
                    data = json.loads(val)
                    numaralar.append(data['number'])
                    redis_req("DEL", k)
            self.wfile.write(json.dumps({"durum": "basarili", "verilen_adet": count, "numaralar": numaralar}, ensure_ascii=False, indent=4).encode('utf-8'))
            return

        if path == '/kod_cek':
            self.send_response(200); self.send_header('Content-type', 'application/json; charset=utf-8'); self.end_headers()
            codes = fetch_source_codes()
            son_kodlar = codes[:50] if isinstance(codes, list) else []
            self.wfile.write(json.dumps(son_kodlar, ensure_ascii=False, indent=4).encode('utf-8'))
            return

        self.send_response(404); self.send_header('Content-type', 'application/json'); self.end_headers()
        self.wfile.write(json.dumps({"mesaj": "Gecersiz endpoint"}).encode('utf-8'))
        return

    def _handle_post(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        if path == '/dosya_yukle_islem':
            content_length = int(self.headers.get('Content-Length', 0))
            boundary = self.headers.get('Content-Type', '').split("=")[-1].encode()
            body = self.rfile.read(content_length)
            
            file_content = ""
            app_name = "Bilinmeyen"
            
            for part in body.split(boundary):
                if b'name="app"' in part:
                    try: app_name = part.split(b'\r\n\r\n')[1].split(b'\r\n')[0].decode('utf-8')
                    except Exception: pass
                elif b'name="dosya"' in part and b'filename' in part:
                    try: file_content = part.split(b'\r\n\r\n')[1].rsplit(b'\r\n', 1)[0].decode('utf-8', errors='ignore')
                    except Exception: pass
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            if file_content:
                raw_nums = re.split(r'[,\s\n]+', file_content)
                valid_nums = [re.sub(r"\D", "", n) for n in raw_nums if 8 <= len(re.sub(r"\D", "", n)) <= 15]
                eklenen = 0
                for num in valid_nums:
                    ulke = numara_ulke_bul(num)
                    stok_id = redis_req("INCR", "stok_sayaci")
                    if isinstance(stok_id, dict) and "error" in stok_id:
                        self.wfile.write(f"<h2 style='color:red;'>Hata: {stok_id['error']}</h2>".encode('utf-8')); return
                    redis_req("SET", f"stok:{stok_id}", json.dumps({"id": stok_id, "number": num, "platform": app_name, "country": ulke}))
                    eklenen += 1
                self.wfile.write(f"<h2 style='color:green;'>✅ {eklenen} numara eklendi.</h2><br><a href='/admin?key={ADMIN_KEY}'>🔙 Geri Dön</a>".encode('utf-8'))
            else:
                self.wfile.write(f"<h2 style='color:red;'>❌ Dosya okunamadı veya boş.</h2><br><a href='/admin?key={ADMIN_KEY}'>🔙 Geri Dön</a>".encode('utf-8'))
            return
