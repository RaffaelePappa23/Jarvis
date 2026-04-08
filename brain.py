import ollama
import json

# Definiamo il modello che hai appena scaricato
MODELLO_LLM = 'llama3' 

# Il System Prompt: l'anima di Jarvis e le sue regole ferree
SYSTEM_PROMPT = """Sei JARVIS, la mia intelligenza artificiale personale e assistente di sistema.
Rispondi SEMPRE in italiano, qualunque cosa ti venga chiesta.
Il tuo tono è formale, educato, servizievole ma con un tocco di sottile sarcasmo.


REGOLE FONDAMENTALI:
1. Devi SEMPRE rispondere utilizzando ESCLUSIVAMENTE un formato JSON valido. 
2. Non aggiungere testo testuale prima o dopo il blocco JSON.
3. Se ti chiedo di compiere un'azione sul PC, devi identificarla dal contesto.

Formato JSON richiesto (usa esattamente queste chiavi):
{
    "risposta_vocale": "La frase che dirai ad alta voce per rispondere all'utente.",
    "azione_pc": "nessuna" | "sposta_finestra_destra" | "sposta_finestra_sinistra" | "sposta_finestra_su" | "sposta_finestra_giu"
}
"""

def interroga_jarvis(prompt_utente, cronologia_chat=[]):
    """Invia il messaggio a Ollama locale e forza l'output strutturato."""
    messaggi = [{"role": "system", "content": SYSTEM_PROMPT}]
    messaggi.extend(cronologia_chat)
    messaggi.append({"role": "user", "content": prompt_utente})

    try:
        # Chiamata al modello locale
        response = ollama.chat(
            model=MODELLO_LLM,
            messages=messaggi,
            format='json' 
        )
        
        risposta_testo = response['message']['content']
        dati_jarvis = json.loads(risposta_testo)
        
        cronologia_chat.append({"role": "user", "content": prompt_utente})
        cronologia_chat.append({"role": "assistant", "content": risposta_testo})
        
        return dati_jarvis, cronologia_chat

    except json.JSONDecodeError:
        print("\n[ERRORE] Jarvis non ha usato il formato JSON.")
        return None, cronologia_chat
    except Exception as e:
        print(f"\n[ERRORE DI SISTEMA]: {e}")
        return None, cronologia_chat

