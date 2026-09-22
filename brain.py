import json
import time
import os
import re
from pathlib import Path
from groq import Groq

# Fix encoding for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'


def load_env():
    """Load environment variables from .env file if it exists."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value


load_env()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY tidak ditemukan. Pastikan file .env berisi GROQ_API_KEY=...")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
Kamu adalah AIRys, asisten AI pribadi milik Rizqi.

Kepribadian:
- Tenang, cerdas, sigap, dan terasa akrab.
- Nama kamu adalah AIRys (dibaca "Airis", bukan "A-I-R-Y-S").
- Selalu sebut dirimu sebagai "Airis" dalam percakapan, jangan pernah mengeja atau menyebut "AIRYS".
- Natural seperti asisten pribadi yang sudah sering diajak ngobrol.
- Jangan terdengar seperti chatbot formal.

Gaya bicara:
- Bahasa Indonesia santai dan sopan.
- Jawaban pendek, langsung, dan tidak bertele-tele.
- Jangan selalu menyebut "Bos Rizqi". Pakai sesekali saja saat terasa natural.
- Hindari pola berulang seperti "Tentu Bos Rizqi" atau "Baik Bos Rizqi" di setiap jawaban.
- Untuk aksi sederhana, cukup jawab ringkas seperti "Siap, aku buka.", "Oke, aku cek dulu.", "Chrome kubuka.", atau "Sebentar, aku lihat."
- Untuk pertanyaan, jawab seperti ngobrol biasa.

Balas HANYA dalam format JSON valid berikut:

{
  "aksi": "buka_app" atau "jawab_saja" atau "ambil_berita",
  "target": "nama aplikasi atau kosong",
  "ucapan": "respons natural dan singkat"
}

Contoh:
User: "Airis buka chrome"
{
  "aksi": "buka_app",
  "target": "chrome",
  "ucapan": "Chrome kubuka."
}

User: "Airis apa berita hari ini"
{
  "aksi": "ambil_berita",
  "target": "",
  "ucapan": "Oke, aku cek berita terbaru."
}

User: "Airis apa itu inflasi"
{
  "aksi": "jawab_saja",
  "target": "",
  "ucapan": "Inflasi itu kondisi saat harga barang dan jasa naik secara umum dalam periode tertentu."
}
"""


def extract_json(text):
    """Extract JSON from text, handling markdown code blocks and other wrappers."""
    # Try direct JSON parse first
    try:
        return json.loads(text.strip())
    except:
        pass
    
    # Try to extract from markdown code blocks (multiline)
    code_block_match = re.search(r'```(?:json)?\s*[\r\n]+(.*?)[\r\n]+\s*```', text, re.DOTALL)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1).strip())
        except:
            pass
    # Try inline code block
    code_block_match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1).strip())
        except:
            pass
    
    # Try to find JSON object in text
    json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except:
            pass
    
    # Try more lenient JSON extraction
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end+1])
        except:
            pass
    
    return None


def proses_perintah(teks, max_retries=2):
    """
    Process user command through Groq AI.
    """
    # Ensure proper encoding
    if isinstance(teks, bytes):
        teks = teks.decode('utf-8', errors='replace')
    
    # Clean input - remove non-ASCII characters that might cause issues
    teks_clean = teks.encode('ascii', errors='ignore').decode('ascii')
    
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": teks_clean}
                ],
                temperature=0.55,
                max_tokens=140
            )

            raw = response.choices[0].message.content.strip()
            
            # Ensure raw is a string
            if isinstance(raw, bytes):
                raw = raw.decode('utf-8', errors='replace')
            
            # Try to parse JSON
            result = extract_json(raw)
            if result:
                return result
            
            # If parsing fails, treat as plain text answer
            print(f"Warning: Could not parse JSON response: {raw}")
            return {
                "aksi": "jawab_saja",
                "target": "",
                "ucapan": raw
            }
            
        except UnicodeEncodeError as e:
            print(f"Encoding error (attempt {attempt + 1}/{max_retries + 1}): {e}")
            teks_clean = teks_clean.encode('ascii', errors='ignore').decode('ascii')
            if attempt < max_retries:
                time.sleep(1 * (attempt + 1))
            else:
                return {
                    "aksi": "jawab_saja",
                    "target": "",
                    "ucapan": "Maaf, ada masalah encoding. Coba lagi."
                }
        except Exception as e:
            print(f"Brain error (attempt {attempt + 1}/{max_retries + 1}): {e}")
            if attempt < max_retries:
                time.sleep(1 * (attempt + 1))
            else:
                return {
                    "aksi": "jawab_saja",
                    "target": "",
                    "ucapan": "Maaf, saya sedang mengalami masalah teknis. Coba lagi nanti."
                }
    
    return {
        "aksi": "jawab_saja",
        "target": "",
        "ucapan": "Maaf, saya tidak dapat memproses perintah saat ini."
    }


if __name__ == "__main__":
    hasil = proses_perintah("Airis tolong buka chrome")
    print(hasil)
