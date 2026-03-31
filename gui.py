import customtkinter as ctk
import threading
from assistant import Assistant
import speech_recognition as sr

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ChatWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.assistant = Assistant()
        self.title(f"{self.assistant.name} — AI Assistant")
        self.geometry("500x650")
        self.resizable(False, False)
        self._build_ui()
        # Inside ChatWindow.__init__ in gui.py
        self._add_message(self.assistant.name,
            f"There you are, Arnab. I was just finishing some calculations, but I suppose they can wait. What's on the agenda today?")
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()


    def _build_ui(self):
        # Header
        header = ctk.CTkLabel(self, text=f"✦ {self.assistant.name}",
                               font=ctk.CTkFont(size=20, weight="bold"))
        header.pack(pady=(16, 4))

        # Chat display
        self.chat_box = ctk.CTkScrollableFrame(self, width=460, height=480)
        self.chat_box.pack(padx=16, pady=8, fill="both", expand=True)

        # Input row
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(padx=16, pady=(4, 16), fill="x")

        self.input_field = ctk.CTkEntry(input_frame, placeholder_text="Say something...",
                                         height=40, font=ctk.CTkFont(size=14))
        self.input_field.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.input_field.bind("<Return>", lambda e: self._on_send())

        self.mic_btn = ctk.CTkButton(input_frame, text="🎤", width=40, 
                                    height=40, command=self._on_mic_click)
        self.mic_btn.pack(side="left", padx=(0, 8))

        send_btn = ctk.CTkButton(input_frame, text="Send", width=80,
                                  height=40, command=self._on_send)
        send_btn.pack(side="right")

    def _add_message(self, sender: str, text: str):
        is_user = sender == "You"
        color = "#2b5278" if is_user else "#2d4a3e"
        anchor = "e" if is_user else "w"

        bubble = ctk.CTkLabel(
            self.chat_box, text=f"{sender}: {text}",
            wraplength=380, justify="left",
            fg_color=color, corner_radius=10,
            font=ctk.CTkFont(size=13), padx=10, pady=8
        )
        bubble.pack(anchor=anchor, pady=4, padx=8)
        self.chat_box._parent_canvas.yview_moveto(1.0)

    def _on_send(self):
        user_text = self.input_field.get().strip()
        if not user_text:
            return
        self.input_field.delete(0, "end")
        self._add_message("You", user_text)
        # Run in thread so UI doesn't freeze
        threading.Thread(target=self._get_reply,
                         args=(user_text,), daemon=True).start()

    def _get_reply(self, user_text: str):
        reply = self.assistant.send_message(user_text)
        self.after(0, self._add_message, self.assistant.name, reply)


    def _on_closing(self):
        """Ensures BB saves her memory before the app shuts down."""
        print("Saving BB's memory...")
        self.assistant.save_memory()
        self.destroy()
    def _on_mic_click(self):
        """Starts the voice recognition in a background thread."""
        self.mic_btn.configure(state="disabled", text="⌛")
        threading.Thread(target=self._listen_to_voice, daemon=True).start()

    def _listen_to_voice(self):
        try:
            with self.mic as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # Convert audio to text
            user_text = self.recognizer.recognize_google(audio)
            
            # Update UI from the main thread
            self.after(0, self._process_voice_input, user_text)
        except Exception as e:
            print(f"Voice Error: {e}")
            self.after(0, lambda: self.mic_btn.configure(state="normal", text="🎤"))

    def _process_voice_input(self, text):
        """Handles the text recognized from voice."""
        self.mic_btn.configure(state="normal", text="🎤")
        self._add_message("You", text)
        threading.Thread(target=self._get_reply, args=(text,), daemon=True).start()