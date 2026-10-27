"""TTW development server. Standard-library only; multiplayer will be built separately."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os

os.chdir(Path(__file__).resolve().parent)

if __name__ == "__main__":
    host, port = "0.0.0.0", 8000
    print(f"TTW development server: http://localhost:{port}")
    ThreadingHTTPServer((host, port), SimpleHTTPRequestHandler).serve_forever()
