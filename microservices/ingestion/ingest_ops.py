import os
import json
from datetime import datetime
from langchain_core.messages import HumanMessage

def transcribe_audio_file(stt_model, audio_path: str) -> str:
    """
    Trascrive un singolo file audio con Whisper
    """
    try:
        print(f"Trascrizione in corso: {audio_path}")
        result = stt_model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        print(f"Errore durante la trascrizione di {audio_path}: {e}")
        raise



def save_transcription(text: str, filename: str) -> str:
    """
    Salva la trascrizione in JSON con testo e timestamp
    """
    try:
        output_path = os.path.join("transcripts", filename + ".json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "transcription": text,
                "timestamp": datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
            }, f, indent=2)
        print(f"Trascrizione salvata correttamente in: {output_path}")
        return output_path
    except Exception as e:
        print(f"Errore durante il salvataggio: {e}")
        raise

# Funzione per correggere la trascrizione clinica
def correct_transcription(llm, transcription: str) -> str:
 
    prompt = f"""
    Sei un assistente medico. Ti fornisco una trascrizione vocale di un paziente che potrebbe contenere:
     - errori ortografici
     - errori grammaticali
     - errori dovuti a rumori ambientali generici (es. traffico, clacson, sirene)
     - errori dovuti a rumori meccanici (es. ventilatori, condizionatori, macchinari generici)
     - errori dovuti a voci non rilevanti (es. persone che parlano in sottofondo, radio, televisione, musica accesa)
     - errori dovuti a rumori fisici legati al paziente o al microfono (es. colpi di tosse, starnuti, click, tocchi al microfono)

    Il tuo compito è:
    - Correggere tutti questi errori
    - Standardizzare i termini medici e riportarli in forma chiara (es. "dolore al petto" → "dolore toracico").
    - Conservare tutte le informazioni cliniche senza aggiungerne di nuove.
    - Non modificare le quantità (es. farmaci, dosaggi, durata dei sintomi).
    - Restituire soltanto il testo corretto e leggibile, senza spiegazioni aggiuntive.

    ESEMPIO:
    [Input]
    "Ciao ho dolore stomaco nausea vomito sangue pressione bassa 90 60"
    [Output]
    "Il paziente riferisce dolore addominale, nausea e vomito ematico. Presenta ipotensione (PA 90/60 mmHg)."
 
    
    Trascrizione da correggere:
    ---
    {transcription}
    ---
    
    Output atteso:
    """
    message = HumanMessage(content=prompt)
    response = llm.invoke([message])
    return response.content