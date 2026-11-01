import socket
import threading
import tkinter as tk
from tkinter import messagebox
import pyvjoystick.vigem as vg

HOST = "0.0.0.0"
DEFAULT_PORT = 65432

# ── server / joystick state ────────────────────────────────────────────────────

_server: socket.socket | None = None
_server_thread: threading.Thread | None = None

axisLX = float(0)
axisLY = float(0)
axisRX = float(0)
axisRY = float(0)

# ── networking helpers ─────────────────────────────────────────────────────────

def create_server(host: str = HOST, port: int = DEFAULT_PORT) -> socket.socket:
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server.bind((host, port))
        print(f"Server successfully started on {host}:{port}")
        return server
    except Exception as exc:
        print(f"Failed to start server: {exc}")
        raise

def close_server(server: socket.socket):
    server.close()
    print("Server closed")

# ── joystick loop (runs in background thread) ──────────────────────────────────

def joystick_control(server: socket.socket):
    global axisLX, axisLY, axisRX, axisRY

    gp = vg.VX360Gamepad()
    XBUTTON_MAPPER = {
        "304": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
        "305": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
        "307": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
        "308": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
        "315": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
        "314": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        "317": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
        "318": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
        "310": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
        "311": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
        "DPU": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
        "DPD": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
        "DPL": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
        "DPR": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    }
    try:
        while True:
            data, addr = server.recvfrom(1024)
            recv_input: str = data.decode("utf-8")
            if ":" in recv_input:
                data_members = recv_input.split(":")
                if data_members[0] == "BTN":
                    if data_members[2] == "1":
                        gp.press_button(button=XBUTTON_MAPPER[data_members[1]])
                    elif data_members[2] == "0":
                        gp.release_button(button=XBUTTON_MAPPER[data_members[1]])
                if data_members[0] == "AXIS":
                    if data_members[1] == "17":
                        if data_members[2] == "-1":
                            gp.press_button(button=XBUTTON_MAPPER["DPU"])
                        elif data_members[2] == "1":
                            gp.press_button(button=XBUTTON_MAPPER["DPD"])
                        else:
                            gp.release_button(button=XBUTTON_MAPPER["DPU"])
                            gp.release_button(button=XBUTTON_MAPPER["DPD"])
                    if data_members[1] == "16":
                        if data_members[2] == "-1":
                            gp.press_button(button=XBUTTON_MAPPER["DPL"])
                        elif data_members[2] == "1":
                            gp.press_button(button=XBUTTON_MAPPER["DPR"])
                        else:
                            gp.release_button(button=XBUTTON_MAPPER["DPL"])
                            gp.release_button(button=XBUTTON_MAPPER["DPR"])
                if data_members[1] == "5":
                    gp.left_trigger_float(float(data_members[2]) / 1023)
                if data_members[1] == "2":
                    gp.right_trigger_float(float(data_members[2]) / 1023)
                if data_members[1] == "0":
                    axisLX = float(data_members[2]) / 32767
                if data_members[1] == "1":
                    axisLY = float(data_members[2]) / -32767
                if data_members[1] == "3":
                    axisRX = float(data_members[2]) / 32767
                if data_members[1] == "4":
                    axisRY = float(data_members[2]) / -32767
                gp.left_joystick_float(x_value_float=axisLX, y_value_float=axisLY)
                gp.right_joystick_float(x_value_float=axisRX, y_value_float=axisRY)
                gp.update()
    except OSError:
        print("Server socket closed, joystick loop stopped.")
    except Exception as exc:
        print(f"Joystick loop error: {exc}")

# ── colour palette ─────────────────────────────────────────────────────────────

C = {
    "bg":        "#0d0d12",
    "surface":   "#16161f",
    "surface2":  "#1e1e2a",
    "border":    "#2a2a3d",
    "accent":    "#6d28d9",
    "accent2":   "#8b5cf6",
    "green":     "#16a34a",
    "green_h":   "#22c55e",
    "green_glow":"#052e16",
    "red":       "#dc2626",
    "red_h":     "#ef4444",
    "text":      "#f1f5f9",
    "text2":     "#94a3b8",
    "muted":     "#475569",
    "entry_bg":  "#0a0a10",
}

