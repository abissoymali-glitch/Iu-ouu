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
from concurrent.futures import ThreadPoolExecutor
import secrets
import time

# YENİ VERİTABANI BİLGİLERİ
NEW_KV_URL = "https://suited-monitor-196412.upstash.io"
NEW_KV_TOKEN = "gQAAAAAAAv88AAIgcDFhNDIzOWMyMjE0NTg0ZTI5YmY0OWEyYzU4YTZlN2IzNw"

def get_kv_creds():
    return NEW_KV_URL, NEW_KV_TOKEN

def redis_pipeline(commands):
    url, token = get_kv_creds()
    if not url or not token:
        return {"error": "Redis bağlantı bilgileri eksik!"}
    try:
        data = json.dumps(commands).encode('utf-8')
        req = urllib.request.Request(url + "/pipeline", data=data, headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {"error": f"Pipeline Hatası: {str(e)}"}

def redis_req(*args):
    url, token = get_kv_creds()
    if not url or not token:
        return {"error": "Redis bağlantı bilgileri eksik!"}
    try:
        data = json.dumps(args).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode('utf-8'))
            if isinstance(res, dict) and 'error' in res: return {"error": f"Redis Hatası: {res['error']}"}
            return res.get('result')
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        return {"error": f"Upstash Hatası: {err_body}"}
    except Exception as e:
        return {"error": f"Bağlantı Hatası: {str(e)}"}

def get_all_stock_keys():
    keys = []
    cursor = "0"
    while True:
        res = redis_req("SCAN", cursor, "MATCH", "stok:*", "COUNT", "10000")
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
API_URL_1 = "http://194.238.28.236:8000/container"
API_URL_2 = "https://numberpanel.tech/api/otp?count=200"

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
    numara = re.sub(r"\D", "", str(numara))
    for uzunluk in [3, 2, 1]:
        prefix = numara[:uzunluk]
        if prefix in ULKE_KODLARI:
            return ULKE_KODLARI[prefix]
    return "Bilinmeyen Ülke"

def fetch_source_codes_1():
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(API_URL_1, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8, context=ctx) as response:
            data = response.read().decode('utf-8')
            parsed_data = json.loads(data)
            return parsed_data if isinstance(parsed_data, list) else []
    except Exception:
        return []

