import socket
import threading
import json
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# Memori penyimpanan data sensor terbaru (Volatile / No History)
data_sensor = {
    "suhu": 0.0,
    "kelembapan": 0.0,
    "waktu": "-"
}

# AMAN: Lock untuk mencegah tabrakan data (Race Condition) antar thread
data_lock = threading.Lock()

# Worker Thread: Menerima data dari Client Sensor via Native Socket TCP
def socket_sensor_worker():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', 6001))
    server_socket.listen(5)
    print("Socket Server Sensor TCP aktif di port 6001...")

    while True:
        try:
            client_conn, addr = server_socket.accept()
            packet = client_conn.recv(1024).decode('utf-8')
            if packet:
                payload = json.loads(packet)
                
                # AMAN: Mengunci data saat proses menulis (Thread-Safe)
                with data_lock:
                    data_sensor["suhu"] = payload["suhu"]
                    data_sensor["kelembapan"] = payload["kelembapan"]
                    data_sensor["waktu"] = payload["waktu"]
                    
            client_conn.close()
        except Exception as e:
            print("Error data socket:", e)

# Jalankan socket listener di background thread
threading.Thread(target=socket_sensor_worker, daemon=True).start()

# HTML Antarmuka Dashboard Web
HTML_DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <title>IoT Sensor Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a24; color: #fff; text-align: center; padding: 40px; }
        .container { display: flex; justify-content: center; gap: 20px; margin-top: 30px; }
        .card { background: #252538; padding: 30px; border-radius: 12px; width: 200px; box-shadow: 0 8px 16px rgba(0,0,0,0.4); }
        .value { font-size: 3rem; font-weight: bold; margin: 15px 0; }
        .suhu { color: #ff5e5e; }
        .kelembapan { color: #5effde; }
        .footer { margin-top: 30px; color: #888; }
    </style>
    <script>
        // Polling data secara real-time setiap 1 detik
        setInterval(async () => {
            // AMAN: Dibungkus try-catch agar browser tidak crash jika koneksi putus
            try {
                const res = await fetch('/api/sensor');
                if (!res.ok) throw new Error("Respons server bermasalah");
                
                const data = await res.json();
                document.getElementById('suhuVal').innerText = data.suhu + " °C";
                document.getElementById('lembabVal').innerText = data.kelembapan + " %";
                document.getElementById('waktuVal').innerText = "Update Terakhir: " + data.waktu;
            } catch (err) {
                console.warn("Gagal mengambil data dari server:", err.message);
                document.getElementById('waktuVal').innerText = "Koneksi terputus. Mencoba menghubungkan kembali...";
            }
        }, 1000);
    </script>
</head>
<body>
    <h1>🖥️ Dashboard Monitoring Sensor IoT Real-Time</h1>
    <div class="container">
        <div class="card">
            <h3>Suhu</h3>
            <div class="value suhu" id="suhuVal">0.0 °C</div>
        </div>
        <div class="card">
            <h3>Kelembapan</h3>
            <div class="value kelembapan" id="lembabVal">0.0 %</div>
        </div>
    </div>
    <p class="footer" id="waktuVal">Update Terakhir: -</p>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_DASHBOARD)

@app.route('/api/sensor')
def get_sensor():
    # AMAN: Mengunci data saat proses membaca (Thread-Safe)
    with data_lock:
        return jsonify(data_sensor)

if __name__ == '__main__':
    # OPTIMAL: debug=False mencegah Flask melakukan reload ganda yang menduplikasi thread socket
    app.run(port=5000, debug=False)
