import os
import torch  # <--- INSERISCI QUESTO ESATTAMENTE QUI (Il Re viene prima)

os.environ["CUDA_MODULE_LOADING"] = "LAZY"
os.environ["COQUI_TOS_AGREED"] = "1"

import pyaudio
import numpy as np
from openwakeword.model import Model
import openwakeword

import mouth  # <--- Sposta mouth prima di ears
import ears
import brain

# --- CONFIGURAZIONI AUDIO ---
CHUNK = 1280
RATE = 16000

def main():
    print("--- INIZIALIZZAZIONE SISTEMI DI J.A.R.V.I.S. ---")
    
    # 0. Scarica modelli base (melspectrogram, embedding)
    print("[SISTEMA] Verifica modelli base di openWakeWord in corso...")
    openwakeword.utils.download_models()

    # 1. WAKE WORD
    cartella_modelli = "modelli_wakeword"
    modello_scelto = "hey_jarvis_v0.1.onnx"
    jarvis_model_path = os.path.join(cartella_modelli, modello_scelto)
    
    if not os.path.exists(jarvis_model_path):
        print(f"\n[ERRORE CRITICO] Modello Wake Word non trovato in: {jarvis_model_path}")
        exit()

    oww_model = Model(wakeword_models=[jarvis_model_path], inference_framework="onnx")
    
    # FIX: warm-up con un chunk di silenzio per popolare prediction_buffer
    dummy_audio = np.zeros(CHUNK, dtype=np.int16)
    oww_model.predict(dummy_audio)
    
    # Ora le chiavi ci sono
    nome_modello_caricato = list(oww_model.prediction_buffer.keys())[0]
    print(f"[SISTEMA] Wake word pronta. Modello attivo: '{nome_modello_caricato}'")

    # 2. INIZIALIZZAZIONE MODULI
    modello_orecchie = ears.inizializza_orecchie()
    modello_bocca = mouth.inizializza_voce()
    cronologia = []

    # 3. MICROFONO
    p = pyaudio.PyAudio()
    mic_stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    print("\n[ONLINE] Jarvis è pronto. Dì 'Hey Jarvis' per attivarlo.")

    try:
        while True:
            audio_data = np.frombuffer(mic_stream.read(CHUNK), dtype=np.int16)
            oww_model.predict(audio_data)
            
            score = oww_model.prediction_buffer[nome_modello_caricato][-1]
            
            if score > 0.5:
                print(f"\n[!] Wake word rilevata! (confidenza: {score:.2f})")
                mic_stream.stop_stream()

                # A. ORECCHIE
                file_audio = ears.registra_audio(soglia_volume=300, silenzio_max=1.5)
                
                if file_audio:
                    # Questa parte viene eseguita SOLO se ha effettivamente registrato un file
                    testo_utente = ears.trascrivi_audio(modello_orecchie, file_audio)
                    print(f"Tu: {testo_utente}")

                    if testo_utente:
                        # B. CERVELLO
                        print("Elaborazione in corso...")
                        risposta_json, cronologia = brain.interroga_jarvis(testo_utente, cronologia)
                        
                        if risposta_json:
                            testo_jarvis = risposta_json.get("risposta_vocale", "Errore nel formato vocale.")
                            azione = risposta_json.get("azione_pc", "nessuna")
                            
                            print(f"Jarvis: {testo_jarvis}")
                            
                            # C. BOCCA
                            mouth.parla(modello_bocca, testo_jarvis)

                            # D. AZIONE 
                            if azione != "nessuna":
                                print(f"[SISTEMA] Azione in coda: {azione}")
                
                else:
                    # Questa parte viene eseguita se c'è stato solo silenzio
                    print("[SISTEMA] Operazione annullata per inattività.")

                # --- QUESTO DEVE RIMANERE SEMPRE ALLA FINE DELL'IF DELLA WAKE WORD ---
                # Reset buffer per evitare riattivazione immediata
                oww_model.reset()
                print("\n[ASCOLTO...] In attesa della wake word.")
                mic_stream.start_stream()

    except KeyboardInterrupt:
        print("\nSpegnimento sistemi in corso...")
    finally:
        mic_stream.stop_stream()
        mic_stream.close()
        p.terminate()

if __name__ == "__main__":
    main()