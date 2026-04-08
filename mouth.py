import os
import torch
import wave
import pyaudio
from TTS.api import TTS

def inizializza_voce():
    print("Inizializzazione modulo vocale XTTSv2 in VRAM...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    return tts

def riproduci_audio_silenzioso(nome_file):
    """Riproduce l'audio in background senza aprire programmi esterni."""
    chunk = 1024
    wf = wave.open(nome_file, 'rb')
    p = pyaudio.PyAudio()
    
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)
        
    stream.stop_stream()
    stream.close()
    p.terminate()

def parla(tts_model, testo, file_campione="campione.wav"):
    file_output = "risposta_jarvis.wav"
    
    if not os.path.exists(file_campione):
        print(f"[ERRORE] File '{file_campione}' non trovato.")
        return

    print("Generazione audio in corso...")
    tts_model.tts_to_file(
        text=testo,
        speaker_wav=file_campione,
        language="it",
        file_path=file_output
    )
    
    print("* Riproduzione audio...")
    # Invece di os.system(), usiamo la nostra nuova funzione silenziosa!
    riproduci_audio_silenzioso(file_output)