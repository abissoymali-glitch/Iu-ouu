from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import ssl

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # CORS izinleri (farklı yerlerden istek atılabilsin diye)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # SSL sertifika doğrulamasını atla (bazen IP adreslerinde hata verir)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            # Hedef API'ye istek at
            req = urllib.request.Request(
                "http://194.238.28.236:8000/container",
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                data = response.read().decode('utf-8')
            
            # Gelen veriyi aynen geri dön
            self.wfile.write(data.encode('utf-8'))
            
        except Exception as e:
            # Hata olursa JSON olarak dön
            error_response = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
        return
