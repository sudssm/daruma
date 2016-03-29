from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import socket

class OAuthRedirectServer(object):
    def __init__(self, auth_callback, port, dropboxflow=None):
        """
        Args:
            auth_callback: a function that takes a single string parameter
                           containing the local URL path that was navigated to.
        """
        handler = self._make_response_handler(auth_callback, dropboxflow=dropboxflow)
        self.server = HTTPServer(('localhost', port), handler)
        self.server.timeout = None

    def get_url(self):
        """
        Returns a string representing the URL that the OAuth server should
        redirect to.
        """
        address = self.server.server_address
        return "http://" + address[0] + ":" + str(address[1])

    def start(self):
        try:
            self.server.handle_request()
            self.server.socket.close()
        except KeyboardInterrupt:
            print '^C received, shutting down the web server'
            self.server.socket.close()

    @staticmethod
    def _get_open_port():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("",0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        return port

    @staticmethod
    def _make_response_handler(auth_callback, dropboxflow=None):
        class handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                if dropboxflow:
                    auth_callback(self.path,dropboxflow)
                else:
                    auth_callback(self.path)
                return
        return handler


# Example usage:
# def dummy_callback(url,port):
#     print port
#     print url

# port = 51168
# s = OAuthRedirectServer(dummy_callback, port)
# print s.get_url()
# s.start()