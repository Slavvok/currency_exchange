from http.server import HTTPServer, BaseHTTPRequestHandler, HTTPStatus
import json
import settings
import sys
from datetime import datetime
from urllib.request import urlopen
from urllib.error import HTTPError


class CurrencyExchangeHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code, message=None):
        self.send_response(code)
        if message:
            self.log_message(message)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def _send_error_403(self):
        self._set_headers(403)
        self.wfile.write(json.dumps({"error": "Forbidden", "code": 403,
                                     "message": "Currently base currency could be only usd"}).encode())

    def _send_error_405(self):
        self._set_headers(405)
        self.wfile.write(json.dumps({"error": "Method not allowed", "code": 405}).encode())

    def _send_error_500(self, message):
        self._set_headers(500)
        self.wfile.write(json.dumps({"error": "Internal server error", "code": 500,
                                     "message": message}).encode())

    def log_date_time_string(self):
        return datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")

    def log_request(self, code='-', size='-'):
        if isinstance(code, HTTPStatus):
            code = code.value
        self.log_message('%s %s %s',
                         self.requestline.split()[0], str(code), str(size))

    def log_message(self, format, *args):
        sys.stderr.write("[%s] %s %s\n" %
                         (self.log_date_time_string(),
                          self.address_string(),
                          format % args))

    def do_HEAD(self):
        self._set_headers(200)

    def do_GET(self):
        self._send_error_405()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        request = json.loads(body.decode())
        try:
            if request:
                curr_from = request['curr_from']
                curr_to = request['curr_to']
                number = float(request['number'])
                r = urlopen(settings.SERVICE_URL.format(curr_from, curr_to))
                data = json.loads(r.read().decode())
                response = dict()
                response[curr_from] = number
                response[curr_to] = float(data['rates'][curr_to.upper()]) * number
                self._set_headers(200, "%(message)s" % {"message": json.dumps(response)})
                self.wfile.write(json.dumps(response).encode())
        except HTTPError:
            self._send_error_403()


if __name__ == "__main__":
    httpd = HTTPServer((settings.DEV_HOST, settings.DEV_PORT), CurrencyExchangeHandler)
    sys.stderr.write(f"Started http server at http://{settings.DEV_HOST}:{settings.DEV_PORT}/\n")
    httpd.serve_forever()
