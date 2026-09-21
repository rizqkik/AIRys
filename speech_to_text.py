import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import os
import time
import warnings

model = None
DEVICE_ID = None

SAMPLE_RATE = 16000
SPEECH_THRESHOLD = 0.012
START_TIMEOUT = 4.0
SILENCE_DURATION = 1.0
MAX_DURATION = 8.0
MIN_RECORD_DURATION = 0.3
BLOCK_SIZE = 1024

def load_model():
    """Lazy load the whisper model."""
    global model
    if model is None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = whisper.load_model("base")
    return model


def get_default_input_device():
    """Get the default input device ID."""
    try:
        device = sd.query_devices(kind='input')
        return device['index']
    except Exception:
        return None


def record_audio(sample_rate=SAMPLE_RATE):
    """
    Record audio from microphone until silence or max duration.
    
    Args:
        sample_rate: Audio sample rate
    
    Returns:
        Tuple of (audio_data, sample_rate) or (None, sample_rate) if timeout
    """
    global DEVICE_ID
    
    if DEVICE_ID is None:
        DEVICE_ID = get_default_input_device()
    
    print("Mendengarkan perintah...")
    frames = []
    started = False
    speech_started_at = None
    last_voice_at = None
    start_time = time.time()

    def callback(indata, frame_count, time_info, status):
        nonlocal started, speech_started_at, last_voice_at
        now = time.time()
        volume = float(np.sqrt(np.mean((indata.astype(np.float32) / 32768.0) ** 2)))

        if volume > SPEECH_THRESHOLD:
            if not started:
                started = True
                speech_started_at = now
            last_voice_at = now

        if started:
            frames.append(indata.copy())

    try:
        with sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
            blocksize=BLOCK_SIZE,
            device=DEVICE_ID,
            callback=callback
        ):
            while True:
                now = time.time()

                if not started and now - start_time > START_TIMEOUT:
                    return None, sample_rate

                if started:
                    recorded_for = now - speech_started_at
                    silent_for = now - last_voice_at if last_voice_at else 0
                    if recorded_for >= MIN_RECORD_DURATION and silent_for >= SILENCE_DURATION:
                        break
                    if recorded_for >= MAX_DURATION:
                        break

                time.sleep(0.03)
    except Exception as e:
        print(f"Recording error: {e}")
        return None, sample_rate

    if not frames:
        return None, sample_rate

    return np.concatenate(frames, axis=0), sample_rate


def transcribe():
    """
    Transcribe audio from microphone to text.
    
    Returns:
        Transcribed text string
    """
    audio, sr = record_audio()
    if audio is None or len(audio) == 0:
        return ""

    tmp_path = tempfile.mktemp(suffix=".wav")
    wav.write(tmp_path, sr, audio)
    
    try:
        whisper_model = load_model()
        result = whisper_model.transcribe(
            tmp_path,
            language="id",
            initial_prompt="Airis, tolong buka Chrome, Spotify, Outlook, WhatsApp, Excel, Word, Notepad"
        )
        return result["text"].strip()
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass


if __name__ == "__main__":
    print("Bicara sekarang...")
    teks = transcribe()
    print(f"Kamu bilang: {teks}")
