import time
import threading
import queue
import webbrowser
import re
from clap_detector import listen_for_claps
from speech_to_text import transcribe
from tts import bicara, set_visualizer_callback
from brain import proses_perintah
from executor import buka_aplikasi
from news_fetcher import mode_interaktif, ambil_berita
from airys_ui import init_ui

aktif = False
ui_queue = queue.Queue()

WAKE_KEYWORDS = [
    "airis",
    "airys",
    "aris",
    "iris",
    "ayris",
    "eyris"
]

NONAKTIF_KEYWORDS = [
    "matikan sistem",
    "matikan",
    "tidur",
    "nonaktif",
    "istirahat"
]

OPEN_KEYWORDS = ["buka", "open", "jalankan", "nyalakan"]


def sapa():
    from datetime import datetime
    from tts import briefing_pagi, briefing_siang, briefing_sore, briefing_malam

    jam = datetime.now().hour

    if jam < 11:
        briefing_pagi()
    elif jam < 15:
        briefing_siang()
    elif jam < 18:
        briefing_sore()
    else:
        briefing_malam()


def has_wake_keyword(teks_lower):
    return any(k in teks_lower for k in WAKE_KEYWORDS)


def quick_app_command(teks_lower):
    if not any(k in teks_lower for k in OPEN_KEYWORDS):
        return None

    resp = buka_aplikasi(teks_lower)
    if not resp:
        return None

    # Extract app name from response: "Chrome sudah dibuka, Bos Rizqi." -> "Chrome"
    match = re.match(r"^(.+?)\s+sudah dibuka", resp)
    if match:
        app_name = match.group(1)
        return f"{app_name} kubuka."
    return resp


def speak_and_show(message):
    ui_queue.put({'type': 'status', 'status': 'speaking'})
    bicara(message)
    ui_queue.put({'type': 'message', 'sender': 'airys', 'message': message})
    ui_queue.put({'type': 'status', 'status': 'listening'})


def main_loop():
    global aktif
    ui = init_ui()
    set_visualizer_callback(ui.update_visualizer)
    ui.tambah_pesan("system", "— sistem dimulai —")
    ui.set_status("standby")

    def process_ui_updates():
        try:
            while True:
                update = ui_queue.get_nowait()
                if update['type'] == 'message':
                    ui.tambah_pesan(update['sender'], update['message'])
                elif update['type'] == 'status':
                    ui.set_status(update['status'])
        except queue.Empty:
            pass
        ui.root.after(100, process_ui_updates)

    ui.root.after(100, process_ui_updates)

    def voice_loop():
        global aktif
        while True:
            if not aktif:
                ui_queue.put({'type': 'status', 'status': 'standby'})
                if listen_for_claps(target_count=2, timeout=2.5):
                    aktif = True
                    ui_queue.put({'type': 'status', 'status': 'aktif'})
                    sapa()
                    ui_queue.put({'type': 'status', 'status': 'listening'})
                time.sleep(0.05)
                continue

            ui_queue.put({'type': 'status', 'status': 'listening'})
            teks = transcribe()
            if not teks or len(teks) < 3:
                continue

            print(f"Terdeteksi: {teks}")
            ui_queue.put({'type': 'message', 'sender': 'user', 'message': teks})
            teks_lower = teks.lower()

            if any(k in teks_lower for k in NONAKTIF_KEYWORDS):
                aktif = False
                ui_queue.put({'type': 'status', 'status': 'standby'})
                message = "Oke, aku standby dulu."
                bicara(message)
                ui_queue.put({'type': 'message', 'sender': 'airys', 'message': message})
                print("Nonaktif. Tepuk 2x untuk aktif kembali.")
                continue

            if not has_wake_keyword(teks_lower):
                print("Diabaikan.")
                continue

            quick_response = quick_app_command(teks_lower)
            if quick_response:
                speak_and_show(quick_response)
                time.sleep(0.15)
                continue

            ui_queue.put({'type': 'status', 'status': 'thinking'})
            hasil = proses_perintah(teks)
            ucapan = hasil.get("ucapan", "Siap.")
            aksi = hasil.get("aksi", "jawab_saja")
            target = hasil.get("target", "")

            if aksi == "buka_app":
                resp = buka_aplikasi(target or teks_lower)
                speak_and_show(ucapan if resp else "Aku belum menemukan aplikasinya.")
            elif aksi == "ambil_berita":
                if target and target.isdigit():
                    nomor = int(target) - 1
                    berita_list = ambil_berita(5)
                    if 0 <= nomor < len(berita_list):
                        berita = berita_list[nomor]
                        message = f"Oke, aku buka berita nomor {target}."
                        speak_and_show(message)
                        ui_queue.put({'type': 'message', 'sender': 'system', 'message': berita['judul']})
                        webbrowser.open(berita['link'])
                    else:
                        speak_and_show("Nomor berita itu belum tersedia.")
                else:
                    # Run news mode in a separate thread to avoid blocking
                    news_thread = threading.Thread(
                        target=mode_interaktif,
                        kwargs={'ui_queue': ui_queue},
                        daemon=True
                    )
                    news_thread.start()
            else:
                speak_and_show(ucapan)

            time.sleep(0.15)

    voice_thread = threading.Thread(target=voice_loop, daemon=True)
    voice_thread.start()

    ui.run()


if __name__ == "__main__":
    main_loop()
