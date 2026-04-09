import os
import torch
import wave
import pyaudio
from TTS.api import TTS
from queue import Queue
import threading

def inizializza_voce():
    print("Inizializzazione modulo vocale XTTSv2 in VRAM...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    return tts

def _riproduci_worker(coda_audio):
    """Thread background che riproduce i file audio appena sono pronti in coda."""
    p = pyaudio.PyAudio()
    while True:
        file_audio = coda_audio.get()
        if file_audio is None:  # Segnale "pillola di cianuro" per uccidere il thread
            break
        
        try:
            wf = wave.open(file_audio, 'rb')
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            
            chunk = 1024
            data = wf.readframes(chunk)
            while data:
                stream.write(data)
                data = wf.readframes(chunk)
                
            stream.stop_stream()
            stream.close()
        except Exception as e:
            pass
        finally:
            # Elimina l'audio temporaneo subito dopo averlo riprodotto
            if os.path.exists(file_audio):
                try:
                    os.remove(file_audio)
                except OSError:
                    pass
            coda_audio.task_done()
            
    p.terminate()

def parla_stream(tts_model, generatore_frasi, file_campione="campione.wav"):
    """Sintetizza in tempo reale un flusso di frasi e le riproduce asincronamente."""
    if not os.path.exists(file_campione):
        print(f"[ERRORE] File '{file_campione}' non trovato.")
        return

    # Inizializza coda e thread
    coda_audio = Queue()
    thread_riproduzione = threading.Thread(target=_riproduci_worker, args=(coda_audio,))
    thread_riproduzione.start()

    contatore = 0
    for frase in generatore_frasi:
        # XTTS crashera' se gli dai solo virgole o stringhe vuote, evitiamolo:
        if not frase.strip() or not any(c.isalpha() for c in frase):
            continue
            
        # FIX PUNTO: XTTS in italiano a volte legge il "." come parola. 
        # Lo sostituiamo con una virgola per mantenere la pausa vocale.
        frase_pulita = frase.replace(".", ",")
            
        file_output = f"temp_jarvis_stream_{contatore}.wav"
        print(f"🗣️ [TTS IN CORSO]: {frase_pulita}")
        
        # Genera il file WAV usando la frase pulita
        tts_model.tts_to_file(
            text=frase_pulita,
            speaker_wav=file_campione,
            language="it",
            file_path=file_output
        )
        
        # Inserisce il file in coda (il Thread di riproduzione lo suonerà immediatamente)
        coda_audio.put(file_output)
        contatore += 1
        
    # Quando l'LLM ha finito di pensare, mandiamo il segnale di chiusura al Thread
    coda_audio.put(None)
    # Attendiamo che Jarvis finisca di dire l'ultima parola prima di riconsegnare il controllo a main
    thread_riproduzione.join()