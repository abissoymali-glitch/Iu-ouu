from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import ssl

# Vercel'de her istek geldiğinde kaynak API'den güncel veriyi çeker
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # CORS izinleri
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            # SSL sertifika doğrulamasını atla (IP adreslerinde bazen hata verir)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            # Kaynak API'ye istek at
            req = urllib.request.Request(
                "http://194.238.28.236:8000/container",
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                data = response.read().decode('utf-8')
                # Gelen veriyi JSON olarak ayrıştır
                parsed = json.loads(data)
                # Alt alta okunaklı (Pretty Print) formata çevir
                formatted = json.dumps(parsed, ensure_ascii=False, indent=4)
                
                self.wfile.write(formatted.encode('utf-8'))
                
        except Exception as e:
            error_response = json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)
            self.wfile.write(error_response.encode('utf-8'))
        return