def fetch_source_codes_2():
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(API_URL_2, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            if isinstance(data, list): return data
            elif isinstance(data, dict) and "otps" in data: return data["otps"]
            return []
    except Exception:
        return []

def clean_code_item(item):
    if isinstance(item, dict) and 'number' in item:
        return {
            'number': str(item.get('number', '')),
            'otp': str(item.get('otp') or item.get('code') or item.get('otp_code') or 'Yok'),
            'platform': str(item.get('platform') or item.get('service') or item.get('app') or 'Bilinmeyen'),
            'time': item.get('time') or item.get('date') or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'sms': item.get('sms') or item.get('message') or '',
            'country': item.get('country') or numara_ulke_bul(item.get('number', ''))
        }
    elif isinstance(item, list) and len(item) >= 2:
        try:
            num, otp = str(item[0]), str(item[1])
            platform = str(item[2]) if len(item) > 2 else 'Bilinmeyen'
            time_str = str(item[3]) if len(item) > 3 else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try: datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            except: time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return {'number': num, 'otp': otp, 'platform': platform, 'time': time_str, 'sms': f"{otp} kodu {platform} için.", 'country': numara_ulke_bul(num)}
        except Exception: return None
    return None

def save_codes_to_redis(codes):
    commands = []
    for item in codes[:50]:
        key = f"canli_kod:{item['number']}:{item['otp']}:{item['time']}"
        commands.append(["SET", key, json.dumps(item), "EX", 600])
    if commands: redis_pipeline(commands)

def get_cached_codes_from_redis():
    keys = []
    cursor = "0"
    while True:
        res = redis_req("SCAN", cursor, "MATCH", "canli_kod:*", "COUNT", "10000")
        if isinstance(res, dict) and "error" in res: return []
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

def fetch_and_cache_codes():
    codes1, codes2 = [], []
    with ThreadPoolExecutor(max_workers=2) as executor:
        f1, f2 = executor.submit(fetch_source_codes_1), executor.submit(fetch_source_codes_2)
        try: codes1 = f1.result(timeout=10)
        except Exception: pass
        try: codes2 = f2.result(timeout=10)
        except Exception: pass
    
    all_codes = []
    for item in codes1 + codes2:
        cleaned = clean_code_item(item)
        if cleaned: all_codes.append(cleaned)
    
    if all_codes: save_codes_to_redis(all_codes)
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
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200); self.end_headers()

    def do_GET(self):
        try: self._handle_get()
        except Exception as e:
            self.send_response(500); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
            self.wfile.write(f"<h2>Hata!</h2><pre>{traceback.format_exc()}</pre>".encode('utf-8'))

    def do_POST(self):
        try: self._handle_post()
        except Exception as e:
            self.send_response(500); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
            self.wfile.write(f"<h2>Hata!</h2><pre>{traceback.format_exc()}</pre>".encode('utf-8'))

    def _handle_get(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path, query = parsed_path.path, urllib.parse.parse_qs(parsed_path.query)
        key = query.get('key', [''])[0]

        if path.startswith('/admin'):
            if key != ADMIN_KEY:
                self.send_response(401)
                self.wfile.write(json.dumps({"hata": "Yetkisiz Erişim! Admin şifresi yanlış."}).encode('utf-8'))
                return
        elif path not in ['/favicon.ico', '/', '/api/index']:
            if not key:
                self.send_response(401)
                self.wfile.write(json.dumps({"hata": "Ücretsiz API kapatılmıştır. Lütfen geçerli bir key kullanın."}).encode('utf-8'))
                return
            
            # KEY İSTEK SAYACI
            try: redis_req("INCR", f"api_req_sayaci:{key}")
            except: pass
            try: redis_req("INCR", "api_kullanim_sayaci")
            except: pass

            key_data_str = redis_req("GET", f"api_key:{key}")
            if not key_data_str:
                self.send_response(401)
                self.wfile.write(json.dumps({"hata": "Geçersiz veya süresi dolmuş key."}).encode('utf-8'))
                return

        if path == '/favicon.ico':
            self.send_response(200); self.send_header('Content-Type', 'image/x-icon'); self.end_headers(); return

        if path == '/' or path == '/api/index':
            self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
            html = """
            <!DOCTYPE html>
            <html lang="tr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Yxce OTP API</title>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }
                    body {
                        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                        color: #fff;
                        min-height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        padding: 20px;
                    }
                    .container {
                        background: rgba(255, 255, 255, 0.05);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        border-radius: 20px;
                        padding: 40px;
                        max-width: 900px;
                        width: 100%;
                        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
                        animation: fadeIn 1s ease-in-out;
                    }
                    @keyframes fadeIn {
                        from { opacity: 0; transform: translateY(-20px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                    h1 {
                        text-align: center;
                        font-size: 2.5rem;
                        font-weight: 800;
                        background: -webkit-linear-gradient(45deg, #00c6ff, #0072ff);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        margin-bottom: 10px;
                    }
                    .subtitle {
                        text-align: center;
                        color: #aaa;
                        margin-bottom: 30px;
                        font-size: 0.9rem;
                    }
                    .endpoint-card {
                        background: rgba(255, 255, 255, 0.03);
                        border-radius: 12px;
                        padding: 20px;
                        margin-bottom: 15px;
                        transition: transform 0.3s ease, background 0.3s ease;
                    }
                    .endpoint-card:hover {
                        transform: translateX(10px);
                        background: rgba(255, 255, 255, 0.08);
                    }
                    .endpoint-title {
                        color: #00c6ff;
                        font-size: 1.1rem;
                        font-weight: 600;
                        margin-bottom: 8px;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    }
                    code {
                        background: #121212;
                        color: #2ecc71;
                        padding: 12px;
                        border-radius: 8px;
                        display: block;
                        font-family: 'Courier New', monospace;
                        font-size: 0.9rem;
                        word-break: break-all;
                        border-left: 4px solid #00c6ff;
                    }
                    .footer {
                        text-align: center;
                        margin-top: 30px;
                        color: #666;
                        font-size: 0.8rem;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 Yxce OTP API</h1>
                    <p class="subtitle">Sistem aktif ve çalışıyor. Kullanmak için geçerli bir key gereklidir.</p>

                    <div class="endpoint-card">
                        <div class="endpoint-title">🔥 1. Canlı Trafik</div>
                        <code>GET /live_trafik?key=KEYINIZ</code>
                    </div>
                    <div class="endpoint-card">
                        <div class="endpoint-title">🔍 2. Kod Sorgulama</div>
                        <code>GET /kod_sorgula?key=KEYINIZ&numara=905551234567,905551234568</code>
                    </div>
                    <div class="endpoint-card">
                        <div class="endpoint-title">📞 3. Numara Alma</div>
                        <code>GET /numara_al?key=KEYINIZ&app=WhatsApp&country=Türkiye&adet=5</code>
                    </div>
                    <div class="endpoint-card">
                        <div class="endpoint-title">📊 4. Stok Durumu</div>
                        <code>GET /stok_durumu?key=KEYINIZ</code>
                    </div>
                    <div class="endpoint-card">
                        <div class="endpoint-title">📩 5. En Son Düşen 10 Kod</div>
                        <code>GET /kod_cek?key=KEYINIZ</code>
                    </div>

                    <p class="footer">Yxce OTP API © 2026 | Gelişmiş Güvenlik ve Altyapı</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8')); return

        if path == '/live_trafik':
            self.send_response(200); self.send_header('Content-type', 'application/json; charset=utf-8'); self.end_headers()
            fetch_and_cache_codes()
            codes = get_cached_codes_from_redis()[:100]
            trafik_sayaci = {}
            for item in codes:
                platform = str(item.get('platform', 'Bilinmeyen')).capitalize()
                ulke = numara_ulke_bul(item.get('number', ''))
                if ulke == "Bilinmeyen Ülke": continue
                key_str = f"{ulke} - {platform}"
                if key_str not in trafik_sayaci: trafik_sayaci[key_str] = 0
                trafik_sayaci[key_str] += 1
            
            sirali_trafik = dict(sorted(trafik_sayaci.items(), key=lambda x: x[1], reverse=True)[:3])
            self.wfile.write(json.dumps({"en_aktif_3_trafik": sirali_trafik}, ensure_ascii=False, indent=4).encode('utf-8'))
            return

        if path == '/kod_sorgula':
            self.send_response(200); self.send_header('Content-type', 'application/json; charset=utf-8'); self.end_headers()
            aranan_numaralar_str = query.get('numara', [''])[0]
            if not aranan_numaralar_str:
                self.wfile.write(json.dumps({"hata": "Numara belirtilmedi."}, ensure_ascii=False).encode('utf-8')); return
            
            numaralar = [re.sub(r"\D", "", n) for n in aranan_numaralar_str.split(',') if re.sub(r"\D", "", n)]
            if len(numaralar) > 10:
                self.wfile.write(json.dumps({"hata": "Aynı anda en fazla 10 numara sorgulanabilir."}, ensure_ascii=False).encode('utf-8')); return

            api_codes = fetch_and_cache_codes()
            cache_codes = get_cached_codes_from_redis()
            all_codes = api_codes + cache_codes
            
            bulunan_kodlar = {}
            for item in all_codes:
                num = re.sub(r"\D", "", str(item.get('number', '')))
                if num in numaralar and num not in bulunan_kodlar:
                    bulunan_kodlar[num] = item
            
            sonuc = {}
            for numara in numaralar:
                if numara in bulunan_kodlar:
                    sonuc[numara] = {"durum": "basarili", "veri": bulunan_kodlar[numara]}
                else:
                    sonuc[numara] = {"durum": "basarisiz", "mesaj": "Bu numaraya ait kod bulunamadi."}
            
            self.wfile.write(json.dumps(sonuc, ensure_ascii=False, indent=4).encode('utf-8'))
            return

        if path == '/admin':
            self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
            kullanim_raw = redis_req("GET", "api_kullanim_sayaci")
            try: kullanim_sayisi = int(kullanim_raw) if kullanim_raw and not isinstance(kullanim_raw, dict) else 0
            except: kullanim_sayisi = 0
            
            html = f"""
            <html><head><title>OTP Admin Panel</title><meta charset="utf-8"></head>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #1e1e1e; color: #fff;">
                <h2>🛠️ Admin Panel</h2>
                <div style="background: #2a2a2a; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    <h3 style="margin: 0; color: #f1c40f;">📈 Toplam API Kullanımı: {kullanim_sayisi} kez</h3>
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
            self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
            islem = query.get('islem', [''])[0]
            
            if islem == "listele":
                stocks = get_formatted_stocks()
                html = f"<h2>📋 Stok Listesi</h2><ul>"
                
                # DÜZELTME BURADA: Eğer stocks bir sözlük değilse hata mesajı göster.
                if not isinstance(stocks, dict):
                    html += f"<li><b>Redis Hatası:</b> {stocks}</li>"
                else:
                    for app, countries in stocks.items():
                        if not isinstance(countries, dict): continue
                        html += f"<li><b>{app}</b><ul>"
                        for c, count in countries.items(): 
                            html += f"<li>{c}: {count} numara</li>"
                        html += "</ul></li>"
                        
                html += f"</ul><br><a href='/admin?key={key}' style='color: #3498db;'>🔙 Geri Dön</a>"
                self.wfile.write(html.encode('utf-8')); return
                
            elif islem == "sil":
                keys = get_all_stock_keys()
                if keys:
                    commands = [["DEL", k] for k in keys]
                    redis_pipeline(commands)
                self.wfile.write(f"<h2>🗑️ Tüm Stoklar Silindi!</h2><br><a href='/admin?key={key}' style='color: #3498db;'>🔙 Geri Dön</a>".encode('utf-8')); return
                
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
                self.wfile.write(html.encode('utf-8')); return
                
            elif islem == "key_listele":
                keys = redis_req("SCAN", "0", "MATCH", "api_key:*", "COUNT", "1000")
                key_list = keys[1] if keys and len(keys) > 1 else []
                html = "<h2>🔑 Key Listesi ve İstek Sayıları</h2><ul>"
                for k in key_list:
                    k_val = redis_req("GET", k)
                    k_name = k.replace('api_key:', '')
                    req_count_raw = redis_req("GET", f"api_req_sayaci:{k_name}")
                    try: req_count = int(req_count_raw) if req_count_raw and not isinstance(req_count_raw, dict) else 0
                    except: req_count = 0
                    
                    if k_val:
                        try:
                            data = json.loads(k_val)
                            html += f"<li><b>{k_name}</b> - İstek: {req_count} - Bitiş: {data.get('bitis', 'Bilinmiyor')} <a href='/admin_islem?islem=key_sil&key={key}&hedef={k_name}'>[SİL]</a></li>"
                        except Exception: pass
                html += f"</ul><br><a href='/admin?key={key}'>🔙 Geri Dön</a>"
                self.wfile.write(html.encode('utf-8')); return
                
            elif islem == "key_sil":
                hedef = query.get('hedef', [''])[0]
                if hedef:
                    redis_req("DEL", f"api_key:{hedef}")
                    redis_req("DEL", f"api_req_sayaci:{hedef}")
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
                saat = int(query.get('saat', ['0'])[0]); gun = int(query.get('gun', ['0'])[0]); ay = int(query.get('ay', ['0'])[0])
                yeni_key = secrets.token_hex(16)
                toplam_saniye = (saat * 3600) + (gun * 86400) + (ay * 2592000)
                if toplam_saniye <= 0:
                    self.wfile.write(f"<h2 style='color:red;'>Hata: Geçerli bir süre girin!</h2><br><a href='/admin?key={key}'>🔙 Geri Dön</a>".encode('utf-8')); return
                bitis = (datetime.now() + timedelta(seconds=toplam_saniye)).strftime("%Y-%m-%d %H:%M:%S")
                redis_req("SET", f"api_key:{yeni_key}", json.dumps({"sure": toplam_saniye, "bitis": bitis}))
                self.wfile.write(f"<h2 style='color:green;'>✅ Key Oluşturuldu!</h2><p><b>KEY: {yeni_key}</b></p><br><a href='/admin_islem?islem=key_listele&key={key}'>🔙 Listeye Dön</a>".encode('utf-8')); return

        if path == '/stok_durumu':
            self.send_response(200); self.send_header('Content-type', 'application/json; charset=utf-8'); self.end_headers()
            self.wfile.write(json.dumps(get_formatted_stocks(), ensure_ascii=False, indent=4).encode('utf-8')); return

        if path == '/numara_al':
            self.send_response(200); self.send_header('Content-type', 'application/json; charset=utf-8'); self.end_headers()
            app, country = query.get('app', [''])[0], query.get('country', [''])[0]
            count = int(query.get('adet', ['1'])[0])
            if count > 20: count = 20
            if not app or not country:
                self.wfile.write(json.dumps({"hata": "Uygulama ve ülke belirtmelisiniz."}, ensure_ascii=False).encode('utf-8')); return
            
            keys = get_all_stock_keys()
            matching_keys = []
            for i in range(0, len(keys), 500):
                vals = redis_req("MGET", *keys[i:i+500])
                if vals and isinstance(vals, list):
                    for idx, val in enumerate(vals):
                        if val:
                            data = json.loads(val)
                            if data.get('platform', '').lower() == app.lower() and data.get('country', '').lower() == country.lower():
                                matching_keys.append(keys[i+idx])

            if not matching_keys:
                self.wfile.write(json.dumps({"hata": "Stok bulunamadı."}, ensure_ascii=False).encode('utf-8')); return
            if len(matching_keys) < count: count = len(matching_keys)
            
            selected_keys = matching_keys[:count]
            selected_vals = redis_req("MGET", *selected_keys)
            
            numaralar, keys_to_delete = [], []
            if selected_vals and isinstance(selected_vals, list):
                for idx, val in enumerate(selected_vals):
                    if val:
                        numaralar.append(json.loads(val)['number'])
                        keys_to_delete.append(selected_keys[idx])
                        
            if keys_to_delete: redis_pipeline([["DEL", k] for k in keys_to_delete])
            
            self.wfile.write(json.dumps({"durum": "basarili", "verilen_adet": len(numaralar), "numaralar": numaralar}, ensure_ascii=False, indent=4).encode('utf-8'))
            return

        if path == '/kod_cek':
            self.send_response(200); self.send_header('Content-type', 'application/json; charset=utf-8'); self.end_headers()
            fetch_and_cache_codes()
            codes = get_cached_codes_from_redis()
            self.wfile.write(json.dumps(codes[:10], ensure_ascii=False, indent=4).encode('utf-8'))
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
                
                if not valid_nums:
                    self.wfile.write(f"<h2 style='color:red;'>❌ Geçerli numara bulunamadı.</h2><br><a href='/admin?key={ADMIN_KEY}'>🔙 Geri Dön</a>".encode('utf-8'))
                    return

                stok_id = redis_req("INCRBY", "stok_sayaci", len(valid_nums))
                if isinstance(stok_id, dict) and "error" in stok_id:
                    self.wfile.write(f"<h2 style='color:red;'>Hata: {stok_id['error']}</h2>".encode('utf-8')); return
                
                start_id = stok_id - len(valid_nums) + 1
                commands = []
                
                for i, num in enumerate(valid_nums):
                    ulke = numara_ulke_bul(num)
                    current_id = start_id + i
                    payload = json.dumps({"id": current_id, "number": num, "platform": app_name, "country": ulke})
                    commands.append(["SET", f"stok:{current_id}", payload])
                
                redis_pipeline(commands)
                
                self.wfile.write(f"<h2 style='color:green;'>✅ {len(valid_nums)} numara başarıyla eklendi.</h2><br><a href='/admin?key={ADMIN_KEY}'>🔙 Geri Dön</a>".encode('utf-8'))
            else:
                self.wfile.write(f"<h2 style='color:red;'>❌ Dosya okunamadı veya boş.</h2><br><a href='/admin?key={ADMIN_KEY}'>🔙 Geri Dön</a>".encode('utf-8'))
            return
