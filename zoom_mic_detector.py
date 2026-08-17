import tkinter as tk
import threading
import time
import psutil
from pywinauto import Desktop

BORDER_THICKNESS = 8
POLL_INTERVAL = 0.25


def is_zoom_running():
    """Check if the Zoom process is running at all."""
    for proc in psutil.process_iter(["name"]):
        if proc.info["name"] and "zoom" in proc.info["name"].lower():
            return True
    return False


def get_mic_state():
    """Return 'LIVE', 'MUTED', or 'UNKNOWN'."""
    if not is_zoom_running():
        return "NOT_RUNNING"

    try:
        zoom_windows = Desktop(backend="uia").windows(
            title_re=".*Zoom.*",
            visible_only=True
        )

        for window in zoom_windows:
            # If Zoom shows "Mute", clicking it would mute us — mic is LIVE.
            if window.descendants(title="Mute", control_type="Button"):
                return "LIVE"
            # If Zoom shows "Unmute", we're currently muted.
            if window.descendants(title="Unmute", control_type="Button"):
                return "MUTED"

    except Exception:
        pass

    return "UNKNOWN"


class RedBorderOverlay:
    """Transparent fullscreen window that shows a red border."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Zoom Live Indicator")
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")  # black = transparent
        self.root.overrideredirect(True)  # no title bar
        self.root.configure(bg="black")

        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()

        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        t = BORDER_THICKNESS
        # Draw four red rectangles forming a border
        self.rects = [
            self.canvas.create_rectangle(0, 0, w, t, fill="red", outline=""),        # top
            self.canvas.create_rectangle(0, h - t, w, h, fill="red", outline=""),    # bottom
            self.canvas.create_rectangle(0, 0, t, h, fill="red", outline=""),        # left
            self.canvas.create_rectangle(w - t, 0, w, h, fill="red", outline=""),    # right
        ]

        self.visible = False
        self.hide()

        # Start polling in a background thread
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def show(self):
        if not self.visible:
            self.root.deiconify()
            self.visible = True

    def hide(self):
        if self.visible or not hasattr(self, "_started"):
            self.root.withdraw()
            self.visible = False
        self._started = True

    def _poll_loop(self):
        while self._running:
            state = get_mic_state()
            if state == "LIVE":
                self.root.after(0, self.show)
                self.root.after(0, lambda: print("\r🔴 MIC LIVE     ", end="", flush=True))
            else:
                self.root.after(0, self.hide)
                if state == "MUTED":
                    self.root.after(0, lambda: print("\rMIC MUTED       ", end="", flush=True))
                elif state == "NOT_RUNNING":
                    self.root.after(0, lambda: print("\rZoom not running ", end="", flush=True))
                else:
                    self.root.after(0, lambda: print("\rZoom state unknown", end="", flush=True))
            time.sleep(POLL_INTERVAL)

    def run(self):
        print("Zoom Live Indicator — running (Ctrl+C to stop)")
        self.root.mainloop()


if __name__ == "__main__":
    overlay = RedBorderOverlay()
    overlay.run()
