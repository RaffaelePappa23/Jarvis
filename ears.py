import pyaudio
import wave
import os
import time
import numpy as np
from faster_whisper import WhisperModel

# Costanti
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
WAVE_OUTPUT_FILENAME = "temp_audio.wav"

def inizializza_orecchie():
    print("Caricamento modello Whisper (base) in VRAM...")
    return WhisperModel("base", device="cuda", compute_type="float16")

from collections import deque # Aggiungi questa in cima ai tuoi import

def registra_audio(soglia_volume=300, silenzio_max=1.5, timeout_iniziale=5.0):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    
    # Teniamo in memoria gli ultimi 0.5 secondi di audio (circa 8 chunk)
    pre_roll = deque(maxlen=8) 
    frames = []
    in_registrazione = False
    
    inizio_ascolto = time.time()
    tempo_ultimo_suono = time.time()

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        volume = np.sqrt(np.mean(audio_data.astype(np.float32)**2))

        if volume > soglia_volume:
            if not in_registrazione:
                print("* Jarvis ti sta ascoltando...")
                in_registrazione = True
                # Aggiungiamo il pre-roll all'inizio della registrazione vera e propria
                frames.extend(list(pre_roll))
            tempo_ultimo_suono = time.time()
            frames.append(data)
        elif in_registrazione:
            frames.append(data)
            if time.time() - tempo_ultimo_suono > silenzio_max:
                break
        else:
            # Se non stiamo ancora registrando, riempiamo il pre-roll
            pre_roll.append(data)
            if time.time() - inizio_ascolto > timeout_iniziale:
                stream.stop_stream()
                stream.close()
                p.terminate()
                return None

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Salvataggio identico a prima...
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return WAVE_OUTPUT_FILENAME

def trascrivi_audio(modello_whisper, file_audio):
    segments, info = modello_whisper.transcribe(file_audio, beam_size=5, language="it")
    testo_completo = " ".join([segment.text for segment in segments])
    
    if os.path.exists(file_audio):
        os.remove(file_audio)
    return testo_completo.strip()