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
    
    # 1. DIZIONARIO DEI SINONIMI: Adattalo ai tuoi programmi!
    sinonimi = {
        "browser": ["brave", "chrome", "edge", "firefox"],
        "chrome": ["brave", "chrome"],  # Se il LLM dice chrome, cerchiamo brave
        "esplora file": ["esplora file", "explorer", "cartella", "documenti"]
    }
    
    nome_app_lower = nome_app.lower().strip()
    # 2. Se la parola è nel dizionario, usa la lista dei sinonimi. Altrimenti usa la parola esatta.
    termini_ricerca = sinonimi.get(nome_app_lower, [nome_app_lower])

    finestre = gw.getAllTitles()
    for titolo in finestre:
        titolo_lower = titolo.lower()
        # 3. Controlla se ALMENO UNO dei termini di ricerca è nel titolo
        if any(termine in titolo_lower for termine in termini_ricerca) and titolo.strip() != "":
            try:
                win = gw.getWindowsWithTitle(titolo)[0]
                if win.isMinimized:
                    win.restore()
                win.activate()
                time.sleep(0.3) # Aspetta il focus di Windows
                return True
            except Exception as e:
                print(f"[MANI] Errore nell'attivazione della finestra: {e}")
                
    print(f"[MANI] Nessuna finestra trovata per '{nome_app}' (termini cercati: {termini_ricerca}).")
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
            parti = target.split(",")
            nome_app = parti[0].strip()
            direzione = parti[1].strip().lower() if len(parti) > 1 else "destra"

            if attiva_finestra(nome_app):
                # PAUSA CRITICA: Diamo a Windows mezzo secondo per completare il focus
                time.sleep(0.5) 

                if direzione == "destra":
                    # Metodo forzato: premiamo fisicamente giù i tasti modificatori
                    pyautogui.keyDown('win')
                    pyautogui.keyDown('shift')
                    pyautogui.press('right')
                    pyautogui.keyUp('shift')
                    pyautogui.keyUp('win')
                    
                elif direzione == "sinistra":
                    pyautogui.keyDown('win')
                    pyautogui.keyDown('shift')
                    pyautogui.press('left')
                    pyautogui.keyUp('shift')
                    pyautogui.keyUp('win')
                    
                elif direzione == "su":
                    # Per il monitor in alto, Win+Su prima massimizza, poi spinge su
                    pyautogui.keyDown('win')
                    pyautogui.press('up')
                    time.sleep(0.1)
                    pyautogui.press('up')
                    pyautogui.keyUp('win')
                    
                elif direzione == "giu" or direzione == "giù":
                    pyautogui.keyDown('win')
                    pyautogui.press('down')
                    pyautogui.keyUp('win')
                    
                elif direzione == "centro":
                    # Windows non ha un comando per "centro". Per ciclare usiamo sinistra
                    print("⚠️ [MANI] Uso 'sinistra' per far ruotare la finestra verso il centro.")
                    pyautogui.keyDown('win')
                    pyautogui.keyDown('shift')
                    pyautogui.press('left')
                    pyautogui.keyUp('shift')
                    pyautogui.keyUp('win')
                    
    except Exception as e:
         print(f"⚠️ [MANI] Errore durante l'esecuzione dell'azione: {e}")