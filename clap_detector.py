import sounddevice as sd
import numpy as np
import time

SAMPLE_RATE = 16000
THRESHOLD = 0.15
CLAP_WINDOW = 2.0
MIN_GAP = 0.15
DEVICE_ID = None  # None = default device


def get_default_input_device():
    """Get the default input device ID."""
    try:
        device = sd.query_devices(kind='input')
        return device['index']
    except Exception:
        return None


def listen_for_claps(target_count=2, timeout=3.0):
    """
    Listen for claps to activate the system.
    
    Args:
        target_count: Number of claps required to activate
        timeout: Maximum time to wait for claps
    
    Returns:
        True if target_count claps detected within timeout, False otherwise
    """
    global DEVICE_ID
    
    # Auto-detect device if not set
    if DEVICE_ID is None:
        DEVICE_ID = get_default_input_device()
    
    clap_times = []
    last_clap_time = 0
    start = time.time()
    
    def callback(indata, frames, time_info, status):
        nonlocal last_clap_time
        volume = np.max(np.abs(indata))
        
        if volume > THRESHOLD:
            now = time.time()
            # Debounce: ignore claps too close together
            if not clap_times or (now - last_clap_time) > MIN_GAP:
                clap_times.append(now)
                last_clap_time = now
                print(f"Tepuk terdeteksi! ({len(clap_times)})")
    
    try:
        with sd.InputStream(
            callback=callback,
            channels=1,
            samplerate=SAMPLE_RATE,
            device=DEVICE_ID,
            blocksize=512
        ):
            while time.time() - start < timeout:
                time.sleep(0.02)
                # Clean up old claps outside the window
                recent = [t for t in clap_times if time.time() - t < CLAP_WINDOW]
                if len(recent) >= target_count:
                    return True
    except Exception as e:
        print(f"Clap detector error: {e}")
        return False
    
    return False


if __name__ == "__main__":
    print("Listening for 2 claps...")
    result = listen_for_claps(target_count=2, timeout=5.0)
    print(f"Result: {result}")
