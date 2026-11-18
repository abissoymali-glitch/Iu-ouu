from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import re
import urllib.request
import urllib.error
import ssl
from datetime import datetime, timedelta
import traceback
from concurrent.futures import ThreadPoolExecutor
import secrets

# YENİ VERİTABANI BİLGİLERİ
NEW_KV_URL = "https://prime-doberman-77444.upstash.io"
NEW_KV_TOKEN = "gQAAAAAAAS6EAAIgcDE3Y2Y3ZWQ1NjZkZGE0MmVlODY0ZjkwNmQxMDZmN2U4Mw"

def get_kv_creds():
    return NEW_KV_URL, NEW_KV_TOKEN

def redis_pipeline(commands):
    url, token = get_kv_creds()
    try:
        data = json.dumps(commands).encode('utf-8')
        req = urllib.request.Request(url + "/pipeline", data=data, headers={
            'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {"error": f"Pipeline Hatası: {str(e)}"}

def redis_req(*args):
    url, token = get_kv_creds()
    try:
        data = json.dumps(args).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={
            'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode('utf-8'))
            if isinstance(res, dict) and 'error' in res: return {"error": f"Redis Hatası: {res['error']}"}
            return res.get('result')
    except Exception as e:
        return {"error": f"Bağlantı Hatası: {str(e)}"}

ADMIN_KEY = "ziyapurna1010"
UYGULAMALAR = ["WhatsApp", "Facebook", "Instagram", "Telegram", "Bip", "Twitter", "TikTok", "Discord", "Google"]
API_URL_1 = "http://194.238.28.236:8000/container"
API_URL_2 = "https://numberpanel.tech/api/otp?count=200"

ULKE_KODLARI = {"1": "ABD/Kanada", "7": "Rusya", "20": "Mısır", "27": "Güney Afrika", "30": "Yunanistan", "31": "Hollanda", "32": "Belçika", "33": "Fransa", "34": "İspanya", "39": "İtalya", "40": "Romanya", "41": "İsviçre", "43": "Avusturya", "44": "İngiltere", "45": "Danimarka", "46": "İsveç", "47": "Norveç", "48": "Polonya", "49": "Almanya", "51": "Peru", "52": "Meksika", "54": "Arjantin", "55": "Brezilya", "56": "Şili", "57": "Kolombiya", "58": "Venezuela", "60": "Malezya", "61": "Avustralya", "62": "Endonezya", "63": "Filipinler", "64": "Yeni Zelanda", "65": "Singapur", "66": "Tayland", "81": "Japonya", "82": "Güney Kore", "84": "Vietnam", "86": "Çin", "90": "Türkiye", "91": "Hindistan", "92": "Pakistan", "93": "Afganistan", "94": "Sri Lanka", "95": "Myanmar", "98": "İran", "212": "Fas", "213": "Cezayir", "216": "Tunus", "218": "Libya", "220": "Gambiya", "221": "Senegal", "222": "Moritanya", "223": "Mali", "224": "Gine", "225": "Fildişi Sahili", "226": "Burkina Faso", "227": "Nijer", "228": "Togo", "229": "Benin", "230": "Mauritius", "231": "Liberya", "232": "Sierra Leone", "233": "Gana", "234": "Nijerya", "235": "Çad", "236": "Orta Afrika", "237": "Kamerun", "238": "Cape Verde", "239": "Sao Tome", "240": "Ekvator Ginesi", "241": "Gabon", "242": "Kongo", "243": "Demokratik Kongo", "244": "Angola", "245": "Gine-Bissau", "246": "Hint Okyanusu", "248": "Seyşeller", "249": "Sudan", "250": "Ruanda", "251": "Etiyopya", "252": "Somali", "253": "Cibuti", "254": "Kenya", "255": "Tanzanya", "256": "Uganda", "257": "Burundi", "258": "Mozambik", "260": "Zambiya", "261": "Madagaskar", "262": "Reunion", "263": "Zimbabve", "264": "Namibya", "265": "Malavi", "266": "Lesotho", "267": "Botsvana", "268": "Esvatini", "269": "Komorlar", "290": "Saint Helena", "291": "Eritre", "297": "Aruba", "298": "Faroe", "299": "Grönland", "350": "Cebelitarık", "351": "Portekiz", "352": "Lüksemburg", "353": "İrlanda", "354": "İzlanda", "355": "Arnavutluk", "356": "Malta", "357": "Kıbrıs", "358": "Finlandiya", "359": "Bulgaristan", "370": "Litvanya", "371": "Letonya", "372": "Estonya", "373": "Moldova", "374": "Ermenistan", "375": "Belarus", "376": "Andorra", "377": "Monako", "378": "San Marino", "380": "Ukrayna", "381": "Sırbistan", "382": "Karadağ", "383": "Kosova", "385": "Hırvatistan", "386": "Slovenya", "387": "Bosna-Hersek", "389": "Kuzey Makedonya", "420": "Çekya", "421": "Slovakya", "423": "Lihtenştayn", "500": "Falkland", "501": "Belize", "502": "Guatemala", "503": "El Salvador", "504": "Honduras", "505": "Nikaragua", "506": "Kosta Rika", "507": "Panama", "509": "Haiti", "590": "Guadeloupe", "591": "Bolivya", "592": "Guyana", "593": "Ekvador", "594": "Fransız Guyanası", "595": "Paraguay", "596": "Martinik", "597": "Surinam", "598": "Uruguay", "599": "Hollanda Antilleri", "670": "Doğu Timor", "672": "Norfolk", "673": "Brunei", "674": "Nauru", "675": "Papua Yeni Gine", "676": "Tonga", "677": "Solomon", "678": "Vanuatu", "679": "Fiji", "680": "Palau", "681": "Wallis", "682": "Cook", "683": "Niue", "685": "Samoa", "686": "Kiribati", "687": "Yeni Kaledonya", "688": "Tuvalu", "689": "Fransız Polinezyası", "690": "Tokelau", "691": "Mikronezya", "692": "Marshall", "850": "Kuzey Kore", "852": "Hong Kong", "853": "Makao", "855": "Kamboçya", "856": "Laos", "880": "Bangladeş", "886": "Tayvan", "960": "Maldivler", "961": "Lübnan", "962": "Ürdün", "963": "Suriye", "964": "Irak", "965": "Kuveyt", "966": "S. Arabistan", "967": "Yemen", "968": "Umman", "970": "Filistin", "971": "BAE", "972": "İsrail", "973": "Bahreyn", "974": "Katar", "975": "Bhutan", "976": "Moğolistan", "977": "Nepal", "992": "Tacikistan", "993": "Türkmenistan", "994": "Azerbaycan", "995": "Gürcistan", "996": "Kırgızistan", "998": "Özbekistan"}

def numara_ulke_bul(numara):
    numara = re.sub(r"\D", "", str(numara))
    for uzunluk in [3, 2, 1]:
        prefix = numara[:uzunluk]
        if prefix in ULKE_KODLARI: return ULKE_KODLARI[prefix]
    return "Bilinmeyen Ülke"

def get_all_stock_keys():
    keys = []
    cursor = "0"
    while True:
        res = redis_req("SCAN", cursor, "MATCH", "stok:*", "COUNT", "10000")
        if isinstance(res, dict) and "error" in res: return res
        if not res or len(res) < 2: break
        cursor = str(res[0])
        keys.extend(res[1])
        if cursor == "0": break
    return keys

def fetch_api_1():
    try:
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(API_URL_1, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8, context=ctx) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception: return []

def fetch_api_2():
    try:
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(API_URL_2, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            if isinstance(data, dict) and "otps" in data: return data["otps"]
            return data if isinstance(data, list) else []
    except Exception: return []

def clean_code_item(item):
    if isinstance(item, dict) and 'number' in item:
        return {
            'number': str(item.get('number', '')),
            'otp': str(item.get('otp') or item.get('code') or 'Yok'),
            'platform': str(item.get('platform') or item.get('service') or 'Bilinmeyen'),
            'time': item.get('time') or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'country': numara_ulke_bul(item.get('number', ''))
        }
    elif isinstance(item, list) and len(item) >= 2:
        try:
            return {
                'number': str(item[0]),
                'otp': str(item[1]),
                'platform': str(item[2]) if len(item) > 2 else 'Bilinmeyen',
                'time': str(item[3]) if len(item) > 3 else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'country': numara_ulke_bul(item[0])
            }
        except Exception: return None
    return None

def fetch_and_cache_codes():
    codes1, codes2 = [], []
    with ThreadPoolExecutor(max_workers=2) as executor:
        f1, f2 = executor.submit(fetch_api_1), executor.submit(fetch_api_2)
        try: codes1 = f1.result(timeout=10)
        except Exception: pass
        try: codes2 = f2.result(timeout=10)
        except Exception: pass
    
    all_codes = []
    for item in codes1 + codes2:
        cleaned = clean_code_item(item)
        if cleaned: all_codes.append(cleaned)
    
    if all_codes:
        commands = []
        for item in all_codes[:50]:
            key = f"canli_kod:{item['number']}:{item['otp']}:{item['time']}"
            commands.append(["SET", key, json.dumps(item), "EX", 600])
        if commands: redis_pipeline(commands)
    return all_codes

def get_cached_codes():
    keys = []
    cursor = "0"
    while True:
        res = redis_req("SCAN", cursor, "MATCH", "canli_kod:*", "COUNT", "10000")
        if not res or len(res) < 2: break
        cursor = str(res[0]); keys.extend(res[1])
        if cursor == "0": break
    if not keys: return []
    
    all_codes = []
    for i in range(0, len(keys), 500):
        vals = redis_req("MGET", *keys[i:i+500])
        if vals and isinstance(vals, list):
            for val in vals:
                if val:
                    try: all_codes.append(json.loads(val))
                    except Exception: pass
    all_codes.sort(key=lambda x: x.get('time', ''), reverse=True)
    return all_codes

def get_formatted_stocks():
    keys = get_all_stock_keys()
    if isinstance(keys, dict) and "error" in keys: return keys 
    grouped = {}
    if not keys: return grouped
    for i in range(0, len(keys), 500):
        vals = redis_req("MGET", *keys[i:i+500])
        if vals and isinstance(vals, list):
            for val in vals:
                if val:
                    try:
                        data = json.loads(val)
                        app, country = data.get('platform', 'Bilinmeyen'), data.get('country', 'Bilinmeyen')
                        if app not in grouped: grouped[app] = {}
                        if country not in grouped[app]: grouped[app][country] = 0
                        grouped[app][country] += 1
                    except Exception: pass
    return grouped

class handler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200); self.end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path, query = parsed_path.path, urllib.parse.parse_qs(parsed_path.query)
        key = query.get('key', [''])[0]

        if path.startswith('/admin'):
            if key != ADMIN_KEY:
                self.send_response(401)
                self.wfile.write(json.dumps({"hata": "Yetkisiz Erişim!"}).encode('utf-8'))
                return
        elif path not in ['/favicon.ico', '/']:
            if not key:
                self.send_response(401)
                self.wfile.write(json.dumps({"hata": "Ücretsiz API kapatılmıştır. Key gereklidir."}).encode('utf-8'))
                return
            key_data_str = redis_req("GET", f"api_key:{key}")
            if not key_data_str:
                self.send_response(401)
                self.wfile.write(json.dumps({"hata": "Geçersiz veya süresi dolmuş key."}).encode('utf-8'))
                return

        if path == '/favicon.ico':
            self.send_response(200); self.end_headers(); return

        if path == '/' or path == '/api/index':
            self.send_response(200)
            html = "<html><body style='font-family: Arial; background: #121212; color: #e0e0e0; padding: 30px;'><h1 style='color: #2ecc71;'>Yxce OTP API</h1><p>Sistem aktif. Kullanmak için key gereklidir.</p></body></html>"
            self.wfile.write(html.encode('utf-8')); return

        if path == '/kod_cek':
            fetch_and_cache_codes()
            codes = get_cached_codes()
            self.wfile.write(json.dumps(codes[:10], ensure_ascii=False, indent=4).encode('utf-8')); return

        if path == '/kod_sorgula':
            aranan = query.get('numara', [''])[0]
            if not aranan:
                self.wfile.write(json.dumps({"hata": "Numara belirtilmedi."}).encode('utf-8')); return
            
            numaralar = [re.sub(r"\D", "", n) for n in aranan.split(',') if re.sub(r"\D", "", n)]
            fetch_and_cache_codes()
            codes = get_cached_codes()
            
            bulunanlar = {}
            for item in codes:
                num = re.sub(r"\D", "", str(item.get('number', '')))
                if num in numaralar and num not in bulunanlar:
                    bulunanlar[num] = item
            
            sonuc = {}
            for num in numaralar:
                sonuc[num] = {"durum": "basarili", "veri": bulunanlar[num]} if num in bulunanlar else {"durum": "basarisiz", "mesaj": "Kod bulunamadı."}
            self.wfile.write(json.dumps(sonuc, ensure_ascii=False, indent=4).encode('utf-8')); return

        if path == '/live_trafik':
            fetch_and_cache_codes()
            codes = get_cached_codes()[:50] 
            
            trafik = {}
            for item in codes:
                ulke = numara_ulke_bul(item.get('number', ''))
                platform = str(item.get('platform', 'Bilinmeyen')).capitalize()
                key_str = f"{ulke} - {platform}"
                trafik[key_str] = trafik.get(key_str, 0) + 1
            
            en_iyi_3 = dict(sorted(trafik.items(), key=lambda x: x[1], reverse=True)[:3])
            self.wfile.write(json.dumps({"en_aktif_3_trafik": en_iyi_3}, ensure_ascii=False, indent=4).encode('utf-8')); return

        if path == '/stok_durumu':
            self.wfile.write(json.dumps(get_formatted_stocks(), ensure_ascii=False, indent=4).encode('utf-8')); return

        if path == '/numara_al':
            app, country = query.get('app', [''])[0], query.get('country', [''])[0]
            count = int(query.get('adet', ['1'])[0])
            if count > 20: count = 20
            if not app or not country: self.wfile.write(json.dumps({"hata": "Uygulama ve ülke belirtmelisiniz."}).encode('utf-8')); return
            
            keys = get_all_stock_keys()
            matching = []
            for i in range(0, len(keys), 500):
                vals = redis_req("MGET", *keys[i:i+500])
                if vals and isinstance(vals, list):
                    for idx, val in enumerate(vals):
                        if val:
                            data = json.loads(val)
                            if data.get('platform', '').lower() == app.lower() and data.get('country', '').lower() == country.lower():
                                matching.append(keys[i+idx])
                                
            if not matching: self.wfile.write(json.dumps({"hata": "Stok bulunamadı."}).encode('utf-8')); return
            if len(matching) < count: count = len(matching)
            
            secilenler = matching[:count]
            selected_vals = redis_req("MGET", *secilenler)
            numaralar, silinecekler = [], []
            if selected_vals and isinstance(selected_vals, list):
                for idx, val in enumerate(selected_vals):
                    if val:
                        numaralar.append(json.loads(val)['number'])
                        silinecekler.append(secilenler[idx])
            if silinecekler: redis_pipeline([["DEL", k] for k in silinecekler])
            self.wfile.write(json.dumps({"durum": "basarili", "verilen_adet": len(numaralar), "numaralar": numaralar}, ensure_ascii=False, indent=4).encode('utf-8')); return

        if path == '/admin':
            kullanim = redis_req("GET", "api_kullanim_sayaci") or 0
            html = f"""
            <html><head><title>Admin Panel</title><meta charset="utf-8"></head>
            <body style="font-family: Arial; padding: 20px; background-color: #1e1e1e; color: #fff;">
                <h2>🛠️ Yxce Admin Panel</h2>
                <div style="background: #2a2a2a; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    <h3 style="margin: 0; color: #f1c40f;">📈 Toplam API Kullanımı: {kullanim} kez</h3>
                </div>
                <form action="/admin_islem" method="GET">
                    <input type="hidden" name="key" value="{key}">
                    <button type="submit" name="islem" value="listele" style="padding: 10px; margin: 5px; background: #3498db; color: white; border: none; border-radius: 5px;">📋 Stok Listesi</button>
                    <button type="submit" name="islem" value="ekle_sayfa" style="padding: 10px; margin: 5px; background: #2ecc71; color: white; border: none; border-radius: 5px;">➕ Stok Ekle</button>
                    <button type="submit" name="islem" value="sil" style="padding: 10px; margin: 5px; background: #e74c3c; color: white; border: none; border-radius: 5px;">🗑️ Tüm Stokları Sil</button>
                    <hr style="margin: 20px 0; border-color: #333;">
                    <button type="submit" name="islem" value="key_listele" style="padding: 10px; margin: 5px; background: #9b59b6; color: white; border: none; border-radius: 5px;">🔑 Key Listesini Gör</button>
                    <button type="submit" name="islem" value="key_olustur_sayfa" style="padding: 10px; margin: 5px; background: #e67e22; color: white; border: none; border-radius: 5px;">➕ Yeni Key Oluştur</button>
                </form>
            </body></html>
            """
            self.wfile.write(html.encode('utf-8')); return

        if path == '/admin_islem':
            islem = query.get('islem', [''])[0]
            
            if islem == "listele":
                stocks = get_formatted_stocks()
                html = "<h2>📋 Stok Listesi</h2><ul>"
                for app, countries in stocks.items():
                    html += f"<li><b>{app}</b><ul>"
                    for c, count in countries.items(): html += f"<li>{c}: {count} numara</li>"
                    html += "</ul></li>"
                html += f"</ul><br><a href='/admin?key={key}' style='color: #3498db;'>🔙 Geri Dön</a>"
                self.wfile.write(html.encode('utf-8')); return
                
            elif islem == "sil":
                keys = get_all_stock_keys()
                if keys: redis_pipeline([["DEL", k] for k in keys])
                self.wfile.write(f"<h2>🗑️ Tüm Stoklar Silindi!</h2><br><a href='/admin?key={key}' style='color: #3498db;'>🔙 Geri Dön</a>".encode('utf-8')); return
                
            elif islem == "ekle_sayfa":
                html = f"<html><body style='background: #1e1e1e; color: #fff; padding: 20px;'><h2>➕ Stok Ekle</h2><form action='/dosya_yukle_islem' method='POST' enctype='multipart/form-data'><input type='hidden' name='key' value='{key}'><select name='app'>"
                for u in UYGULAMALAR: html += f"<option value='{u}'>{u}</option>"
                html += f"</select><br><br><input type='file' name='dosya' accept='.txt'><br><br><button type='submit'>Yükle</button></form><br><a href='/admin?key={key}'>🔙 Geri Dön</a></body></html>"
                self.wfile.write(html.encode('utf-8')); return
                
            elif islem == "key_listele":
                keys = redis_req("SCAN", "0", "MATCH", "api_key:*", "COUNT", "1000")
                key_list = keys[1] if keys and len(keys) > 1 else []
                html = "<h2>🔑 Key Listesi</h2><ul>"
                for k in key_list:
                    k_val = redis_req("GET", k)
                    if k_val:
                        try:
                            data = json.loads(k_val)
                            html += f"<li><b>{k.replace('api_key:', '')}</b> - Bitiş: {data.get('bitis', 'Bilinmiyor')} <a href='/admin_islem?islem=key_sil&key={key}&hedef={k.replace('api_key:', '')}'>[SİL]</a></li>"
                        except Exception: pass
                html += f"</ul><br><a href='/admin?key={key}'>🔙 Geri Dön</a>"
                self.wfile.write(html.encode('utf-8')); return
                
            elif islem == "key_sil":
                hedef = query.get('hedef', [''])[0]
                if hedef:
                    redis_req("DEL", f"api_key:{hedef}")
                    self.wfile.write(f"<h2>🗑️ Key Silindi!</h2><br><a href='/admin_islem?islem=key_listele&key={key}'>🔙 Geri Dön</a>".encode('utf-8'))
                return
                
            elif islem == "key_olustur_sayfa":
                html = f"""
                <html><body style='background: #1e1e1e; color: #fff; padding: 20px;'>
                <h2>➕ Yeni Key Oluştur</h2>
                <form action="/admin_islem" method="GET">
                    <input type="hidden" name="key" value="{key}">
                    <input type="hidden" name="islem" value="key_olustur">
                    <label>Saat:</label> <input type="number" name="saat" value="0" style="width: 50px;">
                    <label>Gün:</label> <input type="number" name="gun" value="0" style="width: 50px;">
                    <label>Ay:</label> <input type="number" name="ay" value="0" style="width: 50px;"><br><br>
                    <button type="submit" style="padding: 10px 20px; background: #2ecc71; color: white; border: none; border-radius: 5px;">Oluştur</button>
                </form>
                <br><a href='/admin?key={key}'>🔙 Geri Dön</a></body></html>
                """
                self.wfile.write(html.encode('utf-8')); return
                
            elif islem == "key_olustur":
                saat = int(query.get('saat', ['0'])[0])
                gun = int(query.get('gun', ['0'])[0])
                ay = int(query.get('ay', ['0'])[0])
                
                yeni_key = secrets.token_hex(16)
                toplam_saniye = (saat * 3600) + (gun * 86400) + (ay * 2592000)
                
                if toplam_saniye <= 0:
                    self.wfile.write(f"<h2 style='color:red;'>Hata: Geçerli bir süre girin!</h2><br><a href='/admin?key={key}'>🔙 Geri Dön</a>".encode('utf-8')); return
                    
                bitis = (datetime.now() + timedelta(seconds=toplam_saniye)).strftime("%Y-%m-%d %H:%M:%S")
                redis_req("SET", f"api_key:{yeni_key}", json.dumps({"sure": toplam_saniye, "bitis": bitis}))
                
                self.wfile.write(f"<h2 style='color:green;'>✅ Key Oluşturuldu!</h2><p><b>KEY: {yeni_key}</b></p><br><a href='/admin_islem?islem=key_listele&key={key}'>🔙 Listeye Dön</a>".encode('utf-8')); return

    def _handle_post(self):
        path = urllib.parse.urlparse(self.path).path
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
            if file_content:
                raw_nums = re.split(r'[,\s\n]+', file_content)
                valid_nums = [re.sub(r"\D", "", n) for n in raw_nums if 8 <= len(re.sub(r"\D", "", n)) <= 15]
                if valid_nums:
                    stok_id = redis_req("INCRBY", "stok_sayaci", len(valid_nums))
                    start_id = stok_id - len(valid_nums) + 1
                    commands = []
                    for i, num in enumerate(valid_nums):
                        ulke = numara_ulke_bul(num)
                        payload = json.dumps({"id": start_id + i, "number": num, "platform": app_name, "country": ulke})
                        commands.append(["SET", f"stok:{start_id + i}", payload])
                    redis_pipeline(commands)
                    self.wfile.write(f"<h2 style='color:green;'>✅ {len(valid_nums)} numara eklendi.</h2><br><a href='/admin?key={ADMIN_KEY}'>🔙 Geri Dön</a>".encode('utf-8'))
                    return
            self.wfile.write(f"<h2 style='color:red;'>❌ Dosya okunamadı veya boş.</h2><br><a href='/admin?key={ADMIN_KEY}'>🔙 Geri Dön</a>".encode('utf-8'))
