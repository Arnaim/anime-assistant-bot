import os
import pickle 
import pygame
import scipy.io.wavfile
import time
from pocket_tts import TTSModel
from pydub import AudioSegment

# Ensure these are the 50MB+ versions from the zip!
AudioSegment.converter = r"D:\Chocolatey\ffmpeg.exe"
AudioSegment.ffprobe   = r"D:\Chocolatey\ffprobe.exe"

class VoiceEngine:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.cache_dir = r"D:/AI_Models_Cache"
        self.state_path = os.path.join(self.cache_dir, "herta_signature.pkl")
        
        os.makedirs(self.cache_dir, exist_ok=True)
        
        print("⌛ Loading TTS Model...")
        self.model = TTSModel.load_model()
        
        if os.path.exists(self.state_path):
            print("⚡ Herta's signature found. Loading instantly...")
            with open(self.state_path, "rb") as f:
                self.herta_state = pickle.load(f)
        else:
            wav_path = os.path.join(self.base_dir, "thehertavoicelines.wav")
            print(f"✨ First time setup: Extracting voice from {wav_path}...")
            self.herta_state = self.model.get_state_for_audio_prompt(wav_path)
            with open(self.state_path, "wb") as f:
                pickle.dump(self.herta_state, f)

        pygame.mixer.init()

    def speak(self, text):
        raw_path = os.path.join(self.base_dir, "raw_generated.wav")
        output_path = os.path.join(self.base_dir, "herta_final.wav")
        
        print(f"🎙️ Madam Herta: {text}")
        
        try:
            # 1. Generate
            audio_tensor = self.model.generate_audio(self.herta_state, text)
            scipy.io.wavfile.write(raw_path, self.model.sample_rate, audio_tensor.numpy())
            
            # 2. Process (Release file lock first)
            pygame.mixer.music.unload() 
            
            sound = AudioSegment.from_wav(raw_path)
            new_sample_rate = int(sound.frame_rate * 1.03) 
            herta_voice = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
            herta_voice = herta_voice.set_frame_rate(44100).high_pass_filter(200) 
            herta_voice.export(output_path, format="wav")

            # 3. Play
            pygame.mixer.music.load(output_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            pygame.mixer.music.unload() # Critical for Windows permission fix
        except Exception as e:
            print(f"❌ Voice Error: {e}")