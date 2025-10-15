import re
import time
from pypdf import PdfReader 
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from tqdm import tqdm
from config import API_KEY

os.environ["GOOGLE_API_KEY"] = API_KEY

def clean_text(text: str) -> str:
    # Rimuovere soft hyphen
    text = re.sub(r"\xad", "", text)
    
    # 2. Rimuove newline interni (multi-colonna), salvo punteggiatura forte o titoli/elenco
    text = re.sub(r"(?<![.!?:;])\n(?!\s*[A-Z0-9□■])", "", text)

    # 3. Riduce spazi multipli
    text = re.sub(r"\s{2,}", " ", text)

    # 4. Corregge spazi strani con apostrofo (d ’ → d’)
    text = re.sub(r"\s’", r"’", text)

    text = re.sub(r'(?<=[a-zà-ú0-9])\.(?=[A-ZÀ-Ýa-zà-ú])', ". ", text)


    # Rimuovere underscore multipli
    text = re.sub(r"_+", "", text)

    # Uniformare i line break tra paragrafi
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    text = re.sub(r"([’'])\s+", r"\1", text)

    # Rimuove trattino seguito da spazio o newline e ricompone la parola
    text = re.sub(r"-\s+", "", text)

    # 🔹 Ricompone parole spezzate da sillabazione
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    text = re.sub(r"[■][^\n,.;:]*", "", text)

    text = re.sub(
        r'^[ \t]*[□]\s*(.+?)(?:\r?\n|$)',
        lambda m: m.group(1).strip() + (". "),
        text,
        flags=re.MULTILINE
    )

    
    text = re.sub(r'^[A-ZÀÖØÞ]{2,}(?:\s+[A-ZÀÖØÞ]{2,})*', '', text, flags=re.MULTILINE)

    return text
    


def model_processing(llm, input_text:str) -> str: 
    prompt = f"""
        Sei un assistente di pulizia testi. 
        Ti fornirò un blocco di testo, originariamente estratto da un PDF, che poi è stato pre-processato \\
        con alcune regole di pulizia base con regex (rimozione di trattini, unione di righe spezzate, eccetera).

        Tuttavia, il testo potrebbe ancora contenere una serie di errori. 

        Il tuo compito è quello di: 
        - CORREGGERE errori di spaziatura (es. "elem ento" invece di "elemento")
        - CORREGGERE errori dovuti a OCR imperfetto (es. "deU’infanzia" invece di "dell’infanzia")
        - CORREGGERE O RIMUOVERE errori dovuti a letture errate di OCR di tabelle o elenchi
        - RIMUOVERE presenza indesiderata di numeri di pagina, intestazioni, piè di pagina 
        - RIMUOVERE presenza indesiderata di indici o sommari 
        - RIMUOVERE testi relativi a intestazioni di sezioni o capitoli che non sono parte del contenuto principale \\
            (es. "Università Campus Biomedico di Roma Società Italiana Sistema 118
            Linee di indirizzo terapeutico - Medicina di emergenza territoriale 118") 
        - RIMUOVERE testi estratti da copertine o pagine non rilevanti 
        - CORREGGERE elenchi che non sono stati formattati correttamente 
        - RIMUOVERE citazioni inutili (es. \\
            "La vita di una persona consiste in un insieme di avvenimenti di cui l’ultimo potrebbe anche cambiare il senso di tutto l’insieme” \\
            Italo Calvino)
        - RIMUOVERE bibliografie, sitografie e didascalie di immagini
        - CORREGGERE altri errori vari di formattazione 

        Tieni in considerazione però che:
        - è IMPERATIVO NON riassumere, NON tradurre e NON aggiungere commenti.
        - il testo ottenuto sarà poi splittato in chunk dal RecursiveCharacterTextSplitter \\ 
        con chunk size = 1000 e chunk overlap = 150, \\
        quindi vai pure a capo dove necessario per separare paragrafi o sezioni.
        - DEVI RESTITUIRE soltanto il testo ripulito, pronto per essere salvato in un file .txt.
        - I chunk ottenuti saranno indicizzati per l'utilizzo di un RAG a supporto di un LLM \\
        che deve decidere se un dato paziente, che fornisce i sintomi, deve recarsi o meno al Pronto soccorso \\
        puoi quindi eliminare dei testi che sono completamente ESULI dall'ambito medico 

        NOTA: non preoccuparti se, a valle di questi processamenti, il testo che ottieni è completamente vuoto, \\
        tu restituiscimelo lo stesso con "" 
        
        NOTA 2: Per motivi dovuti a rate limiting, ti fornirò un testo che proviene dall'estrazione di più pagine

        Ecco il testo da ripulire:
        {input_text}

    """

    response = llm.invoke(prompt)
    return response.content



llm = ChatGoogleGenerativeAI(model = "gemini-2.0-flash-lite")
#pdf_path = r"C:\Users\simon\Desktop\HealthGate\HealthGate\varie\documents\Semeiotica medica. Metodologia -Ranuccio Nuti.pdf"
pdf_path = r"C:\Users\simon\Desktop\HealthGate\HealthGate\varie\documents\Manuale-Triage-tml-rev-03-ottobre.pdf"
#pdf_path = r"C:\Users\simon\Desktop\HealthGate\HealthGate\varie\documents\LineeIndirizzoTerapeutico.pdf"
#pdf_path = r"C:\Users\simon\Desktop\HealthGate\HealthGate\varie\documents\manuale_di_triage_per_ladulto_28VbM8T_0LPFt8e.pdf"

reader = PdfReader(pdf_path)
pages = reader.pages
pages = pages[12:393]

with open("manuale_triage.txt", "a", encoding="utf-8", errors="ignore") as file:
    batch_size = 4   # numero di pagine per richiesta
    buffer = []

    for i, page in enumerate(tqdm(pages, desc="Processing pages"), start=1):
        text = page.extract_text()
        if text:
            buffer.append(clean_text(text))

        if len(buffer) == batch_size or i == len(pages):
            combined_text = " ".join(buffer)
            processed = model_processing(llm, combined_text)
            file.write(processed + " ")

            # Salva progresso
            with open("progress.txt", "w") as pf:
                pf.write(str(i + 1))  # la prossima pagina da processare

            buffer = []  
            time.sleep(2)  # rispetta il limite di 30 RPM



        


