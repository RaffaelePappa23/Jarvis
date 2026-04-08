import pyaudio
import wave
import os
from faster_whisper import WhisperModel

# Costanti
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
WAVE_OUTPUT_FILENAME = "temp_audio.wav"

def inizializza_orecchie():
    print("Caricamento modello Whisper (base) in VRAM...")
    # Lo carichiamo una volta sola qui
    return WhisperModel("base", device="cuda", compute_type="float16")

def registra_audio(secondi=5):
    """Registra per un tempo fisso (per ora)."""
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    
    print("* Ascolto...")
    frames = []
    for _ in range(0, int(RATE / CHUNK * secondi)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    print("* Elaborazione...")
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
    """Usa il modello già caricato per trascrivere."""
    segments, info = modello_whisper.transcribe(file_audio, beam_size=5, language="it")
    testo_completo = " ".join([segment.text for segment in segments])
    
    if os.path.exists(file_audio):
        os.remove(file_audio)
    return testo_completo.strip()