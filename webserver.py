import socket
import os
from datetime import datetime, timezone
import time
# Server configuration
HOST = '127.0.0.1'  
PORT = 8080

# Helper function to format HTTP headers
def build_http_headers(status_code, file_path=None,body=None):
    headers = []
    if status_code == 200:
        headers.append("HTTP/1.1 200 OK")
    elif status_code == 404:
        headers.append("HTTP/1.1 404 Not Found")
    else:
        headers.append("HTTP/1.1 405 Not Allowed")

    headers.append("Connection: keep-alive")
    headers.append("Date: " + datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"))
    headers.append("Server: Python/3.11.3")
    headers.append("Content-Type: " + "text/html")
    # If file exists, add file-related headers
    if file_path and os.path.exists(file_path):
        headers.append("Content-Length: " + str(os.path.getsize(file_path)))
        timestamp = os.path.getmtime(file_path)
        last_modified = datetime.fromtimestamp(timestamp, timezone.utc)
        last_modified = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers.append("Last-Modified: " + last_modified)
    elif body is not None:
        headers.append("Content-Length: " + str(len(body)))
    else:
        headers.append("Content-Length: 0")
    return "\r\n".join(headers) + "\r\n\r\n"

# Main server function
def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Listening on port:{PORT}")  
        try:
            while True:
                client_socket, client_address = server_socket.accept()
                with client_socket:
                    request = client_socket.recv(1024).decode('utf-8')
                    request_line = request.splitlines()[0]
                    method, path, _ = request_line.split()

                    # Serve GET or HEAD requests
                    if method in ('GET', 'HEAD'):
                        safe_path = os.path.normpath(path.lstrip("/"))
                        file_path = os.path.join(os.getcwd(), safe_path)
                        if os.path.exists(file_path) and os.path.isfile(file_path):
                            response_headers = build_http_headers(200, file_path)
                            client_socket.sendall(response_headers.encode('utf-8'))
                            if method == 'GET':
                                with open(file_path, 'rb') as f:
                                    html_body = f.read() 
                                    client_socket.sendall(html_body)
                        else:
                            error_body = "<html><body><h1>404 Not Found</h1></body></html>"
                            response_headers = build_http_headers(404,body=error_body)
                            client_socket.sendall(response_headers.encode('utf-8'))
                            client_socket.sendall(error_body.encode('utf-8'))

                    else:
                        # Method not allowed, send 405 response
                        error_body = "<html><body><h1>405 Method Not Allowed</h1></body></html>"
                        response_headers = build_http_headers(405,body=error_body)
                        client_socket.sendall(response_headers.encode('utf-8'))
                        client_socket.sendall(error_body.encode('utf-8'))
        except KeyboardInterrupt:
            print("Manually exited")
        finally:
            server_socket.close()
            
if __name__ == "__main__":
    run_server()