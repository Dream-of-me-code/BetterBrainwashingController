import os
import threading
import socket
from flask import Flask, request


UPLOAD_DIR = "remote_uploads"
TOKEN = "123"

def start_network_server(ControllWindow):
    app = Flask(__name__)
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    @app.route('/upload_gif', methods=["POST"])
    def  upload_gif():
        if request.headers.get("Authorization") != TOKEN:
            print(f"Unauthorized access attempt using token: {request.headers.get('Authorization')}")
            return {"error": "Unauthorized"}, 401
        
        file = request.files.get("gif")
        if not file:
            return {"error": "No file"}, 400
        
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        file.save(save_path)

        ControllWindow.open_gif_signal.emit(os.path.abspath(save_path))

        return  {"status":  "success"}, 200
    
    def run():
        app.run(host="0.0.0.0", port=5000)

    ip = get_local_ip()
    print("\n=== Remote Media Server ===")
    print(f"listening on: http://{ip}:5000/upload_gif")
    print("=============================\n")

    threading.Thread(target=run, daemon=True).start()

def get_local_ip():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip
