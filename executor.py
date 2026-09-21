import subprocess
import os
import shutil
from pathlib import Path


# System commands that don't need full path or existence check
SYSTEM_COMMANDS = {
    "notepad": "notepad.exe",
    "kalkulator": "calc.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "explorer": "explorer.exe",
    "folder": "explorer.exe",
    "cmd": "cmd.exe",
    "terminal": "cmd.exe",
    "paint": "mspaint.exe",
    "wordpad": "wordpad.exe",
    "snippingtool": "snippingtool.exe",
    "screenshot": "snippingtool.exe",
}


def find_app_path(app_name):
    """Try to find application path dynamically using 'where' command."""
    try:
        result = subprocess.run(
            ['where', app_name],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    return None


def buka_aplikasi(perintah):
    """
    Open application based on voice command.
    
    Args:
        perintah: Voice command text containing app name
    
    Returns:
        Response string if app was opened, None otherwise
    """
    perintah_lower = perintah.lower()
    
    # Define apps to try - system commands first, then installed apps
    apps_to_try = []
    
    # System commands (guaranteed to work on Windows)
    system_apps = {
        "notepad": ("notepad.exe", "Notepad"),
        "kalkulator": ("calc.exe", "Kalkulator"),
        "calculator": ("calc.exe", "Kalkulator"),
        "calc": ("calc.exe", "Kalkulator"),
        "explorer": ("explorer.exe", "Explorer"),
        "folder": ("explorer.exe", "Explorer"),
        "cmd": ("cmd.exe", "Command Prompt"),
        "terminal": ("cmd.exe", "Command Prompt"),
        "paint": ("mspaint.exe", "Paint"),
        "wordpad": ("wordpad.exe", "Wordpad"),
        "snippingtool": ("snippingtool.exe", "Snipping Tool"),
        "screenshot": ("snippingtool.exe", "Snipping Tool"),
    }
    
    # Add system apps that match
    for keyword, (exe, display_name) in system_apps.items():
        if keyword in perintah_lower:
            apps_to_try.append((keyword, exe, display_name))
    
    # Installed applications (need to check existence)
    installed_apps = {
        "chrome": [
            (r"C:\Program Files\Google\Chrome\Application\chrome.exe", "Chrome"),
            (r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", "Chrome"),
        ],
        "edge": [
            (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "Edge"),
            (r"C:\Program Files\Microsoft\Edge\Application\msedge.exe", "Edge"),
        ],
        "outlook": [
            (r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE", "Outlook"),
            (r"C:\Program Files (x86)\Microsoft Office\root\Office16\OUTLOOK.EXE", "Outlook"),
        ],
        "word": [
            (r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE", "Word"),
            (r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE", "Word"),
        ],
        "excel": [
            (r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE", "Excel"),
            (r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE", "Excel"),
        ],
        "powerpoint": [
            (r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE", "PowerPoint"),
            (r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE", "PowerPoint"),
        ],
        "whatsapp": [
            (os.path.expandvars(r"%LOCALAPPDATA%\WhatsApp\WhatsApp.exe"), "WhatsApp"),
        ],
        "spotify": [
            (os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"), "Spotify"),
            (os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\SpotifyAB.SpotifyMusic_zpdnekdrzrea0\Spotify.exe"), "Spotify"),
        ],
        "vs code": [
            (os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"), "VS Code"),
            (r"C:\Program Files\Microsoft VS Code\Code.exe", "VS Code"),
        ],
        "vscode": [
            (os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"), "VS Code"),
            (r"C:\Program Files\Microsoft VS Code\Code.exe", "VS Code"),
        ],
    }
    
    # Add installed apps that exist and match
    for keyword, paths in installed_apps.items():
        if keyword in perintah_lower:
            for path, display_name in paths:
                if os.path.exists(path):
                    apps_to_try.append((keyword, path, display_name))
                    break
    
    # If no matches, try 'where' command as fallback
    if not apps_to_try:
        # Extract potential app name from command
        words = perintah_lower.split()
        for word in words:
            if word in ["buka", "open", "jalankan", "nyalakan", "tolong", "bisakah"]:
                continue
            if len(word) > 2:
                path = find_app_path(word)
                if path:
                    apps_to_try.append((word, path, word.capitalize()))
                    break
    
    # Try to open matched apps
    opened = []
    for keyword, path, display_name in apps_to_try:
        try:
            if path.endswith('.exe'):
                subprocess.Popen(path)
            else:
                subprocess.Popen(path, shell=True)
            opened.append(display_name)
        except Exception as e:
            print(f"Gagal buka {display_name}: {e}")
    
    if opened:
        return f"{', '.join(opened)} sudah dibuka."
    
    return None


if __name__ == "__main__":
    # Test
    print(buka_aplikasi("buka notepad"))
    print(buka_aplikasi("buka chrome"))
    print(buka_aplikasi("buka kalkulator"))
