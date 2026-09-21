import asyncio
import os
import subprocess
import time
import shutil
import tempfile
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav_io

# Global callback for visualizer updates
visualizer_callback = None

def set_visualizer_callback(callback_func):
    global visualizer_callback
    visualizer_callback = callback_func

VOICE = "id-ID-GadisNeural"
RATE = "+8%"
VOLUME = "+0%"

LANGUAGE_VOICE_MAP = {
    "id": "id-ID-GadisNeural",
    "en": "en-US-GuyNeural",
    "es": "es-ES-AlvaroNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "pt": "pt-BR-AntonioNeural",
    "it": "it-IT-FrancescaNeural",
    "ru": "ru-RU-DariyaNeural",
    "ko": "ko-KR-SunHiNeural",
    "ja": "ja-JP-NanamiNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "ar": "ar-SA-HamadNeural",
    "hi": "hi-IN-SwaraNeural",
    "th": "th-TH-PaayalNeural",
    "ms": "ms-MY-YasminNeural",
    "tl": "fil-PH-BlessicaNeural",
}


def get_ffmpeg_path():
    """Find ffmpeg executable."""
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path
    
    # Try common locations
    common_paths = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        os.path.expandvars(r"%USERPROFILE%\ffmpeg\bin\ffmpeg.exe"),
    ]
    for p in common_paths:
        if os.path.exists(p):
            return p
    
    return None


FFMPEG_PATH = get_ffmpeg_path()


def deteksi_bahasa(teks):
    """
    Detect language from text.
    
    Args:
        teks: Text to analyze
    
    Returns:
        Voice ID string
    """
    teks_lower = teks.lower()

    # Unicode ranges for specific scripts
    if any('\u3040' <= ch <= '\u30ff' for ch in teks):  # Japanese
        return LANGUAGE_VOICE_MAP.get("ja")
    if any('\u4e00' <= ch <= '\u9fff' for ch in teks):  # Chinese
        return LANGUAGE_VOICE_MAP.get("zh")
    if any('\uac00' <= ch <= '\ud7af' for ch in teks):  # Korean
        return LANGUAGE_VOICE_MAP.get("ko")
    if any('\u0400' <= ch <= '\u04ff' for ch in teks):  # Russian
        return LANGUAGE_VOICE_MAP.get("ru")
    if any('\u0600' <= ch <= '\u06ff' for ch in teks):  # Arabic
        return LANGUAGE_VOICE_MAP.get("ar")
    if any('\u0900' <= ch <= '\u097f' for ch in teks):  # Hindi
        return LANGUAGE_VOICE_MAP.get("hi")
    if any('\u0e00' <= ch <= '\u0e7f' for ch in teks):  # Thai
        return LANGUAGE_VOICE_MAP.get("th")

    # Spanish character detection
    if any(ch in teks_lower for ch in "ñáéíóú¿¡"):
        return LANGUAGE_VOICE_MAP.get("es")

    # Word-based detection with more keywords
    kata_bahasa = {
        "es": ["que", "del", "los", "las", "por", "para", "una", "con", "hoy", "economía", 
               "gobierno", "niña", "ocurre", "paso", "detiene", "video", "sobre", "como",
               "pero", "también", "tiene", "puede", "fueron", "están", "según", "después"],
        "it": ["che", "perché", "oggi", "dove", "questo", "quello", "ancora", "sempre", 
               "solo", "anche", "sono", "molto", "tutto", "quando", "dopo", "ancora"],
        "fr": [ " le ", " la ", " et ", " est ", " mais ", " ou ", " avec ", " pour ", " une ", 
                " qui ", " où ", " bonjour ", " sont ", " cette ", " comme ", " après ", " aussi ",
                " comment ", " nous ", " vous ", " ils ", " elle ", " sur ", " dans ", " plus ",
                " tous ", " avoir ", " fait ", " sont ", " être ", " fait ", " sont ", " leurs "],
        "pt": ["que", "para", "dos", "das", "não", "com", "uma", "sobre", "brasil", "dia",
               "também", "como", "mais", "tem", "está", "ser", "quando", "muito"],
        "de": [" der ", " die ", " und ", " nicht ", " ist ", " das ", " ein ", " für ", " heute ",
               " sind ", " auch ", " aber ", " wie ", " nach ", " wenn ", " diese ", " noch "],
        "id": [" saya ", " kami ", " kamu ", " dia ", " kita ", " ada ", " akan ", " bisa ", 
               " dengan ", " untuk ", " tidak ", " sudah ", " belum ", " juga ", " sangat ", 
               " banyak ", " adalah ", " menjadi ", " telah ", " masih ", " harus ", " saja ", 
               " tetapi ", " karena ", " jika ", " saat ", " oleh ", " setelah ", " tentang "],
        "en": [" the ", " and ", " for ", " that ", " with ", " from ", " this ", " are ", " was ", 
               " news ", " today ", " market ", " president ", " economy ", " have ", " been ", 
               " which ", " will ", " could ", " would ", " should ", " about ", " their ", 
               " there ", " these ", " those ", " when ", " where ", " while ", " what ", " than "],
    }

    skor = {}
    for lang, kata_list in kata_bahasa.items():
        # Count matches (with word boundaries for space-padded keywords)
        count = 0
        for kata in kata_list:
            if kata.startswith(' ') and kata.endswith(' '):
                # Exact word/phrase match with spaces
                count += teks_lower.count(kata)
            else:
                # Substring match
                count += teks_lower.count(kata)
        skor[lang] = count
    
    bahasa_terpilih = max(skor, key=skor.get)

    if skor[bahasa_terpilih] > 0:
        return LANGUAGE_VOICE_MAP.get(bahasa_terpilih, LANGUAGE_VOICE_MAP["en"])

    # Default to Indonesian if no strong signal (since user is Indonesian)
    return LANGUAGE_VOICE_MAP["id"]


