import io
from urllib.parse import urlparse, parse_qsl
from io import BytesIO
from http.server import HTTPServer, BaseHTTPRequestHandler
from string import Template
from time import sleep

from picamera import PiCamera

TITLE = "Live cam streamer"
CAM_WIDTH = 1280
CAM_HEIGHT = 720
PORT_NUMBER = 8080

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        o = urlparse(self.path)

        if o.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
            return
        elif o.path == '/index.html':

            tpl = Template(index_template)
            content = tpl.safe_substitute(dict(
                TITLE=TITLE))

            content = content.encode('utf-8')

            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(content))
            self.end_headers()

            if self.command == 'GET':
                self.wfile.write(content)

        elif o.path == '/live-cam.jpg':

            capture_width = CAM_WIDTH
            capture_height = CAM_HEIGHT

            try:
                qs_lst = parse_qsl(o.query)
                qs = dict()
                for param in qs_lst:
                    qs[param[0]] = param[1]
                if 'w' in qs and 'h' in qs:

                    capture_width = min(capture_width, int(qs['w']))
                    capture_height = min(capture_height, int(qs['h']))
            except:
                print('Couldn\'t parse query parameters: ' + o.query)

            self.send_response(200)
            self.send_header('Content-type', 'image/jpg')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()

            my_stream = BytesIO()
            camera.capture(my_stream, 'jpeg', resize=(capture_width, capture_height))
            my_stream.seek(0)
            self.wfile.write(my_stream.read())
            my_stream.close()

            # with open('dummy.jpg', 'rb') as file_handle:
            #     self.wfile.write(file_handle.read())

        else:
            self.send_error(404, 'File not found')
            return


with io.open('index.html', 'r') as f:
    index_template = f.read()

print('Starting camera...')
camera = PiCamera(resolution=(CAM_WIDTH, CAM_HEIGHT))
camera.start_preview()
sleep(2)
print('Camera started!')

httpd = HTTPServer(('', PORT_NUMBER), SimpleHTTPRequestHandler)
print('Started httpserver on port ', PORT_NUMBER)
httpd.serve_forever()
