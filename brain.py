import ollama
import json
import re

MODELLO_LLM = 'llama3' 

SYSTEM_PROMPT = """Sei JARVIS, la mia intelligenza artificiale personale e assistente di sistema.
Rispondi SEMPRE in italiano, qualunque cosa ti venga chiesta.
Il tuo tono è formale, educato, servizievole ma con un tocco di sottile sarcasmo.

REGOLE FONDAMENTALI:
1. Devi SEMPRE rispondere utilizzando ESCLUSIVAMENTE un formato JSON valido. 
2. Non aggiungere testo testuale prima o dopo il blocco JSON.
3. Se ti chiedo di compiere un'azione sul PC, devi identificarla dal contesto e scegliere una delle azioni consentite.

Formato JSON richiesto (usa esattamente queste chiavi):
{
    "risposta_vocale": "La frase che dirai ad alta voce per rispondere all'utente.",
    "azione_pc": "nessuna" | "apri_browser" | "apri_esplora_file" | "alza_volume" | "abbassa_volume" | "schermo_intero" | "sposta_finestra_destra" | "sposta_finestra_sinistra" | "sposta_finestra_su" | "sposta_finestra_giu"
}
"""

def interroga_jarvis_stream(prompt_utente, cronologia_chat=[]):
    """Interroga Ollama in streaming, restituendo le frasi al volo e il JSON alla fine."""
    messaggi = [{"role": "system", "content": SYSTEM_PROMPT}]
    messaggi.extend(cronologia_chat)
    messaggi.append({"role": "user", "content": prompt_utente})

    try:
        stream = ollama.chat(
            model=MODELLO_LLM,
            messages=messaggi,
            format='json',
            stream=True  # ATTIVIAMO LO STREAMING
        )
        
        testo_completo = ""
        valore_vocale_estratto = ""
        buffer_frase = ""
        punteggiatura_fine = ['.', '!', '?', ':']

        for chunk in stream:
            frammento = chunk['message']['content']
            testo_completo += frammento
            
            # Estraiamo dinamicamente dal JSON in costruzione usando una Regex sicura
            match = re.search(r'"risposta_vocale"\s*:\s*"((?:[^"\\]|\\.)*)', testo_completo)
            if match:
                # Ripuliamo gli eventuali escape (es. \" o \n)
                testo_attuale = match.group(1).replace('\\"', '"').replace('\\n', ' ')
                nuovi_caratteri = testo_attuale[len(valore_vocale_estratto):]
                valore_vocale_estratto = testo_attuale
                
                if nuovi_caratteri:
                    buffer_frase += nuovi_caratteri
                    
                    # Controlliamo se è finita una frase per poterla inviare alla bocca
                    for p in punteggiatura_fine:
                        if p in buffer_frase:
                            parti = buffer_frase.split(p, 1)
                            frase_da_dire = parti[0] + p
                            # Cedi la frase al programma principale (Yield)
                            yield ("testo", frase_da_dire.strip())
                            buffer_frase = parti[1]
                            break 

        # Svuotiamo eventuali residui nel buffer
        if buffer_frase.strip():
            yield ("testo", buffer_frase.strip())

        # A stream concluso, il JSON è completo. Lo analizziamo.
        dati_jarvis = json.loads(testo_completo)
        cronologia_chat.append({"role": "user", "content": prompt_utente})
        cronologia_chat.append({"role": "assistant", "content": testo_completo})
        
        # Cediamo i dati strutturati per l'Azione PC
        yield ("dati", (dati_jarvis, cronologia_chat))

    except Exception as e:
        print(f"\n[ERRORE DI SISTEMA CERVELLO STREAM]: {e}")
        yield ("dati", (None, cronologia_chat))