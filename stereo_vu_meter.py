
import json
import math
import os
import queue
import sys
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import numpy as np
    import sounddevice as sd
except ImportError:
    np = None
    sd = None

APP_NAME = "Stereo Analog VU Meter"
CONFIG_DIR = os.path.join(os.getenv("APPDATA", os.path.expanduser("~")), "StereoAnalogVUMeter")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")

DEFAULT_CONFIG = {
    "geometry": "980x430+160+160",
    "device": None,
    "samplerate": 48000,
    "blocksize": 1024
}


class AnalogMeter(tk.Canvas):
    def __init__(self, master, label="LEFT", **kwargs):
        super().__init__(
            master,
            bg="#050505",
            highlightthickness=0,
            bd=0,
            relief="flat",
            **kwargs
        )
        self.channel_label = label
        self.current_db = -40.0
        self.target_db = -40.0
        self.peak_db = -40.0
        self.peak_hold = 0
        self.bind("<Configure>", lambda _e: self.redraw())

    @staticmethod
    def db_to_norm(db):
        db = max(-40.0, min(3.0, db))
        # Compressed scale approximating classic analog VU behavior.
        if db <= -20:
            return (db + 40) / 20 * 0.20
        if db <= -10:
            return 0.20 + (db + 20) / 10 * 0.18
        if db <= -5:
            return 0.38 + (db + 10) / 5 * 0.16
        if db <= 0:
            return 0.54 + (db + 5) / 5 * 0.28
        return 0.82 + db / 3 * 0.18

    def set_level(self, db):
        self.target_db = max(-40.0, min(3.0, float(db)))
        if self.target_db > self.peak_db:
            self.peak_db = self.target_db
            self.peak_hold = 18
        elif self.peak_hold > 0:
            self.peak_hold -= 1
        else:
            self.peak_db = max(-40.0, self.peak_db - 0.45)

    def animate(self):
        attack = 0.32
        release = 0.10
        factor = attack if self.target_db > self.current_db else release
        self.current_db += (self.target_db - self.current_db) * factor
        self.redraw()

    def value_to_angle(self, db):
        norm = self.db_to_norm(db)
        return math.radians(145 - norm * 110)

    def redraw(self):
        self.delete("all")
        w = max(1, self.winfo_width())
        h = max(1, self.winfo_height())

        margin = max(12, int(min(w, h) * 0.05))
        self.create_rounded_rect(
            margin, margin, w - margin, h - margin,
            radius=max(16, int(min(w, h) * 0.05)),
            fill="#080808", outline="#2d183a", width=3
        )

        cx = w / 2
        cy = h * 0.84
        radius = min(w * 0.42, h * 0.70)

        # Scale arc
        self.create_arc(
            cx - radius, cy - radius, cx + radius, cy + radius,
            start=35, extent=110, style="arc",
            outline="#6f3f8f", width=max(2, int(radius * 0.015))
        )

        ticks = [-40, -30, -20, -10, -7, -5, -3, -2, -1, 0, 1, 2, 3]
        for db in ticks:
            a = self.value_to_angle(db)
            major = db in (-40, -30, -20, -10, -5, 0, 3)
            outer = radius
            inner = radius * (0.86 if major else 0.90)
            x1 = cx + math.cos(a) * inner
            y1 = cy - math.sin(a) * inner
            x2 = cx + math.cos(a) * outer
            y2 = cy - math.sin(a) * outer
            color = "#c06cff" if db <= 0 else "#ff4f79"
            self.create_line(x1, y1, x2, y2, fill=color, width=3 if major else 2)

            if major:
                tx = cx + math.cos(a) * radius * 0.74
                ty = cy - math.sin(a) * radius * 0.74
                self.create_text(
                    tx, ty, text=str(db),
                    fill=color,
                    font=("Segoe UI", max(8, int(radius * 0.075)), "bold")
                )

        self.create_text(
            cx, h * 0.15, text=self.channel_label,
            fill="#c06cff",
            font=("Segoe UI Semibold", max(11, int(h * 0.055)))
        )
        self.create_text(
            cx, h * 0.24, text="dB",
            fill="#7e4a9c",
            font=("Segoe UI", max(9, int(h * 0.04)), "bold")
        )

        # Needle
        a = self.value_to_angle(self.current_db)
        needle_len = radius * 0.83
        nx = cx + math.cos(a) * needle_len
        ny = cy - math.sin(a) * needle_len
        self.create_line(
            cx, cy, nx, ny,
            fill="#ff243f", width=max(3, int(radius * 0.018))
        )
        self.create_oval(
            cx - radius * 0.055, cy - radius * 0.055,
            cx + radius * 0.055, cy + radius * 0.055,
            fill="#c5142a", outline="#ff5f71", width=2
        )

        level_text = f"{self.current_db:5.1f} dB"
        self.create_text(
            cx, h * 0.90, text=level_text,
            fill="#c06cff",
            font=("Consolas", max(10, int(h * 0.045)), "bold")
        )

    def create_rounded_rect(self, x1, y1, x2, y2, radius=20, **kwargs):
        points = [
            x1 + radius, y1, x2 - radius, y1,
            x2, y1, x2, y1 + radius,
            x2, y2 - radius, x2, y2,
            x2 - radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius,
            x1, y1 + radius, x1, y1
        ]
        return self.create_polygon(points, smooth=True, splinesteps=24, **kwargs)


