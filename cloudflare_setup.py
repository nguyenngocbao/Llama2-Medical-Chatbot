import argparse

# Import các thư viện cần thiết
import atexit
import requests
import subprocess
import time
import re
import os
from random import randint
from threading import Timer
from queue import Queue

# Tạo và cấu hình argparse
parser = argparse.ArgumentParser(description="Run Cloudflare Setup")
parser.add_argument("port", type=int, help="Port number (e.g., 8080)")
args = parser.parse_args()

# Hàm cloudflared
def cloudflared(port, metrics_port, output_queue):
    atexit.register(
        lambda p: p.terminate(),
        subprocess.Popen(
            [
                '/content/cloudflared-linux-amd64',
                'tunnel',
                '--url',
                f'http://127.0.0.1:{port}',
                '--metrics',
                f'127.0.0.1:{metrics_port}',
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        ),
    )
    attempts, tunnel_url = 0, None
    while attempts < 10 and not tunnel_url:
        attempts += 1
        time.sleep(3)
        try:
            tunnel_url = re.search(
                "(?P<url>https?:\/\/[^\s]+.trycloudflare.com)",
                requests.get(f'http://127.0.0.1:{metrics_port}/metrics').text,
            ).group("url")
        except:
            pass
    if not tunnel_url:
        raise Exception("Can't connect to Cloudflare Edge")
    output_queue.put(tunnel_url)

# Khởi tạo Queue và metrics_port
output_queue, metrics_port = Queue(), randint(8000, 9000)

# Sử dụng tham số port truyền vào từ dòng lệnh
port = args.port

# Tạo Timer và khởi động cloudflared với port
thread = Timer(2, cloudflared, args=(port, metrics_port, output_queue))
thread.start()
thread.join()
tunnel_url = output_queue.get()

# Thiết lập biến môi trường 'webui_url' và in ra
os.environ['webui_url'] = tunnel_url
print(tunnel_url)
