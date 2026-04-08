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

def registra_audio(soglia_volume=300, silenzio_max=1.5, timeout_iniziale=5.0):
    """
    Registra dinamicamente: inizia quando c'è rumore, si ferma dopo 'silenzio_max' secondi di quiete.
    Se non sente nulla per 'timeout_iniziale' secondi, annulla.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    
    print("* In ascolto (parla ora)...")
    frames = []
    in_registrazione = False
    
    inizio_ascolto = time.time()
    tempo_ultimo_suono = time.time()

    while True:
        # Leggiamo il chunk audio
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # Calcoliamo il volume (RMS)
        # Usiamo float32 per evitare overflow durante il calcolo
        volume = np.sqrt(np.mean(audio_data.astype(np.float32)**2))

        if volume > soglia_volume:
            if not in_registrazione:
                print("* Voce rilevata, sto acquisendo...")
                in_registrazione = True
            tempo_ultimo_suono = time.time()
            frames.append(data)
            
        elif in_registrazione:
            # Stiamo registrando, ma il volume è sotto la soglia (silenzio)
            frames.append(data)
            if time.time() - tempo_ultimo_suono > silenzio_max:
                print("* Pausa rilevata, elaborazione in corso...")
                break
                
        else:
            # Non stiamo ancora registrando, controlliamo il timeout iniziale
            if time.time() - inizio_ascolto > timeout_iniziale:
                print("* Nessun comando vocale rilevato.")
                stream.stop_stream()
                stream.close()
                p.terminate()
                return None # Nessun file creato

    # Salvataggio del file
    stream.stop_stream()
    stream.close()
    p.terminate()

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