import os
import sys
import requests
import webbrowser
from pathlib import Path
from datetime import datetime, timedelta
from tts import bicara, bicara_dengan_bahasa
from speech_to_text import transcribe
import threading

# Load .env
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    with open(_env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
if not NEWS_API_KEY:
    print("ERROR: NEWS_API_KEY tidak ditemukan di .env")
    sys.exit(1)

def ambil_berita(jumlah=5):
    """Fetch news from NewsAPI."""
    url = "https://newsapi.org/v2/everything"
    kemarin = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    params = {
        "apiKey": NEWS_API_KEY,
        "q": "Indonesia",
        "sortBy": "publishedAt",
        "pageSize": jumlah,
        "from": kemarin
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        articles = data.get("articles", [])
        hasil = []
        for article in articles[:jumlah]:
            judul = article.get("title", "").split(" - ")[0]
            deskripsi = article.get("description", "") or ""
            link = article.get("url", "")
            if judul and judul != "[Removed]":
                hasil.append({
                    "judul": judul,
                    "deskripsi": deskripsi,
                    "link": link
                })
        return hasil
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []




def mode_interaktif(ui_queue=None):
    """Interactive news reading mode."""
    berita_list = ambil_berita()
    if not berita_list:
        bicara("Maaf Bos Rizqi, saya tidak menemukan berita terbaru saat ini.")
        return

    jumlah = len(berita_list)
    if ui_queue:
        ui_queue.put({'type': 'status', 'status': 'speaking'})
    bicara(f"Bos Rizqi, saya menemukan {jumlah} berita terbaru hari ini.")
    if ui_queue:
        ui_queue.put({'type': 'message', 'sender': 'airys', 'message': f"Bos Rizqi, saya menemukan {jumlah} berita terbaru hari ini."})
        ui_queue.put({'type': 'status', 'status': 'aktif'})

    # Announce each headline
    daftar_pesan = []
    for i, berita in enumerate(berita_list, 1):
        judul = berita['judul']
        if ui_queue:
            ui_queue.put({'type': 'status', 'status': 'speaking'})
        bicara_dengan_bahasa(f"Berita {i}. {judul}", detect_text=judul)
        if ui_queue:
            ui_queue.put({'type': 'status', 'status': 'aktif'})
        daftar_pesan.append(f"{i}. {judul}")

    if ui_queue:
        ui_queue.put({'type': 'message', 'sender': 'system', 'message': "\n".join(daftar_pesan)})

    if ui_queue:
        ui_queue.put({'type': 'status', 'status': 'speaking'})
    bicara("Bos Rizqi ingin membuka berita nomor berapa? Sebutkan saja nomornya.")
    if ui_queue:
        ui_queue.put({'type': 'message', 'sender': 'airys', 'message': "Bos Rizqi ingin membuka berita nomor berapa? Sebutkan saja nomornya."})
        ui_queue.put({'type': 'status', 'status': 'aktif'})

    print("\nDaftar Berita:")
    for i, berita in enumerate(berita_list, 1):
        print(f"{i}. {berita['judul']}")

    # Listen for choice
    print("\nMendengarkan pilihan...")
    teks_pilihan = transcribe()
    print(f"Pilihan terdeteksi: {teks_pilihan}")
    if ui_queue and teks_pilihan:
        ui_queue.put({'type': 'message', 'sender': 'user', 'message': teks_pilihan})

    # Parse number choice
    angka_map = {
        "satu": 1, "dua": 2, "tiga": 3, "empat": 4, "lima": 5,
        "enam": 6, "tujuh": 7, "delapan": 8, "sembilan": 9, "sepuluh": 10,
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
        "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
    }

    index = None
    teks_pilihan_lower = teks_pilihan.lower()
    for kata, nomor in angka_map.items():
        if kata in teks_pilihan_lower:
            index = nomor - 1
            break

    if index is None or index < 0 or index >= len(berita_list):
        bicara("Maaf Bos Rizqi, saya tidak memahami pilihan tersebut.")
        return

    berita = berita_list[index]
    deskripsi = berita["deskripsi"]
    link = berita["link"]

    if ui_queue:
        ui_queue.put({'type': 'status', 'status': 'speaking'})
    bicara("Baik Bos Rizqi. Saya buka beritanya sekarang.")
    if ui_queue:
        ui_queue.put({'type': 'message', 'sender': 'airys', 'message': "Baik Bos Rizqi. Saya buka beritanya sekarang."})
        ui_queue.put({'type': 'status', 'status': 'aktif'})
    webbrowser.open(link)

    if deskripsi:
        deskripsi = deskripsi.split("The post")[0].strip()
        if deskripsi:
            if ui_queue:
                ui_queue.put({'type': 'status', 'status': 'speaking'})
            bicara("Ringkasan singkatnya.")
            if ui_queue:
                ui_queue.put({'type': 'status', 'status': 'aktif'})
            if ui_queue:
                ui_queue.put({'type': 'status', 'status': 'speaking'})
            bicara_dengan_bahasa(deskripsi)
            if ui_queue:
                ui_queue.put({'type': 'status', 'status': 'aktif'})