async def bicara_async(teks):
    """Main TTS function."""
    teks = teks.strip()
    if not teks:
        return

    voice = VOICE
    temp_dir = tempfile.mkdtemp()
    mp3_path = os.path.join(temp_dir, "speech.mp3")
    wav_path = os.path.join(temp_dir, "speech.wav")

    try:
        # Generate speech with edge-tts
        communicate = __import__('edge_tts').Communicate(teks, voice, rate=RATE, volume=VOLUME)
        await communicate.save(mp3_path)
    except Exception as e:
        print(f"TTS Error ({voice}): {e}")
        # Try fallback voice
        fallback_voice = "en-US-GuyNeural" if voice != "en-US-GuyNeural" else "id-ID-GadisNeural"
        try:
            communicate = __import__('edge_tts').Communicate(teks, fallback_voice, rate=RATE, volume=VOLUME)
            await communicate.save(mp3_path)
            voice = fallback_voice
        except Exception as e2:
            print(f"TTS Fallback Error ({fallback_voice}): {e2}")
            return

    # Convert MP3 to WAV
    try:
        if FFMPEG_PATH:
            subprocess.run(
                [FFMPEG_PATH, "-y", "-i", mp3_path, "-ar", "44100", "-f", "wav", wav_path],
                capture_output=True,
                timeout=30
            )
        else:
            # No ffmpeg, try direct MP3 playback
            print("Warning: ffmpeg not found. Trying direct playback...")
            return
    except Exception as e:
        print(f"Conversion error: {e}")
        return

    try:
        # Read and play audio
        sr, data = wav_io.read(wav_path)
        
        if data.dtype != np.float32:
            data = data.astype(np.float32) / 32768.0
            if data.ndim > 1:
                data = data.mean(axis=1)

        chunk_size = 1024
        stream = sd.OutputStream(samplerate=sr, channels=1, dtype='float32')
        stream.start()

        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            if len(chunk) < chunk_size:
                chunk = np.pad(chunk, (0, chunk_size - len(chunk)), 'constant')

            stream.write(chunk.reshape(-1, 1) if chunk.ndim == 1 else chunk)

            # Compute RMS amplitude
            rms = np.sqrt(np.mean(chunk ** 2))
            amplitude = min(1.0, rms * 2.0)

            if visualizer_callback:
                visualizer_callback(amplitude)

            time.sleep(chunk_size / sr * 0.95)

        stream.stop()
        stream.close()
        time.sleep(0.05)
    except Exception as e:
        print(f"Playback error: {e}")
    finally:
        # Cleanup temp files
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass


def bicara(teks):
    """Synchronous wrapper for bicara_async."""
    print(f"\nAIRys: {teks}\n")
    asyncio.run(bicara_async(teks))


def bicara_dengan_bahasa(teks, detect_text=None, rate="-10%"):
    """
    Speak text with language detection (for multilingual news).
    
    Args:
        teks: Text to speak
        detect_text: Text to analyze for language detection (uses teks if None)
        rate: Speech rate modifier
    """
    voice = deteksi_bahasa(detect_text or teks)
    fallback_voices = ["es-ES-AlvaroNeural", "en-US-GuyNeural", "id-ID-GadisNeural"]

    temp_dir = tempfile.mkdtemp()
    mp3_path = os.path.join(temp_dir, "news.mp3")
    wav_path = os.path.join(temp_dir, "news.wav")
    ffmpeg_path = FFMPEG_PATH

    async def play(selected_voice):
        communicate = __import__('edge_tts').Communicate(teks, selected_voice, rate=rate)
        await communicate.save(mp3_path)

    print(f"[{voice}]: {teks}")
    try:
        asyncio.run(play(voice))
        
        if ffmpeg_path:
            subprocess.run(
                [ffmpeg_path, "-y", "-i", mp3_path, "-ar", "44100", "-f", "wav", wav_path],
                capture_output=True,
                timeout=30
            )
            sr, data = wav_io.read(wav_path)
            sd.play(data, sr)
            sd.wait()
    except Exception as e:
        print(f"TTS Error ({voice}): {e}")
        for fallback_voice in fallback_voices:
            if fallback_voice == voice:
                continue
            try:
                print(f"TTS fallback to {fallback_voice}")
                asyncio.run(play(fallback_voice))
                if ffmpeg_path:
                    subprocess.run(
                        [ffmpeg_path, "-y", "-i", mp3_path, "-ar", "44100", "-f", "wav", wav_path],
                        capture_output=True,
                        timeout=30
                    )
                    sr, data = wav_io.read(wav_path)
                    sd.play(data, sr)
                    sd.wait()
                return
            except Exception as e2:
                print(f"TTS Fallback Error ({fallback_voice}): {e2}")
    finally:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass


# =========================
# GREETING SYSTEM
# =========================

from datetime import datetime


def briefing_pagi():
    bicara("Pagi Rizqi. AIRys aktif. Ada yang bisa kubantu?")


def briefing_siang():
    bicara("Siang Rizqi. AIRys siap.")


def briefing_sore():
    bicara("Sore Rizqi. Aku aktif.")


def briefing_malam():
    bicara("Malam Rizqi. AIRys siap.")


def shutdown_message():
    bicara("Oke, aku standby dulu.")
