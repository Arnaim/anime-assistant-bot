import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import keyboard
import speech_recognition as sr
from assistant import Assistant
from avatar import load_avatar, EXPRESSIONS
from tray import TrayManager

# --- COLORS (Fixed: Removed 8-digit transparency hex codes) ---
BG          = "#2a2542"
BG2         = "#221e38"
ACCENT      = "#7a56ae"
ACCENT2     = "#b19dcc"
TEXT        = "#e0dee0"
MUTED       = "#a99ca6"
BUBBLE_BB   = "#352d5e"
BUBBLE_USER = "#7a56ae"

class ChatWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Initializing Assistant first so its name is available
        self.assistant = Assistant()
        
        self.title(f"{self.assistant.name} — Genius Assistant")
        self.geometry("480x660")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.protocol("WM_DELETE_WINDOW", self._hide_to_tray)

        self.recognizer = sr.Recognizer()
        self.mic        = sr.Microphone()

        self._avatar_images = {}
        self._preload_avatars()

        self._build_ui()

        self.tray = TrayManager(
            show_callback=self._show_window,
            quit_callback=self._quit_app
        )
        self.tray.start()

        # Global Hotkey (Ctrl+Shift+H)
        keyboard.add_hotkey('ctrl+shift+h', self._toggle_window)

    def _preload_avatars(self):
        """Pre-loads avatars using CTkImage for high-DPI scaling support."""
        for expr in EXPRESSIONS:
            pil_img = load_avatar(expr)
            # Wrapping PIL image in CTkImage fixes the scaling UserWarning
            self._avatar_images[expr] = ctk.CTkImage(
                light_image=pil_img,
                dark_image=pil_img,
                size=(110, 110)
            )

    def _build_ui(self):
        # ── Custom Titlebar ──────────────────────────────────────────────────
        self.title_bar = ctk.CTkFrame(self, fg_color=BG2, height=40, corner_radius=0)
        self.title_bar.pack(fill="x", side="top")
        
        title_lbl = ctk.CTkLabel(self.title_bar, text=f"✨ {self.assistant.name.upper()} TERMINAL", 
                                 font=ctk.CTkFont(size=12, weight="bold"), text_color=ACCENT2)
        title_lbl.pack(side="left", padx=15)

        # ── Avatar Display ────────────────────────────────────────────────────
        self.avatar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.avatar_frame.pack(pady=20)

        self.avatar_label = ctk.CTkLabel(self.avatar_frame, text="", image=self._avatar_images["idle"])
        self.avatar_label.pack()

        # ── Chat Area ────────────────────────────────────────────────────────
        self.chat_frame = ctk.CTkScrollableFrame(
            self, fg_color=BG2, corner_radius=15, 
            scrollbar_button_color=ACCENT,
            scrollbar_button_hover_color=ACCENT2
        )
        self.chat_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # ── Input Bar ────────────────────────────────────────────────────────
        input_bar = ctk.CTkFrame(self, fg_color="transparent")
        input_bar.pack(fill="x", side="bottom", padx=20, pady=(0, 10))

        self.input_field = ctk.CTkEntry(
            input_bar,
            placeholder_text="Say something to Herta...",
            fg_color=BG, border_color=ACCENT, text_color=TEXT,
            placeholder_text_color=MUTED,
            font=ctk.CTkFont(size=13),
            height=38, corner_radius=20
        )
        self.input_field.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_field.bind("<Return>", lambda e: self._on_send_click())

        self.mic_btn = ctk.CTkButton(
            input_bar, text="🎤", width=38, height=38,
            fg_color=BG, border_width=1, border_color=ACCENT,
            hover_color=BUBBLE_BB, text_color=TEXT,
            font=ctk.CTkFont(size=16), corner_radius=20,
            command=self._on_mic_click
        )
        self.mic_btn.pack(side="right", padx=2)

        self.send_btn = ctk.CTkButton(
            input_bar, text="➤", width=38, height=38,
            fg_color=ACCENT, hover_color=ACCENT2, text_color=BG,
            font=ctk.CTkFont(size=16), corner_radius=20,
            command=self._on_send_click
        )
        self.send_btn.pack(side="right")

        # Bottom Hint (Fixed: Removed the '88' transparency suffix)
        ctk.CTkLabel(self, text="Ctrl+Shift+H to hide  ·  lives in system tray",
                     font=ctk.CTkFont(size=10), text_color=MUTED, fg_color=BG).pack(fill="x", pady=2)

    def _add_message(self, sender, text):
        is_user = sender.lower() == "you"
        color = BUBBLE_USER if is_user else BUBBLE_BB
        anchor = "e" if is_user else "w"
        
        msg_box = ctk.CTkFrame(self.chat_frame, fg_color=color, corner_radius=12)
        msg_box.pack(anchor=anchor, padx=10, pady=5)
        
        lbl = ctk.CTkLabel(msg_box, text=text, text_color=TEXT, 
                           font=ctk.CTkFont(size=12), wraplength=300, justify="left")
        lbl.pack(padx=12, pady=8)
        
        # Auto-scroll to bottom
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def _set_expression(self, expr):
        if expr in self._avatar_images:
            self.avatar_label.configure(image=self._avatar_images[expr])

    def _on_send_click(self):
        text = self.input_field.get().strip()
        if not text: return
        
        self.input_field.delete(0, 'end')
        self._add_message("You", text)
        
        # Start reply thread
        threading.Thread(target=self._get_reply, args=(text,), daemon=True).start()

    def _get_reply(self, text):
        self._set_expression("thinking")
        self.send_btn.configure(state="disabled")
        
        reply = self.assistant.send_message(text)
        
        self.after(0, self._set_expression, "talking")
        self.after(0, self._add_message, self.assistant.name, reply)
        self.after(0, self.send_btn.configure, {"state": "normal"})
        
        # Go back to idle after speaking (approximate timing)
        self.after(4000, self._set_expression, "idle")

    def _on_mic_click(self):
        self.mic_btn.configure(state="disabled", text="⌛")
        threading.Thread(target=self._listen_voice, daemon=True).start()

    def _listen_voice(self):
        try:
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            user_text = self.recognizer.recognize_google(audio)
            self.after(0, self._process_voice_input, user_text)
        except Exception as e:
            print(f"Voice error: {e}")
            self.after(0, lambda: [
                self.mic_btn.configure(state="normal", text="🎤"),
                self._set_expression("error")
            ])
            self.after(2000, lambda: self._set_expression("idle"))

    def _process_voice_input(self, text: str):
        self.mic_btn.configure(state="normal", text="🎤")
        self._add_message("You", text)
        threading.Thread(target=self._get_reply, args=(text,), daemon=True).start()

    # ── Window / tray logic ────────────────────────────────────────────────
    def _hide_to_tray(self):
        self.withdraw()

    def _show_window(self):
        self.after(0, self.deiconify)
        self.after(0, self.lift)

    def _toggle_window(self):
        if self.winfo_viewable():
            self.withdraw()
        else:
            self._show_window()

    def _quit_app(self):
        self.tray.stop()
        self.destroy()
        import os
        os._exit(0)