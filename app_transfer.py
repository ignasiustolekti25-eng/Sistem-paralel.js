import socket
import threading
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Penyimpanan log teks yang diterima server
log_transfer = []

# Worker Thread: Mendengarkan data teks masuk via Socket TCP
def socket_transfer_worker():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', 7001))
    server_socket.listen(5)
    print("Socket Server Transfer aktif di port 7001...")

    while True:
        try:
            client_conn, addr = server_socket.accept()
            data_mentah = client_conn.recv(2048).decode('utf-8')
            if data_mentah:
                log_transfer.append(data_mentah)
                print(f"Teks diterima dari client: {data_mentah}")
            client_conn.close()
        except Exception as e:
            print("Error socket:", e)

threading.Thread(target=socket_transfer_worker, daemon=True).start()

# HTML Antarmuka Pengiriman Data Teks
HTML_TRANSFER = """
<!DOCTYPE html>
<html>
<head>
    <title>Aplikasi Transfer Data</title>
    <style>
        body { font-family: sans-serif; padding: 40px; background: #f4f6f9; color: #333; }
        .box { background: white; max-width: 500px; margin: 0 auto; padding: 25px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        textarea { width: 95%; height: 100px; margin-bottom: 15px; padding: 10px; border: 1px solid #ccc; border-radius: 4px; resize: none; }
        button { background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 1rem; }
        button:hover { background: #218838; }
        .logs { margin-top: 25px; text-align: left; background: #e9ecef; padding: 15px; border-radius: 5px; max-height: 15px0px; overflow-y: auto; }
    </style>
    <script>
        async function kirimData() {
            const teksInput = document.getElementById('teks').value;
            if(!teksInput.trim()) return alert("Teks tidak boleh kosong!");

            // Mengirim data ke Route Flask, yang kemudian diteruskan via Socket
            const res = await fetch('/kirim-via-socket', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pesan: teksInput })
            });
            
            if(res.ok) {
                document.getElementById('teks').value = '';
                muatLog();
            }
        }

        async function muatLog() {
            const res = await fetch('/api/logs');
            const data = await res.json();
            const logBox = document.getElementById('logBox');
            logBox.innerHTML = data.map(log => `<div>▪️ ${log}</div>`).join('');
        }
        
        // Memuat log saat halaman pertama kali dibuka
        window.onload = muatLog;
    </script>
</head>
<body>
    <div class="box">
        <h2>📄 Aplikasi Transfer Data Teks</h2>
        <textarea id="teks" placeholder="Ketik data teks yang ingin dikirim ke server melalui Socket TCP..."></textarea>
        <br>
        <button onclick=kirimData()>Kirim Data</button>
        
        <h3>Log Penerimaan Server:</h3>
        <div class="logs" id="logBox"> Belum ada data.</div>
    </div>
</body>
</html>
