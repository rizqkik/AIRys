import tkinter as tk
import time
import math
import random


class AIRysUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AIRys Core")
        self.root.geometry("360x500")
        self.root.configure(bg="#010409")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        self.root.geometry("360x500+{}+{}".format(
            self.root.winfo_screenwidth() - 380,
            self.root.winfo_screenheight() - 550
        ))

        self.state = "idle"
        self.frame_count = 0
        self.audio_level = 0.0
        self.target_audio_level = 0.0
        self.nodes = []
        self.node_links = []
        self.orbit_lines = []
        self.mesh_lines = []
        self.frame_lines = []
        self.frame_nodes = []
        self.wave_values = [0.02] * 28
        self.target_wave_values = [0.02] * 28
        self.wave_items = []

        self.state_colors = {
            "idle": "#6f849a",
            "listening": "#7ed6ff",
            "thinking": "#a8b7ff",
            "speaking": "#9fffee",
        }

        self._build_ui()
        self.animate()

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#010409")
        header.pack(pady=(15, 0))

        tk.Label(
            header,
            text="AIRys",
            font=("Segoe UI", 23, "bold"),
            fg="#f2f8ff",
            bg="#010409"
        ).pack()

        tk.Label(
            header,
            text="WIRELIGHT NEURAL CORE",
            font=("Segoe UI", 7),
            fg="#34445a",
            bg="#010409"
        ).pack(pady=(0, 3))

        self.status_label = tk.Label(
            self.root,
            text="standby",
            font=("Segoe UI", 9),
            fg="#6f849a",
            bg="#010409"
        )
        self.status_label.pack(pady=(0, 5))

        self.core_canvas = tk.Canvas(
            self.root,
            width=300,
            height=292,
            bg="#010409",
            highlightthickness=0
        )
        self.core_canvas.pack(pady=(0, 0))

        self.outer_glow = self.core_canvas.create_oval(48, 30, 252, 234, outline="#07111c", width=1)
        self.inner_glow = self.core_canvas.create_oval(76, 58, 224, 206, outline="#081827", width=1)
        self.scan_arc = self.core_canvas.create_arc(
            48, 30, 252, 234,
            start=0,
            extent=82,
            style="arc",
            outline="#15314a",
            width=2
        )

        self._create_wireframe_assets()

        for i in range(28):
            x = 28 + i * 9
            item = self.core_canvas.create_line(x, 270, x, 270, fill="#26384c", width=1, capstyle="round")
            self.wave_items.append(item)

        self.message_frame = tk.Frame(
            self.root,
            bg="#050912",
            height=54,
            highlightbackground="#101b2a",
            highlightthickness=1
        )
        self.message_frame.pack(fill="x", padx=22, pady=(0, 8))
        self.message_frame.pack_propagate(False)

        self.interaction_label = tk.Label(
            self.message_frame,
            text="",
            bg="#050912",
            fg="#bdcad8",
            font=("Segoe UI", 9),
            justify="left",
            anchor="nw",
            wraplength=292
        )
        self.interaction_label.pack(fill="both", expand=True, padx=10, pady=7)

        self.footer_label = tk.Label(
            self.root,
            text="tepuk 2x untuk mengaktifkan",
            font=("Segoe UI", 8),
            fg="#34445a",
            bg="#010409"
        )
        self.footer_label.pack(pady=(0, 8))

    def _create_wireframe_assets(self):
        random.seed(23)

        for _ in range(10):
            item = self.core_canvas.create_line(0, 0, 0, 0, fill="#0a1724", width=1)
            self.frame_lines.append({"item": item})

        for _ in range(6):
            item = self.core_canvas.create_oval(0, 0, 0, 0, fill="#31526d", outline="")
            self.frame_nodes.append(item)

        for _ in range(9):
            item = self.core_canvas.create_line(0, 0, 0, 0, fill="#12304a", width=1, smooth=True)
            self.orbit_lines.append({
                "item": item,
                "tilt": random.uniform(-0.72, 0.72),
                "phase": random.uniform(0, math.tau),
                "scale": random.uniform(0.78, 1.08),
                "speed": random.uniform(0.32, 0.62),
            })

        for y in [-0.7, -0.42, -0.16, 0.12, 0.38, 0.64]:
            item = self.core_canvas.create_line(0, 0, 0, 0, fill="#10273d", width=1, smooth=True)
            self.mesh_lines.append({"item": item, "type": "lat", "value": y})

        for angle in [0.0, 0.65, 1.3, 1.95, 2.6]:
            item = self.core_canvas.create_line(0, 0, 0, 0, fill="#0d2338", width=1, smooth=True)
            self.mesh_lines.append({"item": item, "type": "mer", "value": angle})

        for _ in range(72):
            theta = random.uniform(0, math.tau)
            y = random.uniform(-0.9, 0.9)
            ring_radius = math.sqrt(max(0.0, 1.0 - y * y))
            node = {
                "x": math.cos(theta) * ring_radius,
                "y": y,
                "z": math.sin(theta) * ring_radius,
                "phase": random.uniform(0, math.tau),
                "size": random.choice([1.0, 1.15, 1.3, 1.6]),
                "item": self.core_canvas.create_oval(0, 0, 0, 0, fill="#5a86a8", outline=""),
            }
            self.nodes.append(node)

        for _ in range(58):
            a = random.randrange(len(self.nodes))
            b = random.randrange(len(self.nodes))
            if a != b:
                item = self.core_canvas.create_line(0, 0, 0, 0, fill="#0e263c", width=1)
                self.node_links.append({"a": a, "b": b, "item": item})

    def tambah_pesan(self, pengirim, pesan):
        """Thread-safe message addition."""
        try:
            if pengirim == "airys":
                content = f"AIRys: {pesan}"
            elif pengirim == "user":
                content = f"Bos Rizqi: {pesan}"
            else:
                content = pesan
            self.interaction_label.config(text=content)
        except Exception as e:
            print(f"UI error: {e}")

    def _mix(self, c1, c2, amount):
        amount = max(0.0, min(1.0, amount))
        c1 = c1.lstrip("#")
        c2 = c2.lstrip("#")
        r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
        r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
        r = int(r1 + (r2 - r1) * amount)
        g = int(g1 + (g2 - g1) * amount)
        b = int(b1 + (b2 - b1) * amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _project(self, x, y, z, angle_y, angle_x, rx, ry, cx, cy):
        cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
        cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)

        xz = x * cos_y - z * sin_y
        zz = x * sin_y + z * cos_y
        yy = y * cos_x - zz * sin_x
        zz = y * sin_x + zz * cos_x

        depth = (zz + 1.25) / 2.5
        perspective = 0.76 + depth * 0.16
        px = cx + xz * rx * perspective
        py = cy + yy * ry * perspective
        return px, py, yy, zz, depth

    def _draw_line(self, item, coords, color, width=1):
        flat = []
        for x, y in coords:
            flat.extend([x, y])
        self.core_canvas.coords(item, *flat)
        self.core_canvas.itemconfig(item, fill=color, width=width)

    def _sphere_point(self, angle, y, angle_y, angle_x, rx, ry, cx, cy):
        radius = math.sqrt(max(0.0, 1.0 - y * y))
        return self._project(
            math.cos(angle) * radius,
            y,
            math.sin(angle) * radius,
            angle_y,
            angle_x,
            rx,
            ry,
            cx,
            cy
        )

    def animate(self):
        self.frame_count += 1
        t = time.time()

        if self.state == "idle":
            self.target_audio_level = 0.022 + (math.sin(t * 1.0) + 1) * 0.006
            rotation = 0.11
            activity = 0.36
        elif self.state == "listening":
            self.target_audio_level = 0.07 + (math.sin(t * 2.1) + 1) * 0.014
            rotation = 0.21
            activity = 0.72
        elif self.state == "thinking":
            self.target_audio_level = 0.095 + (math.sin(t * 2.8) + 1) * 0.018
            rotation = 0.28
            activity = 0.96
        else:  # speaking
            rotation = 0.2 + self.target_audio_level * 0.1
            activity = 1.08 + self.target_audio_level * 0.8

        self.audio_level += (self.target_audio_level - self.audio_level) * 0.16
        accent = self.state_colors.get(self.state, "#6f849a")
        cx, cy = 150, 136
        base_radius = 88 + self.audio_level * 18
        rx = base_radius
        ry = base_radius * 0.9
        angle_y = t * rotation
        angle_x = math.sin(t * 0.18) * 0.1

        halo_radius = base_radius + 21 + math.sin(t * 1.2) * 1.4
        self.core_canvas.coords(self.outer_glow, cx - halo_radius, cy - halo_radius, cx + halo_radius, cy + halo_radius)
        self.core_canvas.coords(self.inner_glow, cx - halo_radius * 0.73, cy - halo_radius * 0.73, cx + halo_radius * 0.73, cy + halo_radius * 0.73)
        self.core_canvas.itemconfig(self.outer_glow, outline=self._mix("#02070d", accent, 0.2))
        self.core_canvas.itemconfig(self.inner_glow, outline=self._mix("#02070d", accent, 0.13))
        self.core_canvas.itemconfig(self.scan_arc, start=(t * 30 * (1 + activity)) % 360, outline=self._mix("#07111d", accent, 0.62))

        frame_base = [
            (-1.12, -0.92, 0.12),
            (1.08, -0.82, -0.06),
            (0.9, 0.86, 0.08),
            (-0.98, 0.76, -0.12),
            (0.0, -1.28, 0.0),
            (0.0, 1.18, 0.0),
        ]
        frame_points = []
        for x, y, z in frame_base:
            px, py, _, _, _ = self._project(x, y, z, angle_y * 0.45, angle_x, rx * 1.18, ry * 1.18, cx, cy)
            frame_points.append((px, py))

        frame_edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 0), (4, 1), (4, 2), (4, 3), (5, 0), (5, 1)]
        for i, edge in enumerate(frame_edges):
            a, b = edge
            self.core_canvas.coords(self.frame_lines[i]["item"], *frame_points[a], *frame_points[b])
            self.core_canvas.itemconfig(self.frame_lines[i]["item"], fill=self._mix("#050c14", accent, 0.28), width=1)

        for item, point in zip(self.frame_nodes, frame_points):
            x, y = point
            size = 1.9 + self.audio_level * 1.0
            self.core_canvas.coords(item, x - size, y - size, x + size, y + size)
            self.core_canvas.itemconfig(item, fill=self._mix("#193047", accent, 0.68))

        for mesh in self.mesh_lines:
            coords = []
            if mesh["type"] == "lat":
                y = mesh["value"]
                for step in range(52):
                    theta = math.tau * step / 51
                    px, py, _, zz, _ = self._sphere_point(theta, y, angle_y, angle_x, rx, ry, cx, cy)
                    if zz > -0.98:
                        coords.append((px, py))
            else:
                angle = mesh["value"] + angle_y * 0.36
                for step in range(56):
                    y = -1 + 2 * step / 55
                    px, py, _, zz, _ = self._sphere_point(angle, y, angle_y, angle_x, rx, ry, cx, cy)
                    if zz > -1.0:
                        coords.append((px, py))
            if len(coords) > 2:
                self._draw_line(mesh["item"], coords, self._mix("#06101a", accent, 0.18))

        for orbit in self.orbit_lines:
            coords = []
            orbit_angle = angle_y * orbit["speed"] + orbit["phase"]
            tilt = orbit["tilt"]
            scale = orbit["scale"] + self.audio_level * 0.05
            for step in range(72):
                theta = math.tau * step / 71
                x = math.cos(theta) * scale
                z = math.sin(theta) * scale
                y = math.sin(theta + orbit_angle) * tilt * 0.24
                px, py, _, zz, _ = self._project(x, y, z, angle_y + orbit_angle * 0.14, angle_x + tilt * 0.06, rx, ry, cx, cy)
                if zz > -1.05:
                    coords.append((px, py))
            if len(coords) > 2:
                color = self._mix("#07111d", accent, 0.22 + self.audio_level * 0.16)
                self._draw_line(orbit["item"], coords, color)

        projected_nodes = []
        for node in self.nodes:
            pulse = math.sin(t * 1.35 + node["phase"]) * 0.004 * activity
            px, py, yy, zz, depth = self._project(
                node["x"] * (1 + pulse),
                node["y"] * (1 + pulse),
                node["z"] * (1 + pulse),
                angle_y,
                angle_x,
                rx,
                ry,
                cx,
                cy
            )
            projected_nodes.append((px, py, depth))
            light = 0.25 + depth * 0.62 + (math.sin(t * 2.1 + node["phase"]) + 1) * 0.025
            color = self._mix("#07111d", accent, light)
            size = node["size"] + depth * 0.9 + self.audio_level * 0.85
            self.core_canvas.coords(node["item"], px - size, py - size, px + size, py + size)
            self.core_canvas.itemconfig(node["item"], fill=color)

        for link in self.node_links:
            ax, ay, ad = projected_nodes[link["a"]]
            bx, by, bd = projected_nodes[link["b"]]
            if abs(ax - bx) < 82 and abs(ay - by) < 82:
                color = self._mix("#040a11", accent, 0.14 + min(ad, bd) * 0.18)
                self.core_canvas.coords(link["item"], ax, ay, bx, by)
                self.core_canvas.itemconfig(link["item"], fill=color)
            else:
                self.core_canvas.coords(link["item"], 0, 0, 0, 0)

        if self.state != "speaking" and self.frame_count % 6 == 0:
            for i in range(len(self.target_wave_values)):
                phase = t * 2.4 + i * 0.42
                if self.state == "idle":
                    self.target_wave_values[i] = 0.012 + abs(math.sin(phase)) * 0.018
                elif self.state == "listening":
                    self.target_wave_values[i] = 0.03 + abs(math.sin(phase)) * 0.06
                else:
                    self.target_wave_values[i] = 0.05 + abs(math.sin(phase)) * 0.1

        for i, item in enumerate(self.wave_items):
            self.wave_values[i] += (self.target_wave_values[i] - self.wave_values[i]) * 0.24
            height = 2 + self.wave_values[i] * 30
            x = 28 + i * 9
            self.core_canvas.coords(item, x, 270 - height / 2, x, 270 + height / 2)
            self.core_canvas.itemconfig(item, fill=self._mix("#07111d", accent, 0.72))

        self.root.after(16, self.animate)

    def set_state(self, state):
        self.state = state

    def update_visualizer(self, amplitude):
        """Update visualizer with audio amplitude (thread-safe)."""
        try:
            amplitude = max(0.02, min(1.0, amplitude))
            self.target_audio_level = amplitude
            t = time.time()
            for i in range(len(self.target_wave_values)):
                center_bias = 1.0 - abs(i - 13.5) / 17
                ripple = 0.74 + math.sin(t * 14 + i * 0.72) * 0.16
                self.target_wave_values[i] = max(0.018, min(1.0, amplitude * center_bias * ripple))
        except Exception as e:
            print(f"Visualizer error: {e}")

    def set_status(self, mode):
        """Set status display (thread-safe)."""
        try:
            modes = {
                "standby": ("standby", "#6f849a", "tepuk 2x untuk mengaktifkan"),
                "aktif": ("aktif", "#8295aa", "siap menerima perintah"),
                "listening": ("mendengarkan...", "#7ed6ff", "sedang mendengarkan"),
                "thinking": ("berpikir...", "#a8b7ff", "AIRys sedang berpikir"),
                "speaking": ("berbicara...", "#9fffee", "AIRys sedang berbicara"),
            }
            text, color, footer = modes.get(mode, modes["standby"])
            self.status_label.config(text=text, fg=color)
            self.footer_label.config(text=footer)
            if mode == "speaking":
                self.set_state("speaking")
            elif mode == "listening":
                self.set_state("listening")
            elif mode == "thinking":
                self.set_state("thinking")
            elif mode in ["standby", "aktif"]:
                self.set_state("idle")
        except Exception as e:
            print(f"Status error: {e}")

    def run(self):
        self.root.mainloop()


ui = None


def init_ui():
    global ui
    ui = AIRysUI()
    return ui


if __name__ == "__main__":
    ui = AIRysUI()
    ui.tambah_pesan("system", "— sistem dimulai —")
    ui.tambah_pesan("airys", "Selamat malam Bos Rizqi, sistem aktif.")
    ui.set_status("aktif")
    ui.tambah_pesan("user", "Airis, buka Chrome.")
    ui.tambah_pesan("airys", "Baik Bos Rizqi, Chrome dibuka sekarang.")
    ui.run()