# ── custom rounded button ──────────────────────────────────────────────────────

class RoundButton(tk.Canvas):
    """Canvas button with rounded corners that updates label/colour at runtime."""

    W, H, R = 280, 44, 11

    def __init__(self, parent, label, bg, hover, command):
        super().__init__(
            parent,
            width=self.W, height=self.H,
            bg=C["surface2"], highlightthickness=0, cursor="hand2",
        )
        self._label   = label
        self._bg      = bg
        self._hover   = hover
        self._command = command
        self._over    = False
        self._draw(bg)
        self.bind("<Enter>",    lambda _: self._enter())
        self.bind("<Leave>",    lambda _: self._leave())
        self.bind("<Button-1>", lambda _: self._click())

    def _draw(self, fill):
        w, h, r = self.W, self.H, self.R
        self.delete("all")
        # filled rounded rectangle built from arcs + rects
        for x0, y0, x1, y1, start in (
            (0,     0,     2*r,   2*r,   90),
            (w-2*r, 0,     w,     2*r,   0),
            (0,     h-2*r, 2*r,   h,     180),
            (w-2*r, h-2*r, w,     h,     270),
        ):
            self.create_arc(x0, y0, x1, y1, start=start, extent=90,
                            fill=fill, outline=fill)
        self.create_rectangle(r, 0, w-r, h, fill=fill, outline=fill)
        self.create_rectangle(0, r, w, h-r, fill=fill, outline=fill)
        self.create_text(w // 2, h // 2, text=self._label,
                         fill="white", font=("Segoe UI", 10, "bold"))

    def set_style(self, label: str, bg: str, hover: str):
        self._label = label
        self._bg    = bg
        self._hover = hover
        self._draw(hover if self._over else bg)

    def _enter(self):
        self._over = True
        self._draw(self._hover)

    def _leave(self):
        self._over = False
        self._draw(self._bg)

    def _click(self):
        self._command()


# ── main window ────────────────────────────────────────────────────────────────

class JoystickServerApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Joystick Server")
        self.resizable(False, False)
        self.configure(bg=C["bg"])
        self._running   = False
        self._pulse_on  = False
        self._build_ui()

    # ── layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # gradient-like top bar (two thin strips)
        tk.Frame(self, bg=C["accent"],  height=3).pack(fill="x")
        tk.Frame(self, bg=C["accent2"], height=1).pack(fill="x")

        # ── header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=C["bg"], pady=18)
        hdr.pack(fill="x")

        icon_lbl = tk.Label(hdr, text="🎮", font=("Segoe UI", 26),
                            bg=C["bg"], fg=C["text"])
        icon_lbl.pack()
        tk.Label(hdr, text="Joystick Server",
                 font=("Segoe UI", 15, "bold"),
                 fg=C["text"], bg=C["bg"]).pack()
        tk.Label(hdr, text="Virtual gamepad via UDP",
                 font=("Segoe UI", 9),
                 fg=C["text2"], bg=C["bg"]).pack(pady=(2, 0))

        # ── card ──────────────────────────────────────────────────────────────
        card = tk.Frame(self, bg=C["surface"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(padx=28, pady=(4, 20), fill="x")

        inner = tk.Frame(card, bg=C["surface"], padx=22, pady=22)
        inner.pack(fill="x")

        # port label row
        port_hdr = tk.Frame(inner, bg=C["surface"])
        port_hdr.pack(fill="x", pady=(0, 4))
        tk.Label(port_hdr, text="SERVER PORT",
                 font=("Segoe UI", 8, "bold"),
                 fg=C["text2"], bg=C["surface"]).pack(side="left")

        # port entry with accent border
        ef = tk.Frame(inner, bg=C["entry_bg"],
                      highlightbackground=C["accent2"], highlightthickness=1)
        ef.pack(fill="x", pady=(0, 18))

        self.port_var = tk.StringVar(value=str(DEFAULT_PORT))
        self.port_entry = tk.Entry(
            ef,
            textvariable=self.port_var,
            font=("Consolas", 13, "bold"),
            fg=C["text"], bg=C["entry_bg"],
            insertbackground=C["accent2"],
            relief="flat", highlightthickness=0, bd=8,
            justify="center",
        )
        self.port_entry.pack(fill="x")

        # toggle button (start / stop)
        self.toggle_btn = RoundButton(
            inner,
            label="▶   Start Server",
            bg=C["green"], hover=C["green_h"],
            command=self._on_toggle,
        )
        self.toggle_btn.pack()

        # ── status bar ────────────────────────────────────────────────────────
        sf = tk.Frame(self, bg=C["bg"], pady=10)
        sf.pack(fill="x", padx=28)

        self._dot = tk.Canvas(sf, width=12, height=12,
                              bg=C["bg"], highlightthickness=0)
        self._dot.pack(side="left", padx=(0, 8))
        self._dot_id = self._dot.create_oval(1, 1, 11, 11,
                                             fill=C["muted"], outline="")

        self.status_var = tk.StringVar(value="Idle  —  server not running")
        self.status_lbl = tk.Label(
            sf, textvariable=self.status_var,
            font=("Segoe UI", 9), fg=C["muted"], bg=C["bg"],
        )
        self.status_lbl.pack(side="left")

        # ── footer ────────────────────────────────────────────────────────────
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")
        tk.Label(self, text="UDP  ·  ViGEm  ·  Windows",
                 font=("Segoe UI", 8),
                 fg=C["muted"], bg=C["bg"], pady=10).pack()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── pulse animation ───────────────────────────────────────────────────────

    def _pulse(self):
        if not self._pulse_on:
            return
        cur = self._dot.itemcget(self._dot_id, "fill")
        nxt = C["green_h"] if cur != C["green_h"] else C["green"]
        self._dot.itemconfig(self._dot_id, fill=nxt)
        self.after(700, self._pulse)

    # ── toggle ────────────────────────────────────────────────────────────────

    def _on_toggle(self):
        if self._running:
            self._stop()
        else:
            self._start()

    def _start(self):
        global _server, _server_thread

        port_text = self.port_var.get().strip()
        if not port_text.isdigit() or not (1 <= int(port_text) <= 65535):
            messagebox.showerror(
                "Invalid port",
                "Please enter a port number between 1 and 65535.",
            )
            return

        port = int(port_text)
        try:
            _server = create_server(HOST, port)
        except Exception as exc:
            messagebox.showerror("Start failed", str(exc))
            return

        _server_thread = threading.Thread(
            target=joystick_control, args=(_server,), daemon=True
        )
        _server_thread.start()
        self._running = True

        self.port_entry.config(state="disabled")
        self.toggle_btn.set_style("■   Stop Server", C["red"], C["red_h"])
        self.status_var.set(f"Listening on port {port}")
        self.status_lbl.config(fg=C["green_h"])
        self._pulse_on = True
        self._pulse()

    def _stop(self):
        global _server, _server_thread

        self._pulse_on = False
        self._running  = False

        if _server:
            close_server(_server)
            _server = None
        _server_thread = None

        self.port_entry.config(state="normal")
        self.toggle_btn.set_style("▶   Start Server", C["green"], C["green_h"])
        self.status_var.set("Idle  —  server not running")
        self.status_lbl.config(fg=C["muted"])
        self._dot.itemconfig(self._dot_id, fill=C["muted"])

    def _on_close(self):
        self._pulse_on = False
        if _server:
            close_server(_server)
        self.destroy()


# ── entry point ────────────────────────────────────────────────────────────────

def run_app():
    app = JoystickServerApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
