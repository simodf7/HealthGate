from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import os
 
# Impostazione delle credenziali Google Cloud
os.environ["GOOGLE_API_KEY"] = "AIzaSyBuxrY6tmzNZhxxZxZKIjlsI2GBEwXpWMo"
 
# Funzione per correggere la trascrizione clinica
def correct_transcription(transcription: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
 
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
    "fem 62 anni dolore stomaco nausea vomito sangue pressione bassa 90 60"
    [Output]
    "Paziente femmina di 62 anni con dolore addominale, nausea e vomito ematico. Ipotensione (PA 90/60 mmHg)."
 
    
    Trascrizione da correggere:
    ---
    {transcription}
    ---
    
    Output atteso:
    """
    message = HumanMessage(content=prompt)
    response = llm.invoke([message])
    return response.content
 
# Esecuzione del processo
if __name__ == "__main__":
    transcription = (
        " Fatt scente maschri 45 anni dolore peto da due ore sudore preto e spiro corto prezo. A stirina a casa 3-2-5, ma dolore non migliora nessun trauma recente comadores forte da benti. Ania l'ergienege."    )
    corrected_transcription = correct_transcription(transcription)
    print("Trascrizione corretta:", corrected_transcription)