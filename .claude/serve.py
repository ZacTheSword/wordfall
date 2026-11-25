import http.server, os
H = http.server.SimpleHTTPRequestHandler
H.extensions_map['.html'] = 'text/html; charset=utf-8'
class Handler(H):
    def do_PUT(self):
        # test helper: save a rendered audio preview next to the game
        if self.path != '/media/rot-thaw-preview.wav':
            self.send_error(403); return
        n = int(self.headers.get('Content-Length', 0))
        with open('media/rot-thaw-preview.wav', 'wb') as f:
            f.write(self.rfile.read(n))
        self.send_response(204); self.end_headers()
http.server.test(HandlerClass=Handler, port=8765, bind='127.0.0.1')
