import os
import pyautogui
import time
import webbrowser
import pygetwindow as gw
from urllib.parse import quote

# Nuovo import semplificato per l'audio
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def get_volume_controller():
    """Inizializza il controller del volume di Windows (per pycaw aggiornato)."""
    devices = AudioUtilities.GetSpeakers()
    # Nelle nuove versioni l'accesso è diretto e non richiede più 'Activate' o 'cast'
    return devices.EndpointVolume.QueryInterface(IAudioEndpointVolume)

def imposta_volume(target_vol):
    """Imposta il volume a una percentuale esatta (0-100)."""
    volume = get_volume_controller()
    # Pycaw lavora con decibel scalari da 0.0 a 1.0
    target_vol = max(0, min(100, target_vol)) / 100.0
    volume.SetMasterVolumeLevelScalar(target_vol, None)

def modifica_volume(delta):
    """Alza o abbassa il volume in base al delta (+20 o -20)."""
    volume = get_volume_controller()
    current_vol = volume.GetMasterVolumeLevelScalar() * 100
    nuovo_vol = current_vol + delta
    imposta_volume(nuovo_vol)

def attiva_finestra(nome_app):
    """Cerca una finestra aperta tramite il nome e la porta in primo piano."""
    finestre = gw.getAllTitles()
    # Cerca una corrispondenza parziale (es. "chrome" in "Nuova scheda - Google Chrome")
    for titolo in finestre:
        if nome_app.lower() in titolo.lower() and titolo.strip() != "":
            try:
                win = gw.getWindowsWithTitle(titolo)[0]
                if win.isMinimized:
                    win.restore()
                win.activate()
                time.sleep(0.3) # Aspetta che Windows metta a fuoco la finestra
                return True
            except Exception as e:
                print(f"[MANI] Errore nell'attivazione della finestra: {e}")
    print(f"[MANI] Finestra '{nome_app}' non trovata.")
    return False

def esegui_azione(azione, target="", valore=0):
    """Esegue l'azione in base ai parametri ricevuti dal LLM."""
    if azione == "nessuna":
        return

    print(f"🤲 [MANI] Esecuzione: {azione} | Target: '{target}' | Valore: {valore}")

    try:
        # --- VOLUME ---
        if azione == "alza_volume":
            modifica_volume(valore if valore > 0 else 10)
        elif azione == "abbassa_volume":
            modifica_volume(-valore if valore > 0 else -10)
        elif azione == "imposta_volume":
            imposta_volume(valore)

        # --- APERTURA APP ---
        elif azione == "apri_app":
            target_pulito = target.lower().strip()
            if "browser" in target_pulito or "chrome" in target_pulito or "edge" in target_pulito:
                webbrowser.open("https://www.google.com")
            elif "file" in target_pulito or "esplora" in target_pulito:
                os.startfile("explorer")
            else:
                # Tenta di aprirlo tramite i comandi di Windows
                os.system(f"start {target_pulito}")

        # --- RICERCA WEB ---
        elif azione == "cerca_web":
            if target:
                query_formattata = quote(target)
                url = f"https://www.google.com/search?q={query_formattata}"
                webbrowser.open(url)

        # --- SPOSTAMENTO FINESTRE ---
        elif azione == "sposta_finestra":
            # Il target qui è "nome_app, direzione" (es. "chrome, destra")
            parti = target.split(",")
            nome_app = parti[0].strip()
            direzione = parti[1].strip().lower() if len(parti) > 1 else "destra"

            if attiva_finestra(nome_app):
                if direzione == "destra":
                    pyautogui.hotkey('win', 'shift', 'right')
                elif direzione == "sinistra":
                    pyautogui.hotkey('win', 'shift', 'left')
                elif direzione == "su":
                    pyautogui.hotkey('win', 'up')
                    time.sleep(0.1)
                    pyautogui.hotkey('win', 'up')
                elif direzione == "giu" or direzione == "giù":
                    pyautogui.hotkey('win', 'down')
                    
    except Exception as e:
         print(f"⚠️ [MANI] Errore durante l'esecuzione dell'azione: {e}")