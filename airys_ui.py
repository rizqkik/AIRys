import tkinter as tk
import time
import math
import random


class AIRysUI:
    """
    AIRys HUD Interface — JARVIS-style circular heads-up display.
    Central concentric rings with animated arcs, peripheral status panels,
    waveform visualizer, and connecting lines.
    """

    # Color palette (matching JARVIS HUD reference)
    BG = "#050810"
    CYAN = "#00d4ff"
    CYAN_BRIGHT = "#00ffff"
    CYAN_DIM = "#004466"
    CYAN_MID = "#0088cc"
    BLUE_DARK = "#0a1628"
    BLUE_MED = "#0066cc"
    WHITE = "#ffffff"
    GRAY = "#8899aa"
    GRAY_DIM = "#445566"
    GREEN = "#00ff88"
    ORANGE = "#ff6600"
    RING_FILL = "#0a1628"

    def __init__(self, width=800, height=600):
        self.root = tk.Tk()
        self.root.title("AIRys HUD")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)
        self.root.geometry(f"{width}x{height}")
        self.root.attributes('-topmost', True)
        # Position: top-right corner
        screen_w = self.root.winfo_screenwidth()
        self.root.geometry(f"{width}x{height}+{screen_w - width - 20}+20")

        # Animation state
        self.frame_count = 0
        self.state = "standby"  # standby, aktif, listening, thinking, speaking
        self.glow_intensity = 0.5
        self.rotation_angle = 0
        self.audio_level = 0.0
        self.target_audio_level = 0.0
        self.scan_angle = 0

        # Text display
        self.last_user_text = ""
        self.last_airys_text = ""

        # Build canvas
        self.canvas = tk.Canvas(
            self.root, width=width, height=height,
            bg=self.BG, highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Pre-generate background grid
        self._build_background()

        # Central HUD elements (static)
        self._build_central_hud()

        # Peripheral panels
        self._build_status_bars()
        self._build_right_panel()
        self._build_connecting_lines()
        self._build_waveform()

        # Footer
        self.footer_text = self.canvas.create_text(
            width // 2, height - 18,
            text="TEPUK 2X UNTUK MENGAKTIFKAN",
            font=("Segoe UI", 9),
            fill=self.GRAY_DIM
        )

        # Message area (bottom center, above footer)
        self.msg_bg = self.canvas.create_rectangle(
            180, height - 60, width - 180, height - 35,
            fill="#0a1220", outline=self.CYAN_DIM, width=1
        )
        self.msg_text = self.canvas.create_text(
            width // 2, height - 47,
            text="",
            font=("Segoe UI", 10),
            fill=self.GRAY,
            width=380
        )

        # Start animation loop
        self._animate()

    # ------------------------------------------------------------------ #
    #                        BACKGROUND GRID                              #
    # ------------------------------------------------------------------ #
    def _build_background(self):
        w = self.canvas.winfo_reqwidth() or 800
        h = self.canvas.winfo_reqheight() or 600

        # Radial grid (spider web) — faint lines from center
        cx, cy = w // 2, h // 2 - 20
        for angle in range(0, 360, 15):
            rad = math.radians(angle)
            x2 = cx + math.cos(rad) * max(w, h)
            y2 = cy + math.sin(rad) * max(w, h)
            self.canvas.create_line(cx, cy, x2, y2,
                                    fill="#0d1f33", width=1, dash=(2, 8))

        # Scatter dots (data nodes)
        random.seed(42)
        for _ in range(40):
            x = random.randint(0, w)
            y = random.randint(0, h)
            # Avoid center area
            if abs(x - cx) < 180 and abs(y - cy) < 180:
                continue
            size = random.uniform(0.5, 1.5)
            alpha_hex = random.choice(["#0d1f33", "#132a40", "#0a1828"])
            self.canvas.create_oval(x - size, y - size, x + size, y + size,
                                    fill=alpha_hex, outline="")

    # ------------------------------------------------------------------ #
    #                        CENTRAL HUD RINGS                            #
    # ------------------------------------------------------------------ #
    def _build_central_hud(self):
        w = self.canvas.winfo_reqwidth() or 800
        h = self.canvas.winfo_reqheight() or 600
        self.hud_cx = w // 2
        self.hud_cy = h // 2 - 20

        cx, cy = self.hud_cx, self.hud_cy

        # Ring radii
        self.r_inner = 55      # text circle
        self.r_data = 75       # segmented arc ring
        self.r_tick = 95       # tick marks ring
        self.r_outer = 115     # outer decorative ring
        self.r_connect = 140   # connection lines start

        # Static ring items
        # Inner circle (text background)
        self.inner_circle = self.canvas.create_oval(
            cx - self.r_inner, cy - self.r_inner,
            cx + self.r_inner, cy + self.r_inner,
            fill=self.BLUE_DARK, outline=self.CYAN_DIM, width=2
        )

        # Outer ring (static)
        self.outer_ring = self.canvas.create_oval(
            cx - self.r_outer, cy - self.r_outer,
            cx + self.r_outer, cy + self.r_outer,
            fill="", outline=self.CYAN_DIM, width=1
        )

        # Center text: "AIRYS"
        self.center_text = self.canvas.create_text(
            cx, cy, text="AIRYS",
            font=("Segoe UI", 20, "bold"),
            fill=self.WHITE
        )

        # Subtitle below center
        self.center_subtitle = self.canvas.create_text(
            cx, cy + 22, text="ONLINE",
            font=("Segoe UI", 7),
            fill=self.CYAN_DIM
        )

        # Dynamic elements (updated in animate)
        self.segment_items = []
        self.tick_items = []
        self.scan_line = None
        self.glow_items = []

        # Create tick marks (72 ticks, every 5 degrees)
        for i in range(72):
            angle = math.radians(i * 5)
            is_major = i % 9 == 0  # major tick every 45 degrees
            r1 = self.r_tick
            r2 = self.r_tick + (8 if is_major else 4)
            x1 = cx + math.cos(angle) * r1
            y1 = cy + math.sin(angle) * r1
            x2 = cx + math.cos(angle) * r2
            y2 = cy + math.sin(angle) * r2
            color = self.CYAN_MID if is_major else self.CYAN_DIM
            item = self.canvas.create_line(x1, y1, x2, y2,
                                           fill=color, width=1)
            self.tick_items.append(item)

        # Create segmented data ring (3 arcs of 120 degrees each)
        for i in range(3):
            start = i * 120
            arc = self.canvas.create_arc(
                cx - self.r_data, cy - self.r_data,
                cx + self.r_data, cy + self.r_data,
                start=start, extent=100,
                style="arc", outline=self.CYAN, width=2
            )
            self.segment_items.append(arc)

        # Scan line
        self.scan_line = self.canvas.create_line(
            cx, cy, cx, cy - self.r_outer,
            fill=self.CYAN_BRIGHT, width=1
        )

        # Glow circles (multiple for glow effect)
        for i in range(3):
            r = self.r_inner + 6 + i * 4
            alpha = max(20, 60 - i * 15)
            hex_color = self._fade_color(self.CYAN, alpha / 100)
            glow = self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill="", outline=hex_color, width=1
            )
            self.glow_items.append(glow)

    # ------------------------------------------------------------------ #
    #                          STATUS BARS                                #
    # ------------------------------------------------------------------ #
    def _build_status_bars(self):
        """Left panel: System Status, Voice Recognition, Processing."""
        cx = self.hud_cx
        cy = self.hud_cy
        left_x = cx - self.r_connect - 90

        # System Status bar
        bar_y = cy - 50
        self.canvas.create_text(
            left_x, bar_y - 14, text="SYSTEM STATUS",
            font=("Segoe UI", 7, "bold"), fill=self.CYAN_MID, anchor="w"
        )
        self.bar_sys_bg = self.canvas.create_rectangle(
            left_x, bar_y, left_x + 80, bar_y + 8,
            fill="#0a1220", outline=self.CYAN_DIM, width=1
        )
        self.bar_sys_fill = self.canvas.create_rectangle(
            left_x, bar_y, left_x, bar_y + 8,
            fill=self.CYAN, outline=""
        )

        # Voice Recognition bar
        bar_y = cy + 10
        self.canvas.create_text(
            left_x, bar_y - 14, text="VOICE RECOGNITION",
            font=("Segoe UI", 7, "bold"), fill=self.CYAN_MID, anchor="w"
        )
        self.bar_voice_bg = self.canvas.create_rectangle(
            left_x, bar_y, left_x + 80, bar_y + 8,
            fill="#0a1220", outline=self.CYAN_DIM, width=1
        )
        self.bar_voice_fill = self.canvas.create_rectangle(
            left_x, bar_y, left_x, bar_y + 8,
            fill=self.CYAN, outline=""
        )

        # Processing bar
        bar_y = cy + 70
        self.canvas.create_text(
            left_x, bar_y - 14, text="PROCESSING",
            font=("Segoe UI", 7, "bold"), fill=self.CYAN_MID, anchor="w"
        )
        self.bar_proc_bg = self.canvas.create_rectangle(
            left_x, bar_y, left_x + 80, bar_y + 8,
            fill="#0a1220", outline=self.CYAN_DIM, width=1
        )
        self.bar_proc_fill = self.canvas.create_rectangle(
            left_x, bar_y, left_x, bar_y + 8,
            fill=self.CYAN, outline=""
        )
        self.bar_proc_text = self.canvas.create_text(
            left_x + 90, bar_y + 4, text="0%",
            font=("Segoe UI", 8), fill=self.GRAY, anchor="w"
        )

    # ------------------------------------------------------------------ #
    #                          RIGHT PANEL                                #
    # ------------------------------------------------------------------ #
    def _build_right_panel(self):
        """Right panel: Active status, All Systems Operational."""
        cx = self.hud_cx
        cy = self.hud_cy
        right_x = cx + self.r_connect + 60

        # Active circle indicator
        self.active_circle = self.canvas.create_oval(
            right_x - 18, cy - 50, right_x + 18, cy - 14,
            fill="", outline=self.CYAN_DIM, width=2
        )
        self.active_dot = self.canvas.create_oval(
            right_x - 4, cy - 38, right_x + 4, cy - 30,
            fill=self.CYAN, outline=""
        )
        self.canvas.create_text(
            right_x + 30, cy - 36, text="ACTIVE",
            font=("Segoe UI", 8, "bold"), fill=self.CYAN, anchor="w"
        )
        self.canvas.create_text(
            right_x + 30, cy - 24, text="ONLINE",
            font=("Segoe UI", 7), fill=self.GRAY, anchor="w"
        )

        # All Systems Operational bar chart
        self.canvas.create_text(
            right_x, cy + 18, text="ALL SYSTEMS\nOPERATIONAL",
            font=("Segoe UI", 6, "bold"), fill=self.CYAN_MID,
            justify="center"
        )
        bar_positions = [right_x - 24, right_x - 12, right_x,
                          right_x + 12, right_x + 24]
        self.sys_bars = []
        base_y = cy + 55
        for i, bx in enumerate(bar_positions):
            bar_h = 8 + i * 4
            bar = self.canvas.create_rectangle(
                bx - 3, base_y - bar_h, bx + 3, base_y,
                fill=self.CYAN, outline=""
            )
            self.sys_bars.append((bar, bar_h))

    # ------------------------------------------------------------------ #
    #                       CONNECTING LINES                              #
    # ------------------------------------------------------------------ #
    def _build_connecting_lines(self):
        """Thin lines from central HUD to peripheral panels."""
        cx = self.hud_cx
        cy = self.hud_cy

        # Left connections
        self.line_left_sys = self.canvas.create_line(
            cx - self.r_connect, cy - 30,
            cx - self.r_connect - 30, cy - 30,
            fill=self.CYAN_DIM, width=1
        )
        self.line_left_voice = self.canvas.create_line(
            cx - self.r_connect, cy + 30,
            cx - self.r_connect - 30, cy + 30,
            fill=self.CYAN_DIM, width=1
        )

        # Right connections
        self.line_right_active = self.canvas.create_line(
            cx + self.r_connect, cy - 30,
            cx + self.r_connect + 30, cy - 30,
            fill=self.CYAN_DIM, width=1
        )
        self.line_right_sys = self.canvas.create_line(
            cx + self.r_connect, cy + 30,
            cx + self.r_connect + 30, cy + 30,
            fill=self.CYAN_DIM, width=1
        )

    # ------------------------------------------------------------------ #
    #                          WAVEFORM                                   #
    # ------------------------------------------------------------------ #
    def _build_waveform(self):
        """Audio waveform visualizer below the central HUD."""
        cx = self.hud_cx
        cy = self.hud_cy
        wave_y = cy + self.r_outer + 50
        self.wave_y = wave_y
        wave_w = 200
        wave_h = 40
        self.wave_h = wave_h
        self.wave_points = 40

        # Background
        self.wave_bg = self.canvas.create_rectangle(
            cx - wave_w // 2, wave_y - wave_h // 2,
            cx + wave_w // 2, wave_y + wave_h // 2,
            fill="#0a1220", outline=self.CYAN_DIM, width=1
        )

        # Waveform line (animated)
        self.wave_line = self.canvas.create_line(
            cx - wave_w // 2, wave_y,
            cx + wave_w // 2, wave_y,
            fill=self.CYAN, width=1, smooth=True
        )

        # Label
        self.canvas.create_text(
            cx, wave_y + wave_h // 2 + 12,
            text="AUDIO INPUT",
            font=("Segoe UI", 6), fill=self.GRAY_DIM
        )

    # ------------------------------------------------------------------ #
    #                         ANIMATION                                   #
    # ------------------------------------------------------------------ #
    def _animate(self):
        self.frame_count += 1
        t = time.time()

        # --- State-based parameters ---
        if self.state == "standby":
            self.target_audio_level = 0.02
            rotation_speed = 0.05
            glow_target = 0.3
            scan_speed = 0.3
            bar_level = 0.3
            wave_amp = 0.5
        elif self.state == "aktif":
            self.target_audio_level = 0.08
            rotation_speed = 0.2
            glow_target = 0.7
            scan_speed = 0.8
            bar_level = 0.8
            wave_amp = 2.0
        elif self.state == "listening":
            self.target_audio_level = 0.06
            rotation_speed = 0.15
            glow_target = 0.6
            scan_speed = 0.5
            bar_level = 0.7
            wave_amp = 4.0
        elif self.state == "thinking":
            self.target_audio_level = 0.1
            rotation_speed = 0.35
            glow_target = 0.9
            scan_speed = 1.5
            bar_level = 1.0
            wave_amp = 1.0
        else:  # speaking
            self.target_audio_level = 0.12 + (math.sin(t * 8) + 1) * 0.04
            rotation_speed = 0.25
            glow_target = 1.0
            scan_speed = 1.0
            bar_level = 0.9
            wave_amp = 5.0

        # Smooth transitions
        self.audio_level += (self.target_audio_level - self.audio_level) * 0.1
        self.glow_intensity += (glow_target - self.glow_intensity) * 0.08
        self.rotation_angle += rotation_speed
        self.scan_angle = (self.scan_angle + scan_speed) % 360

        cx, cy = self.hud_cx, self.hud_cy

        # --- Update segmented arcs ---
        for i, arc in enumerate(self.segment_items):
            base_start = i * 120 + self.rotation_angle * 30
            glow = self.glow_intensity
            color = self._fade_color(self.CYAN, glow)
            self.canvas.itemconfig(arc, start=base_start, outline=color)

        # --- Update scan line ---
        rad = math.radians(self.scan_angle)
        x2 = cx + math.cos(rad) * self.r_outer
        y2 = cy + math.sin(rad) * self.r_outer
        self.canvas.coords(self.scan_line, cx, cy, x2, y2)
        self.canvas.itemconfig(self.scan_line,
                               fill=self._fade_color(self.CYAN_BRIGHT,
                                                     self.glow_intensity))

        # --- Update glow rings ---
        for i, glow in enumerate(self.glow_items):
            alpha = max(0.15, self.glow_intensity - i * 0.2)
            color = self._fade_color(self.CYAN, alpha)
            self.canvas.itemconfig(glow, outline=color)
            # Pulse radius slightly
            pulse = math.sin(t * 2 + i) * 2
            r = self.r_inner + 6 + i * 4 + pulse
            self.canvas.coords(glow, cx - r, cy - r, cx + r, cy + r)

        # --- Update tick marks brightness ---
        for i, tick in enumerate(self.tick_items):
            is_major = i % 9 == 0
            phase = math.sin(t * 2 + i * 0.3)
            if is_major:
                alpha = 0.4 + phase * 0.2 * self.glow_intensity
            else:
                alpha = 0.2 + phase * 0.15 * self.glow_intensity
            self.canvas.itemconfig(tick,
                                   fill=self._fade_color(self.CYAN, alpha))

        # --- Update inner circle glow ---
        inner_color = self._fade_color(self.CYAN_DIM,
                                       0.3 + self.glow_intensity * 0.4)
        self.canvas.itemconfig(self.inner_circle, outline=inner_color)
        self.canvas.itemconfig(self.outer_ring,
                               outline=self._fade_color(self.CYAN_DIM,
                                                        0.3 + self.glow_intensity * 0.3))

        # --- Update center text glow ---
        text_color = self._fade_color(self.WHITE, 0.7 + self.glow_intensity * 0.3)
        self.canvas.itemconfig(self.center_text, fill=text_color)

        # --- Update status bars ---
        left_x = cx - self.r_connect - 90
        # System Status
        fill_w = 80 * (bar_level + math.sin(t * 3) * 0.05)
        self.canvas.coords(self.bar_sys_fill,
                           left_x, cy - 50, left_x + fill_w, cy - 42)
        # Voice Recognition
        v_level = bar_level * (0.7 + math.sin(t * 5) * 0.3)
        fill_w = 80 * v_level
        self.canvas.coords(self.bar_voice_fill,
                           left_x, cy + 10, left_x + fill_w, cy + 18)
        # Processing
        p_level = bar_level * (0.6 + math.sin(t * 4) * 0.4)
        fill_w = 80 * p_level
        self.canvas.coords(self.bar_proc_fill,
                           left_x, cy + 70, left_x + fill_w, cy + 78)
        self.canvas.itemconfig(self.bar_proc_text,
                               text=f"{int(p_level * 100)}%")

        # --- Update active indicator ---
        active_color = self._fade_color(self.CYAN, 0.5 + self.glow_intensity * 0.5)
        self.canvas.itemconfig(self.active_circle, outline=active_color)
        self.canvas.itemconfig(self.active_dot, fill=active_color)

        # --- Update system bars chart ---
        for bar, base_h in self.sys_bars:
            wobble = math.sin(t * 3 + base_h) * 3
            new_h = max(4, base_h + wobble)
            right_x = cx + self.r_connect + 60
            bx = right_x - 24 + (self.sys_bars.index((bar, base_h)) * 12)
            base_y = cy + 55
            self.canvas.coords(bar, bx - 3, base_y - new_h, bx + 3, base_y)

        # --- Update waveform ---
        wave_coords = []
        wave_w = 200
        segments = self.wave_points
        for i in range(segments):
            x = cx - wave_w // 2 + (i / segments) * wave_w
            # Multiple sine waves combined
            phase = t * 6 + i * 0.4
            y_off = (math.sin(phase) * 0.5 +
                     math.sin(phase * 1.7 + 1) * 0.3 +
                     math.sin(phase * 0.3 + 2) * 0.2)
            y = self.wave_y + y_off * self.wave_h * wave_amp * 0.15
            wave_coords.extend([x, y])
        if len(wave_coords) >= 4:
            self.canvas.coords(self.wave_line, *wave_coords)
            wave_color = self._fade_color(self.CYAN, 0.4 + self.glow_intensity * 0.5)
            self.canvas.itemconfig(self.wave_line, fill=wave_color)

        # --- Update connecting line pulse ---
        for line in [self.line_left_sys, self.line_left_voice,
                     self.line_right_active, self.line_right_sys]:
            pulse = 0.15 + self.glow_intensity * 0.3
            self.canvas.itemconfig(line,
                                   fill=self._fade_color(self.CYAN_DIM, pulse))

        # --- Footer text ---
        footer_texts = {
            "standby": "TEPUK 2X UNTUK MENGAKTIFKAN",
            "aktif": "SIAP MENERIMA PERINTAH",
            "listening": "SEDANG MENDENGARKAN...",
            "thinking": "AIRys SEDANG BERPIKIR...",
            "speaking": "AIRys SEDANG BERBICARA..."
        }
        self.canvas.itemconfig(self.footer_text,
                               text=footer_texts.get(self.state, ""))

        # Schedule next frame (~60fps)
        self.root.after(16, self._animate)

    # ------------------------------------------------------------------ #
    #                        PUBLIC API                                   #
    # ------------------------------------------------------------------ #
    def set_status(self, mode):
        """Set the HUD state: standby, aktif, listening, thinking, speaking."""
        mode_map = {
            "standby": "standby",
            "aktif": "aktif",
            "listening": "listening",
            "thinking": "thinking",
            "speaking": "speaking",
        }
        self.state = mode_map.get(mode, "standby")

    def tambah_pesan(self, pengirim, pesan):
        """Display a message in the message area."""
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

    def update_visualizer(self, amplitude):
        """Update visualizer with audio amplitude."""
        try:
            self.target_audio_level = max(0.02, min(1.0, amplitude))
        except Exception as e:
            print(f"Visualizer error: {e}")

    def run(self):
        """Start the Tkinter main loop."""
        self.root.mainloop()

    # ------------------------------------------------------------------ #
    #                         UTILITIES                                   #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _fade_color(hex_color, alpha):
        """Return a color mixed toward background for glow simulation."""
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        # Mix toward dark background
        bg_r, bg_g, bg_b = 0x05, 0x08, 0x10
        r = int(r * alpha + bg_r * (1 - alpha))
        g = int(g * alpha + bg_g * (1 - alpha))
        b = int(b * alpha + bg_b * (1 - alpha))
        return f"#{r:02x}{g:02x}{b:02x}"


# Global singleton for import
ui = None


def init_ui():
    global ui
    ui = AIRysUI()
    return ui


if __name__ == "__main__":
    app = AIRysUI()
    app.set_status("aktif")
    app.tambah_pesan("system", "Sistem dimulai")
    app.run()