class AudioSetupDialog(tk.Toplevel):
    def __init__(self, parent, current_device, samplerate, blocksize, on_apply):
        super().__init__(parent)
        self.parent = parent
        self.on_apply = on_apply
        self.configure(bg="#101010")
        self.overrideredirect(True)
        self.transient(parent)
        self.grab_set()

        width, height = 560, 330
        px = parent.winfo_rootx() + max(0, (parent.winfo_width() - width) // 2)
        py = parent.winfo_rooty() + max(0, (parent.winfo_height() - height) // 2)
        self.geometry(f"{width}x{height}+{px}+{py}")

        outer = tk.Frame(self, bg="#2d183a")
        outer.pack(fill="both", expand=True, padx=2, pady=2)
        body = tk.Frame(outer, bg="#101010")
        body.pack(fill="both", expand=True, padx=1, pady=1)

        titlebar = tk.Frame(body, bg="#171019", height=42)
        titlebar.pack(fill="x")
        titlebar.pack_propagate(False)
        title = tk.Label(
            titlebar, text="AUDIO SETUP", bg="#171019",
            fg="#c06cff", font=("Segoe UI Semibold", 12)
        )
        title.pack(side="left", padx=14)

        close_btn = tk.Button(
            titlebar, text="✕", command=self.destroy,
            bg="#171019", fg="#ff5f71", activebackground="#2b1620",
            activeforeground="#ffffff", bd=0, font=("Segoe UI", 13),
            cursor="hand2"
        )
        close_btn.pack(side="right", padx=8)

        for widget in (titlebar, title):
            widget.bind("<ButtonPress-1>", self._drag_start)
            widget.bind("<B1-Motion>", self._drag_move)

        content = tk.Frame(body, bg="#101010")
        content.pack(fill="both", expand=True, padx=22, pady=20)

        tk.Label(
            content, text="Stereo input device",
            bg="#101010", fg="#d7c2e5", font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        self.device_map = {}
        device_names = []
        if sd is not None:
            try:
                for idx, dev in enumerate(sd.query_devices()):
                    if int(dev.get("max_input_channels", 0)) >= 2:
                        name = f"{idx}: {dev['name']}"
                        device_names.append(name)
                        self.device_map[name] = idx
            except Exception:
                pass

        self.device_var = tk.StringVar()
        combo = ttk.Combobox(
            content, textvariable=self.device_var,
            values=device_names, state="readonly", font=("Segoe UI", 10)
        )
        combo.pack(fill="x", pady=(6, 18))

        selected_name = None
        for name, idx in self.device_map.items():
            if idx == current_device:
                selected_name = name
                break
        if selected_name:
            self.device_var.set(selected_name)
        elif device_names:
            self.device_var.set(device_names[0])

        row = tk.Frame(content, bg="#101010")
        row.pack(fill="x")

        tk.Label(row, text="Sample rate", bg="#101010", fg="#d7c2e5").grid(row=0, column=0, sticky="w")
        self.rate_var = tk.StringVar(value=str(samplerate))
        ttk.Combobox(
            row, textvariable=self.rate_var,
            values=["44100", "48000", "96000"],
            state="readonly", width=12
        ).grid(row=1, column=0, sticky="w", pady=(5, 0))

        tk.Label(row, text="Block size", bg="#101010", fg="#d7c2e5").grid(row=0, column=1, sticky="w", padx=(24, 0))
        self.block_var = tk.StringVar(value=str(blocksize))
        ttk.Combobox(
            row, textvariable=self.block_var,
            values=["256", "512", "1024", "2048"],
            state="readonly", width=12
        ).grid(row=1, column=1, sticky="w", padx=(24, 0), pady=(5, 0))

        tk.Label(
            content,
            text="Only devices with at least two input channels are listed.",
            bg="#101010", fg="#75667d", font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(18, 0))

        buttons = tk.Frame(content, bg="#101010")
        buttons.pack(side="bottom", fill="x")
        tk.Button(
            buttons, text="CANCEL", command=self.destroy,
            bg="#262026", fg="#d7c2e5", activebackground="#383038",
            activeforeground="#ffffff", bd=0, padx=20, pady=8,
            cursor="hand2"
        ).pack(side="right")
        tk.Button(
            buttons, text="APPLY", command=self.apply,
            bg="#5b2b75", fg="#ffffff", activebackground="#754092",
            activeforeground="#ffffff", bd=0, padx=22, pady=8,
            cursor="hand2"
        ).pack(side="right", padx=(0, 10))

    def _drag_start(self, event):
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def _drag_move(self, event):
        self.geometry(f"+{event.x_root - self._drag_x}+{event.y_root - self._drag_y}")

    def apply(self):
        name = self.device_var.get()
        if not name:
            messagebox.showerror("Audio Setup", "No stereo input device is available.", parent=self)
            return
        self.on_apply(
            self.device_map[name],
            int(self.rate_var.get()),
            int(self.block_var.get())
        )
        self.destroy()


class VUMeterApp(tk.Tk):
    MIN_W = 720
    MIN_H = 320

    def __init__(self):
        super().__init__()
        self.config_data = self.load_config()
        self.geometry(self.config_data.get("geometry", DEFAULT_CONFIG["geometry"]))
        self.minsize(self.MIN_W, self.MIN_H)
        self.overrideredirect(True)
        self.configure(bg="#080808")

        self.audio_queue = queue.Queue(maxsize=8)
        self.stream = None
        self.device = self.config_data.get("device")
        self.samplerate = int(self.config_data.get("samplerate", 48000))
        self.blocksize = int(self.config_data.get("blocksize", 1024))
        self.running = False

        self._drag_offset = None
        self._resize_start = None
        self._resize_geom = None

        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.after(60, self.process_audio)
        self.after(200, self.start_audio)

    def build_ui(self):
        outer = tk.Frame(self, bg="#2d183a")
        outer.pack(fill="both", expand=True, padx=2, pady=2)

        main = tk.Frame(outer, bg="#080808")
        main.pack(fill="both", expand=True, padx=1, pady=1)

        titlebar = tk.Frame(main, bg="#141014", height=46)
        titlebar.pack(fill="x")
        titlebar.pack_propagate(False)

        title = tk.Label(
            titlebar, text="STEREO ANALOG VU METER",
            bg="#141014", fg="#c06cff",
            font=("Segoe UI Semibold", 12)
        )
        title.pack(side="left", padx=15)

        self.status_var = tk.StringVar(value="AUDIO OFFLINE")
        status = tk.Label(
            titlebar, textvariable=self.status_var,
            bg="#141014", fg="#75667d",
            font=("Segoe UI", 9, "bold")
        )
        status.pack(side="left", padx=(16, 0))

        setup_btn = tk.Button(
            titlebar, text="SETUP", command=self.open_setup,
            bg="#2d183a", fg="#dcb7f0",
            activebackground="#4a275c", activeforeground="#ffffff",
            bd=0, padx=14, pady=5, cursor="hand2",
            font=("Segoe UI", 9, "bold")
        )
        setup_btn.pack(side="right", padx=(0, 8))

        close_btn = tk.Button(
            titlebar, text="✕", command=self.close_app,
            bg="#141014", fg="#ff5f71",
            activebackground="#2b1620", activeforeground="#ffffff",
            bd=0, padx=12, cursor="hand2",
            font=("Segoe UI", 13)
        )
        close_btn.pack(side="right")

        min_btn = tk.Button(
            titlebar, text="—", command=self.minimize,
            bg="#141014", fg="#c06cff",
            activebackground="#291d2e", activeforeground="#ffffff",
            bd=0, padx=12, cursor="hand2",
            font=("Segoe UI", 13)
        )
        min_btn.pack(side="right")

        for widget in (titlebar, title, status):
            widget.bind("<ButtonPress-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.drag_window)
            widget.bind("<Double-Button-1>", self.toggle_maximize)

        meters = tk.Frame(main, bg="#080808")
        meters.pack(fill="both", expand=True, padx=10, pady=(10, 14))
        meters.grid_columnconfigure(0, weight=1, uniform="meters")
        meters.grid_columnconfigure(1, weight=1, uniform="meters")
        meters.grid_rowconfigure(0, weight=1)

        self.left_meter = AnalogMeter(meters, label="LEFT")
        self.left_meter.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.right_meter = AnalogMeter(meters, label="RIGHT")
        self.right_meter.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        self.resize_grip = tk.Label(
            main, text="◢", bg="#080808", fg="#6f3f8f",
            font=("Segoe UI Symbol", 13), cursor="size_nw_se"
        )
        self.resize_grip.place(relx=1.0, rely=1.0, anchor="se", x=-3, y=-2)
        self.resize_grip.bind("<ButtonPress-1>", self.start_resize)
        self.resize_grip.bind("<B1-Motion>", self.resize_window)

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            result = DEFAULT_CONFIG.copy()
            result.update(data)
            return result
        except Exception:
            return DEFAULT_CONFIG.copy()

    def save_config(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self.config_data.update({
            "geometry": self.geometry(),
            "device": self.device,
            "samplerate": self.samplerate,
            "blocksize": self.blocksize
        })
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2)
        except Exception:
            pass

    def start_drag(self, event):
        self._drag_offset = (event.x_root - self.winfo_x(), event.y_root - self.winfo_y())

    def drag_window(self, event):
        if self._drag_offset:
            x = event.x_root - self._drag_offset[0]
            y = event.y_root - self._drag_offset[1]
            self.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self._resize_start = (event.x_root, event.y_root)
        self._resize_geom = (self.winfo_width(), self.winfo_height())

    def resize_window(self, event):
        if not self._resize_start:
            return
        dx = event.x_root - self._resize_start[0]
        dy = event.y_root - self._resize_start[1]
        w = max(self.MIN_W, self._resize_geom[0] + dx)
        h = max(self.MIN_H, self._resize_geom[1] + dy)
        self.geometry(f"{w}x{h}")

    def toggle_maximize(self, _event=None):
        if getattr(self, "_maximized", False):
            self.geometry(getattr(self, "_restore_geometry", DEFAULT_CONFIG["geometry"]))
            self._maximized = False
        else:
            self._restore_geometry = self.geometry()
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            self.geometry(f"{sw}x{sh}+0+0")
            self._maximized = True

    def minimize(self):
        self.overrideredirect(False)
        self.iconify()
        self.bind("<Map>", self.restore_borderless, add="+")

    def restore_borderless(self, _event=None):
        if self.state() == "normal":
            self.overrideredirect(True)
            self.unbind("<Map>")

    def open_setup(self):
        AudioSetupDialog(
            self, self.device, self.samplerate, self.blocksize,
            self.apply_audio_settings
        )

    def apply_audio_settings(self, device, samplerate, blocksize):
        self.device = device
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.save_config()
        self.start_audio()

    def stop_audio(self):
        self.running = False
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

    def start_audio(self):
        self.stop_audio()
        if sd is None or np is None:
            self.status_var.set("INSTALL DEPENDENCIES")
            self.status_var.configure(fg="#ff5f71")
            return

        try:
            if self.device is None:
                default_input = sd.default.device[0]
                if default_input is not None and default_input >= 0:
                    info = sd.query_devices(default_input)
                    if int(info["max_input_channels"]) >= 2:
                        self.device = int(default_input)

            if self.device is None:
                self.status_var.set("SELECT A STEREO INPUT")
                self.status_var.configure(fg="#ff5f71")
                return

            def callback(indata, frames, time_info, status):
                if status:
                    pass
                if indata.shape[1] < 2:
                    return
                rms = np.sqrt(np.mean(np.square(indata[:, :2]), axis=0) + 1e-12)
                db = 20.0 * np.log10(rms)
                try:
                    self.audio_queue.put_nowait((float(db[0]), float(db[1])))
                except queue.Full:
                    try:
                        self.audio_queue.get_nowait()
                    except queue.Empty:
                        pass

            self.stream = sd.InputStream(
                device=self.device,
                channels=2,
                samplerate=self.samplerate,
                blocksize=self.blocksize,
                dtype="float32",
                callback=callback
            )
            self.stream.start()
            self.running = True
            dev_name = sd.query_devices(self.device)["name"]
            self.status_var.set(f"LIVE • {dev_name}")
            self.status_var.configure(fg="#7bd88f")
        except Exception as exc:
            self.status_var.set("AUDIO ERROR")
            self.status_var.configure(fg="#ff5f71")
            messagebox.showerror(
                "Audio Error",
                f"Could not start the selected input device.\n\n{exc}",
                parent=self
            )

    def process_audio(self):
        latest = None
        try:
            while True:
                latest = self.audio_queue.get_nowait()
        except queue.Empty:
            pass

        if latest is not None:
            self.left_meter.set_level(latest[0])
            self.right_meter.set_level(latest[1])
        elif not self.running:
            self.left_meter.set_level(-40.0)
            self.right_meter.set_level(-40.0)

        self.left_meter.animate()
        self.right_meter.animate()
        self.after(33, self.process_audio)

    def close_app(self):
        self.save_config()
        self.stop_audio()
        self.destroy()


def main():
    app = VUMeterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
