import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import keyboard
import speech_recognition as sr
from assistant import Assistant
from avatar import load_avatar, EXPRESSIONS
from tray import TrayManager

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
        self.assistant = Assistant()
        self.title("Herta — Space Assistant")
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

        keyboard.add_hotkey("ctrl+shift+h", self._toggle_window)

        self._add_message("Herta",
            "There you are, Arnab. I was just finishing some calculations, "
            "but I suppose they can wait. What's on the agenda today?")

    # ── Avatar ─────────────────────────────────────────────────────────────

    def _preload_avatars(self):
        for expr in EXPRESSIONS:
            pil_img = load_avatar(expr)
            self._avatar_images[expr] = ImageTk.PhotoImage(pil_img)

    def _set_expression(self, expr: str):
        if expr not in self._avatar_images:
            expr = "idle"
        self.after(0, lambda: [
            self.avatar_label.configure(image=self._avatar_images[expr]),
            self.expr_badge.configure(text=EXPRESSIONS[expr]["label"])
        ])

    # ── UI build ───────────────────────────────────────────────────────────

    def _build_ui(self):
        # Title bar
        titlebar = ctk.CTkFrame(self, fg_color=BG2, height=44, corner_radius=0)
        titlebar.pack(fill="x")
        titlebar.pack_propagate(False)

        ctk.CTkLabel(titlebar, text="✦  Herta",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=ACCENT2).pack(side="left", padx=16)

        self.status_dot = ctk.CTkLabel(titlebar, text="●",
                                        font=ctk.CTkFont(size=10),
                                        text_color=ACCENT)
        self.status_dot.pack(side="right", padx=16)

        ctk.CTkLabel(titlebar, text="Space Assistant",
                     font=ctk.CTkFont(size=12),
                     text_color=MUTED).pack(side="right")

        # Chat area
        self.chat_frame = ctk.CTkScrollableFrame(
            self, fg_color=BG, corner_radius=0)
        self.chat_frame.pack(fill="both", expand=True)

        # Avatar (bottom-right corner)
        self.avatar_outer = ctk.CTkFrame(
            self, fg_color=BG, width=130, height=145)
        self.avatar_outer.place(relx=1.0, rely=1.0, anchor="se", x=-8, y=-62)

        self.avatar_label = ctk.CTkLabel(
            self.avatar_outer, text="",
            image=self._avatar_images["idle"],
            fg_color=BG)
        self.avatar_label.pack()

        self.expr_badge = ctk.CTkLabel(
            self.avatar_outer,
            text=EXPRESSIONS["idle"]["label"],
            font=ctk.CTkFont(size=10),
            text_color=ACCENT2,
            fg_color=BUBBLE_BB,
            corner_radius=10,
            padx=8, pady=2)
        self.expr_badge.pack(pady=(2, 0))

        # Input bar
        input_bar = ctk.CTkFrame(self, fg_color=BG2, height=62, corner_radius=0)
        input_bar.pack(fill="x", side="bottom")
        input_bar.pack_propagate(False)

        self.input_field = ctk.CTkEntry(
            input_bar,
            placeholder_text="Say something to Herta...",
            fg_color=BG, border_color=ACCENT + "44",
            text_color=TEXT, placeholder_text_color=MUTED,
            font=ctk.CTkFont(size=13),
            height=38, corner_radius=20)
        self.input_field.pack(side="left", fill="x",
                               expand=True, padx=(12, 6), pady=12)
        self.input_field.bind("<Return>", lambda e: self._on_send())

        # Mic button
        self.mic_btn = ctk.CTkButton(
            input_bar, text="🎤", width=38, height=38,
            fg_color=BG, border_width=1,
            border_color=ACCENT + "66",
            hover_color=BUBBLE_BB,
            text_color=TEXT,
            font=ctk.CTkFont(size=16),
            corner_radius=20,
            command=self._on_mic_click)
        self.mic_btn.pack(side="left", padx=(0, 6), pady=12)

        # Send button
        self.send_btn = ctk.CTkButton(
            input_bar, text="→", width=38, height=38,
            fg_color=ACCENT, hover_color=ACCENT2,
            text_color=TEXT, font=ctk.CTkFont(size=16),
            corner_radius=20, command=self._on_send)
        self.send_btn.pack(side="left", padx=(0, 12), pady=12)

        # Hotkey hint
        ctk.CTkLabel(self,
                     text="Ctrl+Shift+H to hide  ·  lives in system tray",
                     font=ctk.CTkFont(size=10),
                     text_color=MUTED + "88",
                     fg_color=BG2).pack(fill="x")

    # ── Messaging ──────────────────────────────────────────────────────────

    def _add_message(self, sender: str, text: str):
        is_user = sender == "You"
        anchor  = "e" if is_user else "w"
        bg      = BUBBLE_USER if is_user else BUBBLE_BB
        padx    = (60, 10) if is_user else (10, 60)

        bubble = ctk.CTkLabel(
            self.chat_frame,
            text=text,
            wraplength=300,
            justify="left",
            fg_color=bg,
            text_color=TEXT,
            corner_radius=12,
            font=ctk.CTkFont(size=13),
            padx=12, pady=8)
        bubble.pack(anchor=anchor, pady=(4, 0), padx=padx)

        name_label = ctk.CTkLabel(
            self.chat_frame,
            text=sender,
            font=ctk.CTkFont(size=10),
            text_color=MUTED,
            fg_color=BG)
        name_label.pack(
            anchor=anchor,
            padx=(14 if not is_user else 0, 0 if not is_user else 14))

        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def _on_send(self):
        text = self.input_field.get().strip()
        if not text:
            return
        self.input_field.delete(0, "end")
        self._add_message("You", text)
        self.send_btn.configure(state="disabled")
        self._set_expression("thinking")
        threading.Thread(target=self._get_reply,
                         args=(text,), daemon=True).start()

    def _get_reply(self, text: str):
        reply = self.assistant.send_message(text)
        self._set_expression("talking")
        self.after(0, self._add_message, "Herta", reply)
        self.after(0, self.send_btn.configure, {"state": "normal"})
        self.after(2500, lambda: self._set_expression("idle"))

    # ── Voice input ────────────────────────────────────────────────────────

    def _on_mic_click(self):
        self.mic_btn.configure(state="disabled", text="⌛")
        self._set_expression("thinking")
        threading.Thread(target=self._listen_to_voice, daemon=True).start()

    def _listen_to_voice(self):
        try:
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source, timeout=5, phrase_time_limit=10)
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
        self.send_btn.configure(state="disabled")
        threading.Thread(target=self._get_reply,
                         args=(text,), daemon=True).start()

    # ── Window / tray ──────────────────────────────────────────────────────

    def _hide_to_tray(self):
        self.withdraw()

    def _show_window(self):
        self.after(0, self.deiconify)
        self.after(0, self.lift)

    def _toggle_window(self):
        if self.winfo_viewable():
            self._hide_to_tray()
        else:
            self._show_window()

    def _quit_app(self):
        print("Saving Herta's memory...")
        self.assistant.save_memory()
        self.tray.stop()
        self.after(0, self.destroy)