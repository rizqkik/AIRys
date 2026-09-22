import tkinter as tk
import time
import math
import random


class AIRysUI:
    """
    AIRys HUD Interface v2
    - Audio Input waveform (real mic) at bottom
    - Orbital wave around center ring (AIRys speaking)
    - Processing bar (real timing)
    - Voice Recognition bar (confidence)
    - Blue/cyan palette, "AIRYS" centered
    """

    # Colors
    BG = "#050810"
    CYAN = "#00d4ff"
    CYAN_BRIGHT = "#00ffff"
    CYAN_DIM = "#004466"
    CYAN_MID = "#0088cc"
    BLUE_DARK = "#0a1628"
    WHITE = "#ffffff"
    GRAY = "#8899aa"
    GRAY_DIM = "#445566"
    GREEN = "#00ff88"
    ORANGE = "#ff6600"

    def __init__(self, width=820, height=620):
        self.root = tk.Tk()
        self.root.title("AIRys HUD")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{width}x{height}+{(screen_w - width) // 2}+{(screen_h - height) // 2}")
        self.root.attributes('-topmost', False)

        # Animation state
        self.state = "standby"
        self.frame_count = 0
        self.glow_intensity = 0.4
        self.rotation_angle = 0
        self.scan_angle = 0

        # Audio levels (0.0 - 1.0)
        self.mic_level = 0.0          # Real mic input level
        self.target_mic_level = 0.0
        self.airys_level = 0.0        # AIRys output level
        self.target_airys_level = 0.0

        # Voice recognition confidence
        self.voice_confidence = 0.0
        self.target_voice_confidence = 0.0

        # Processing timing (0-100%)
        self.processing_pct = 0.0
        self.processing_active = False
        self.processing_start_time = 0

        # Wave orbital angle (spins when AIRys speaks)
        self.orbital_angle = 0.0

        # Canvas
        self.canvas = tk.Canvas(self.root, width=width, height=height,
                                bg=self.BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # HUD center
        self.hud_cx = width // 2
        self.hud_cy = height // 2 - 30

        # Build layers
        self._build_background()
        self._build_central_hud()
        self._build_audio_input_wave()
        self._build_status_bars()
        self._build_right_panel()
        self._build_connecting_lines()
        self._build_message_area()
        self._build_footer()

        # Start animation
        self._animate()

    # ------------------------------------------------------------------ #
    #                        BACKGROUND                                   #
    # ------------------------------------------------------------------ #
    def _build_background(self):
        w = self.canvas.winfo_reqwidth() or 820
        h = self.canvas.winfo_reqheight() or 620
        cx, cy = self.hud_cx, self.hud_cy

        # Radial grid lines
        for angle in range(0, 360, 15):
            rad = math.radians(angle)
            x2 = cx + math.cos(rad) * max(w, h)
            y2 = cy + math.sin(rad) * max(w, h)
            self.canvas.create_line(cx, cy, x2, y2, fill="#0d1f33",
                                    width=1, dash=(2, 8))

        # Scattered dots
        random.seed(42)
        for _ in range(35):
            x = random.randint(0, w)
            y = random.randint(0, h)
            if abs(x - cx) < 200 and abs(y - cy) < 200:
                continue
            s = random.uniform(0.5, 1.5)
            c = random.choice(["#0d1f33", "#132a40", "#0a1828"])
            self.canvas.create_oval(x-s, y-s, x+s, y+s, fill=c, outline="")

    # ------------------------------------------------------------------ #
    #                     CENTRAL HUD RINGS                               #
    # ------------------------------------------------------------------ #
    def _build_central_hud(self):
        cx, cy = self.hud_cx, self.hud_cy

        # Radii
        self.r_inner = 55
        self.r_data = 78
        self.r_tick = 98
        self.r_orbital = 118  # Where orbital wave rotates
        self.r_outer = 135
        self.r_connect = 160

        # Inner circle
        self.inner_circle = self.canvas.create_oval(
            cx - self.r_inner, cy - self.r_inner,
            cx + self.r_inner, cy + self.r_inner,
            fill=self.BLUE_DARK, outline=self.CYAN_DIM, width=2)

        # Outer ring
        self.outer_ring = self.canvas.create_oval(
            cx - self.r_outer, cy - self.r_outer,
            cx + self.r_outer, cy + self.r_outer,
            fill="", outline=self.CYAN_DIM, width=1)

        # Center text
        self.center_text = self.canvas.create_text(
            cx, cy - 4, text="AIRYS",
            font=("Segoe UI", 18, "bold"), fill=self.WHITE)
        self.center_sub = self.canvas.create_text(
            cx, cy + 18, text="ONLINE",
            font=("Segoe UI", 7), fill=self.CYAN_DIM)

        # Segmented data ring (3 arcs)
        self.segment_items = []
        for i in range(3):
            arc = self.canvas.create_arc(
                cx - self.r_data, cy - self.r_data,
                cx + self.r_data, cy + self.r_data,
                start=i * 120, extent=100,
                style="arc", outline=self.CYAN, width=2)
            self.segment_items.append(arc)

        # Tick marks
        self.tick_items = []
        for i in range(72):
            angle = math.radians(i * 5)
            is_major = i % 9 == 0
            r1, r2 = self.r_tick, self.r_tick + (8 if is_major else 4)
            x1 = cx + math.cos(angle) * r1
            y1 = cy + math.sin(angle) * r1
            x2 = cx + math.cos(angle) * r2
            y2 = cy + math.sin(angle) * r2
            c = self.CYAN_MID if is_major else self.CYAN_DIM
            item = self.canvas.create_line(x1, y1, x2, y2, fill=c, width=1)
            self.tick_items.append(item)

        # Orbital wave ring (AIRys voice - glowing dots that rotate)
        self.orbital_items = []
        for i in range(12):
            dot = self.canvas.create_oval(0, 0, 0, 0, fill=self.CYAN, outline="")
            self.orbital_items.append(dot)

        # Scan line
        self.scan_line = self.canvas.create_line(
            cx, cy, cx, cy - self.r_outer,
            fill=self.CYAN_BRIGHT, width=1)

        # Glow rings
        self.glow_items = []
        for i in range(3):
            r = self.r_inner + 6 + i * 4
            gc = self._fade(self.CYAN, max(0.15, 0.6 - i * 0.15))
            g = self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill="", outline=gc, width=1)
            self.glow_items.append(g)

    # ------------------------------------------------------------------ #
    #                    AUDIO INPUT WAVEFORM                             #
    # ------------------------------------------------------------------ #
    def _build_audio_input_wave(self):
        cx, cy = self.hud_cx, self.hud_cy
        wave_y = cy + self.r_outer + 60
        wave_w = 240
        wave_h = 50
        self.wave_y = wave_y
        self.wave_w = wave_w
        self.wave_h = wave_h
        self.wave_points = 48

        # BG
        self.canvas.create_rectangle(
            cx - wave_w // 2, wave_y - wave_h // 2,
            cx + wave_w // 2, wave_y + wave_h // 2,
            fill="#0a1220", outline=self.CYAN_DIM, width=1)

        # Wave line
        self.wave_line = self.canvas.create_line(
            cx - wave_w // 2, wave_y,
            cx + wave_w // 2, wave_y,
            fill=self.CYAN, width=2, smooth=True)

        # Label
        self.canvas.create_text(
            cx, wave_y + wave_h // 2 + 14,
            text="AUDIO INPUT", font=("Segoe UI", 7),
            fill=self.GRAY_DIM)

    # ------------------------------------------------------------------ #
    #                        STATUS BARS                                  #
    # ------------------------------------------------------------------ #
    def _build_status_bars(self):
        cx, cy = self.hud_cx, self.hud_cy
        left_x = cx - self.r_connect - 95

        # Voice Recognition
        bar_y = cy - 55
        self.canvas.create_text(
            left_x, bar_y - 12, text="VOICE RECOGNITION",
            font=("Segoe UI", 7, "bold"), fill=self.CYAN_MID, anchor="w")
        self.canvas.create_rectangle(
            left_x, bar_y, left_x + 80, bar_y + 8,
            fill="#0a1220", outline=self.CYAN_DIM, width=1)
        self.bar_voice_fill = self.canvas.create_rectangle(
            left_x, bar_y, left_x, bar_y + 8,
            fill=self.CYAN, outline="")
        self.bar_voice_text = self.canvas.create_text(
            left_x + 90, bar_y + 4, text="0%",
            font=("Segoe UI", 8), fill=self.GRAY, anchor="w")

        # Processing
        bar_y = cy + 15
        self.canvas.create_text(
            left_x, bar_y - 12, text="PROCESSING",
            font=("Segoe UI", 7, "bold"), fill=self.CYAN_MID, anchor="w")
        self.canvas.create_rectangle(
            left_x, bar_y, left_x + 80, bar_y + 8,
            fill="#0a1220", outline=self.CYAN_DIM, width=1)
        self.bar_proc_fill = self.canvas.create_rectangle(
            left_x, bar_y, left_x, bar_y + 8,
            fill=self.CYAN, outline="")
        self.bar_proc_text = self.canvas.create_text(
            left_x + 90, bar_y + 4, text="0%",
            font=("Segoe UI", 8), fill=self.GRAY, anchor="w")

    # ------------------------------------------------------------------ #
    #                       RIGHT PANEL                                   #
    # ------------------------------------------------------------------ #
    def _build_right_panel(self):
        cx, cy = self.hud_cx, self.hud_cy
        right_x = cx + self.r_connect + 55

        # Active indicator
        self.active_circle = self.canvas.create_oval(
            right_x - 20, cy - 55, right_x + 20, cy - 15,
            fill="", outline=self.CYAN_DIM, width=2)
        self.active_dot = self.canvas.create_oval(
            right_x - 4, cy - 39, right_x + 4, cy - 31,
            fill=self.CYAN, outline="")
        self.canvas.create_text(
            right_x + 32, cy - 39, text="ACTIVE",
            font=("Segoe UI", 8, "bold"), fill=self.CYAN, anchor="w")
        self.canvas.create_text(
            right_x + 32, cy - 25, text="ONLINE",
            font=("Segoe UI", 7), fill=self.GRAY, anchor="w")

        # All Systems Operational
        self.canvas.create_text(
            right_x, cy + 18, text="ALL SYSTEMS\nOPERATIONAL",
            font=("Segoe UI", 6, "bold"), fill=self.CYAN_MID,
            justify="center")
        bar_pos = [right_x - 24, right_x - 12, right_x, right_x + 12, right_x + 24]
        self.sys_bars = []
        base_y = cy + 58
        for i, bx in enumerate(bar_pos):
            bh = 8 + i * 4
            bar = self.canvas.create_rectangle(
                bx - 3, base_y - bh, bx + 3, base_y,
                fill=self.CYAN, outline="")
            self.sys_bars.append((bar, bh))

    # ------------------------------------------------------------------ #
    #                     CONNECTING LINES                                #
    # ------------------------------------------------------------------ #
    def _build_connecting_lines(self):
        cx, cy = self.hud_cx, self.hud_cy
        self.line_left = self.canvas.create_line(
            cx - self.r_connect, cy - 30,
            cx - self.r_connect - 25, cy - 30,
            fill=self.CYAN_DIM, width=1)
        self.line_right = self.canvas.create_line(
            cx + self.r_connect, cy - 30,
            cx + self.r_connect + 25, cy - 30,
            fill=self.CYAN_DIM, width=1)

    # ------------------------------------------------------------------ #
    #                      MESSAGE AREA                                   #
    # ------------------------------------------------------------------ #
    def _build_message_area(self):
        cx = self.hud_cx
        h = self.canvas.winfo_reqheight() or 620
        my = h - 58
        self.canvas.create_rectangle(
            160, my, cx * 2 - 160, my + 24,
            fill="#0a1220", outline=self.CYAN_DIM, width=1)
        self.msg_text = self.canvas.create_text(
            cx, my + 12, text="",
            font=("Segoe UI", 9), fill=self.GRAY, width=400)

    # ------------------------------------------------------------------ #
    #                         FOOTER                                      #
    # ------------------------------------------------------------------ #
    def _build_footer(self):
        cx = self.hud_cx
        h = self.canvas.winfo_reqheight() or 620
        self.footer_text = self.canvas.create_text(
            cx, h - 22, text="TEPUK 2X UNTUK MENGAKTIFKAN",
            font=("Segoe UI", 8), fill=self.GRAY_DIM)

    # ------------------------------------------------------------------ #
    #                         ANIMATION                                   #
    # ------------------------------------------------------------------ #
    def _animate(self):
        self.frame_count += 1
        t = time.time()

        # State params
        if self.state == "standby":
            tgt_glow, rot_speed, scan_spd = 0.25, 0.03, 0.2
            wave_amp = 0.3
        elif self.state == "aktif":
            tgt_glow, rot_speed, scan_spd = 0.7, 0.2, 0.8
            wave_amp = 2.0
        elif self.state == "listening":
            tgt_glow, rot_speed, scan_spd = 0.6, 0.12, 0.5
            wave_amp = 4.0  # Mic level drives this
        elif self.state == "thinking":
            tgt_glow, rot_speed, scan_spd = 0.9, 0.35, 1.5
            wave_amp = 1.5
        else:  # speaking
            tgt_glow, rot_speed, scan_spd = 1.0, 0.25, 1.0
            wave_amp = 5.0  # AIRys level drives this

        # Smooth transitions
        self.glow_intensity += (tgt_glow - self.glow_intensity) * 0.08
        self.rotation_angle += rot_speed
        self.scan_angle = (self.scan_angle + scan_spd) % 360

        # Mic level decay when not listening
        if self.state != "listening":
            self.target_mic_level *= 0.92
        self.mic_level += (self.target_mic_level - self.mic_level) * 0.15

        # AIRys level decay when not speaking
        if self.state != "speaking":
            self.target_airys_level *= 0.90
        self.airys_level += (self.target_airys_level - self.airys_level) * 0.12

        # Voice confidence
        self.voice_confidence += (self.target_voice_confidence - self.voice_confidence) * 0.1
        self.target_voice_confidence *= 0.95  # decay

        # Processing
        if self.processing_active:
            elapsed = time.time() - self.processing_start_time
            self.processing_pct = min(100, elapsed * 40)  # ~2.5s to fill
        else:
            self.processing_pct *= 0.9

        cx, cy = self.hud_cx, self.hud_cy

        # --- Segmented arcs ---
        for i, arc in enumerate(self.segment_items):
            base_start = i * 120 + self.rotation_angle * 30
            color = self._fade(self.CYAN, self.glow_intensity)
            self.canvas.itemconfig(arc, start=base_start, outline=color)

        # --- Scan line ---
        rad = math.radians(self.scan_angle)
        x2 = cx + math.cos(rad) * self.r_outer
        y2 = cy + math.sin(rad) * self.r_outer
        self.canvas.coords(self.scan_line, cx, cy, x2, y2)
        self.canvas.itemconfig(self.scan_line,
                               fill=self._fade(self.CYAN_BRIGHT, self.glow_intensity))

        # --- Orbital wave (AIRys voice - rotates around ring) ---
        self.orbital_angle += 0.08 + self.airys_level * 0.15
        orb_r = self.r_orbital + 8
        for i, dot in enumerate(self.orbital_items):
            angle = self.orbital_angle + i * (2 * math.pi / 12)
            orb_x = cx + math.cos(angle) * orb_r
            orb_y = cy + math.sin(angle) * orb_r
            # Size pulses with AIRys level
            sz = 2 + self.airys_level * 4 + math.sin(t * 8 + i) * self.airys_level * 2
            color = self._fade(self.CYAN_BRIGHT, 0.4 + self.airys_level * 0.5)
            self.canvas.coords(dot, orb_x - sz, orb_y - sz, orb_x + sz, orb_y + sz)
            self.canvas.itemconfig(dot, fill=color)

        # --- Tick marks ---
        for i, tick in enumerate(self.tick_items):
            is_major = i % 9 == 0
            phase = math.sin(t * 2 + i * 0.3)
            alpha = (0.5 if is_major else 0.25) + phase * 0.15 * self.glow_intensity
            self.canvas.itemconfig(tick, fill=self._fade(self.CYAN, alpha))

        # --- Glow rings ---
        for i, glow in enumerate(self.glow_items):
            alpha = max(0.1, self.glow_intensity - i * 0.2)
            color = self._fade(self.CYAN, alpha)
            self.canvas.itemconfig(glow, outline=color)
            pulse = math.sin(t * 2 + i) * 1.5
            r = self.r_inner + 6 + i * 4 + pulse
            self.canvas.coords(glow, cx - r, cy - r, cx + r, cy + r)

        # --- Inner circle ---
        ic = self._fade(self.CYAN_DIM, 0.3 + self.glow_intensity * 0.4)
        self.canvas.itemconfig(self.inner_circle, outline=ic)
        self.canvas.itemconfig(self.outer_ring,
                               outline=self._fade(self.CYAN_DIM, 0.2 + self.glow_intensity * 0.3))
        self.canvas.itemconfig(self.center_text,
                               fill=self._fade(self.WHITE, 0.7 + self.glow_intensity * 0.3))

        # --- Voice Recognition bar ---
        v_fill = 80 * self.voice_confidence
        left_x = cx - self.r_connect - 95
        self.canvas.coords(self.bar_voice_fill,
                           left_x, cy - 55, left_x + v_fill, cy - 47)
        self.canvas.itemconfig(self.bar_voice_text,
                               text=f"{int(self.voice_confidence * 100)}%")

        # --- Processing bar ---
        p_fill = 80 * (self.processing_pct / 100)
        self.canvas.coords(self.bar_proc_fill,
                           left_x, cy + 15, left_x + p_fill, cy + 23)
        self.canvas.itemconfig(self.bar_proc_text,
                               text=f"{int(self.processing_pct)}%")

        # --- Active indicator ---
        ac = self._fade(self.CYAN, 0.5 + self.glow_intensity * 0.5)
        self.canvas.itemconfig(self.active_circle, outline=ac)
        self.canvas.itemconfig(self.active_dot, fill=ac)

        # --- System bars ---
        right_x = cx + self.r_connect + 55
        for i, (bar, base_h) in enumerate(self.sys_bars):
            wobble = math.sin(t * 3 + i * 1.5) * 3
            new_h = max(4, base_h + wobble)
            bx = right_x - 24 + i * 12
            base_y = cy + 58
            self.canvas.coords(bar, bx - 3, base_y - new_h, bx + 3, base_y)

        # --- Audio Input Waveform (real mic) ---
        wave_coords = []
        for i in range(self.wave_points):
            x = cx - self.wave_w // 2 + (i / self.wave_points) * self.wave_w
            phase = t * 8 + i * 0.5
            mic_factor = self.mic_level if self.state == "listening" else self.mic_level * 0.3
            y_off = (math.sin(phase) * 0.5 +
                     math.sin(phase * 1.7 + 1) * 0.3 +
                     math.sin(phase * 0.3 + 2) * 0.2)
            y = self.wave_y + y_off * self.wave_h * wave_amp * mic_factor
            wave_coords.extend([x, y])
        if len(wave_coords) >= 4:
            self.canvas.coords(self.wave_line, *wave_coords)
            wc = self._fade(self.CYAN, 0.4 + self.glow_intensity * 0.5)
            self.canvas.itemconfig(self.wave_line, fill=wc)

        # --- Connecting lines ---
        for line in [self.line_left, self.line_right]:
            pulse = 0.1 + self.glow_intensity * 0.25
            self.canvas.itemconfig(line, fill=self._fade(self.CYAN_DIM, pulse))

        # --- Footer ---
        footer_map = {
            "standby": "TEPUK 2X UNTUK MENGAKTIFKAN",
            "aktif": "SIAP MENERIMA PERINTAH",
            "listening": "SEDANG MENDENGARKAN...",
            "thinking": "AIRys SEDANG BERPIKIR...",
            "speaking": "AIRys SEDANG BERBICARA..."
        }
        self.canvas.itemconfig(self.footer_text, text=footer_map.get(self.state, ""))

        self.root.after(16, self._animate)

    # ------------------------------------------------------------------ #
    #                       PUBLIC API                                    #
    # ------------------------------------------------------------------ #
    def set_status(self, mode):
        """standby, aktif, listening, thinking, speaking"""
        self.state = mode

    def tambah_pesan(self, pengirim, pesan):
        try:
            if pengirim == "airys":
                text = f"AIRys: {pesan}"
            elif pengirim == "user":
                text = f"Bos Rizqi: {pesan}"
            else:
                text = pesan
            self.canvas.itemconfig(self.msg_text, text=text)
        except Exception as e:
            print(f"UI error: {e}")

    def update_mic_level(self, level):
        """Update audio input level (0.0 - 1.0)."""
        self.target_mic_level = max(0.0, min(1.0, level))

    def update_airys_level(self, level):
        """Update AIRys output level (0.0 - 1.0)."""
        self.target_airys_level = max(0.0, min(1.0, level))

    def set_voice_confidence(self, confidence):
        """Update voice recognition confidence (0.0 - 1.0)."""
        self.target_voice_confidence = max(0.0, min(1.0, confidence))

    def start_processing(self):
        """Mark processing start."""
        self.processing_active = True
        self.processing_start_time = time.time()

    def stop_processing(self):
        """Mark processing done."""
        self.processing_active = False

    def run(self):
        self.root.mainloop()

    # ------------------------------------------------------------------ #
    #                        UTILITIES                                    #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _fade(hex_color, alpha):
        alpha = max(0.0, min(1.0, alpha))
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        bg_r, bg_g, bg_b = 0x05, 0x08, 0x10
        r = int(r * alpha + bg_r * (1 - alpha))
        g = int(g * alpha + bg_g * (1 - alpha))
        b = int(b * alpha + bg_b * (1 - alpha))
        return f"#{r:02x}{g:02x}{b:02x}"


ui = None


def init_ui():
    global ui
    ui = AIRysUI()
    return ui


if __name__ == "__main__":
    app = AIRysUI()
    app.set_status("aktif")
    app.tambah_pesan("system", "Sistem dimulai")
    app.tambah_pesan("airys", "Halo Bos Rizqi, AIRys online.")
    app.run()
