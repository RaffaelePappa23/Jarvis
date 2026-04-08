import os
import pyautogui
import time

def esegui_azione(azione):
    """Mappa l'azione testuale ricevuta dal JSON del LLM a un comando fisico sul PC."""
    if azione == "nessuna":
        return

    print(f"🤲 [MANI] Esecuzione azione in corso: {azione}")

    # --- AZIONI DI SISTEMA E APPLICAZIONI ---
    if azione == "apri_browser":
        # Apre il browser predefinito
        os.startfile("https://www.google.com")
        
    elif azione == "apri_esplora_file":
        # Apre Esplora Risorse
        os.startfile("explorer")
        
    # --- AZIONI AUDIO ---
    elif azione == "alza_volume":
        # Preme il tasto multimediale "Volume Su" 5 volte (circa +10%)
        pyautogui.press('volumeup', presses=5)
        
    elif azione == "abbassa_volume":
        # Preme il tasto multimediale "Volume Giù" 5 volte
        pyautogui.press('volumedown', presses=5)

    # --- GESTIONE FINESTRE E SCHERMI (4 Monitor) ---
    elif azione == "schermo_intero":
        # Scorciatoia di Windows per massimizzare la finestra attiva
        pyautogui.hotkey('win', 'up')
        
    elif azione == "sposta_finestra_destra":
        # Sposta la finestra al monitor di destra
        pyautogui.hotkey('win', 'shift', 'right')
        
    elif azione == "sposta_finestra_sinistra":
        # Sposta la finestra al monitor di sinistra
        pyautogui.hotkey('win', 'shift', 'left')
        
    elif azione == "sposta_finestra_su":
        # Per il tuo quarto monitor posizionato in alto, solitamente Windows 
        # richiede prima di togliere il full-screen, poi usare win+up più volte.
        pyautogui.hotkey('win', 'up')
        time.sleep(0.1)
        pyautogui.hotkey('win', 'up')
        
    elif azione == "sposta_finestra_giu":
        # Minimizza o sposta verso il basso
        pyautogui.hotkey('win', 'down')
        
    else:
        print(f"[MANI] ⚠️ Comando non riconosciuto: {azione}")