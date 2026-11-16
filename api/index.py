from http.server import BaseHTTPRequestHandler
import json
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Hedef API'ye git ve güncel veriyi çek
            r = requests.get("http://194.238.28.236:8000/container", timeout=8)
            if r.status_code == 200:
                # Tıpa tıp aynısını dön
                self.wfile.write(r.content)
            else:
                self.wfile.write(json.dumps({"hata": "Kaynak API yanit vermedi"}).encode('utf-8'))
        except Exception as e:
            self.wfile.write(json.dumps({"hata": str(e)}).encode('utf-8'))
        return
