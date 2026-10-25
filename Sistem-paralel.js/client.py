import socket
import time
import json
import random
from datetime import datetime

print("Simulasi Perangkat IoT Aktif...")

while True:
    try:
        # Membuat koneksi baru ke Server Socket TCP
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 6001))

        # Simulasi pembacaan data sensor acak
        payload = {
            "suhu": round(random.uniform(25.0, 34.0), 1),
            "kelembapan": round(random.uniform(60.0, 85.0), 1),
            "waktu": datetime.now().strftime("%H:%M:%S")
        }

        # Mengirim data dalam bentuk JSON String
        client_socket.send(json.dumps(payload).encode('utf-8'))
        print(f"Data terkirim -> Suhu: {payload['suhu']}°C, Kelembapan: {payload['kelembapan']}%")
        
        client_socket.close()
    except Exception as e:
        print("Gagal mengirim data, mencoba kembali...", e)
        
    time.sleep(2) # Kirim data secara periodik setiap 2 detik
