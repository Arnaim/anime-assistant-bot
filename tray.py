import pystray
from PIL import Image, ImageDraw
import threading

def make_tray_icon() -> Image.Image:
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 60, 60], fill="#7a56ae", outline="#b19dcc", width=2)
    draw.text((14, 18), "HT", fill="#e0dee0")
    return img

class TrayManager:
    def __init__(self, show_callback, quit_callback):
        self.show_cb = show_callback
        self.quit_cb = quit_callback
        self.icon    = None

    def start(self):
        menu = pystray.Menu(
            pystray.MenuItem("Show Herta", self._show),
            pystray.MenuItem("Quit",       self._quit),
        )
        self.icon = pystray.Icon(
            "Herta", make_tray_icon(), "Herta — Space Assistant", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def stop(self):
        if self.icon:
            self.icon.stop()

    def _show(self, icon, item):
        self.show_cb()

    def _quit(self, icon, item):
        self.quit_cb()