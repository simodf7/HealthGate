# Exec:
# cd microservices/report-management
# set PYTHONUTF8=1
# python pdf_generator.py

# Comando per installare l'esportatore PDF:
# python -m playwright install chromium


"""
Libreria per la generazione automatica di schede paziente HTML e PDF da dati JSON
================================================================================

Versione semplificata per database HealthGate con campi ridotti.

Campi supportati:
- Anagrafici: firstname, lastname, birth_date, sex, social_sec_number
- Visita: data, id, created_at
- Medici: diagnosi, sintomi, trattamento, decisione, motivazione

Funzioni principali:
- genera_scheda_da_json(json_data, output_html, template_path)
- genera_scheda_pdf_da_json(json_data, output_pdf, template_path, mantieni_html)
- stampa_html_in_pdf(html_path, output_pdf)
- crea_report_medico(dati_report, filename, template_path)
"""

import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import traceback

base_dir = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.abspath(os.path.join(base_dir, "scheda_paziente.html"))


def carica_template_html(percorso_template=template_path):
    """
    Carica il template HTML per la scheda paziente dal file system.

    Args:
        percorso_template (str): Percorso del file HTML template

    Returns:
        str: Contenuto del file HTML template, None se errore
    """
    try:
        with open(percorso_template, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"❌ Errore: Template HTML non trovato: {percorso_template}")
        return None
    except Exception as e:
        print(f"❌ Errore nella lettura del template: {e}")
        return None


def mappa_campi_json_a_html(dati_json):
    """
    Converte i dati JSON del paziente in una mappatura per i campi HTML.
    
    Gestisce solo i campi presenti nel database HealthGate:
    - Anagrafici: firstname, lastname, birth_date, sex, social_sec_number
    - Visita: data, id, created_at
    - Medici: diagnosi, sintomi, trattamento, decisione, motivazione

    Args:
        dati_json (dict): Dizionario con i dati del paziente

    Returns:
        dict: Mappatura campo_html -> valore_da_inserire
    """
    mapping = {}

    # Dati anagrafici
    mapping['lastname'] = dati_json.get('lastname', '')
    mapping['firstname'] = dati_json.get('firstname', '')
    mapping['birth_date'] = dati_json.get('birth_date', '')
    mapping['sex'] = dati_json.get('sex', '')
    mapping['social_sec_number'] = dati_json.get('social_sec_number', '')

    # Informazioni visita
    mapping['data'] = dati_json.get('data', '')
    
    # Gestione ID (può essere int o dict MongoDB)
    id_val = dati_json.get('id', '')
    if isinstance(id_val, dict) and '$numberInt' in id_val:
        mapping['id'] = str(id_val['$numberInt'])
    else:
        mapping['id'] = str(id_val) if id_val else ''

    # Formattazione created_at
    created_at = dati_json.get('created_at', '')
    if created_at:
        try:
            if isinstance(created_at, str):
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                mapping['created_at'] = dt.strftime('%d/%m/%Y %H:%M:%S')
            else:
                mapping['created_at'] = str(created_at)
        except:
            mapping['created_at'] = str(created_at)

    # Informazioni mediche
    mapping['diagnosi'] = dati_json.get('diagnosi', '')
    mapping['sintomi'] = dati_json.get('sintomi', '')
    mapping['trattamento'] = dati_json.get('trattamento', '')
    mapping['decisione'] = dati_json.get('decisione', '')
    mapping['motivazione'] = dati_json.get('motivazione', '')

    print("✅ Mappatura JSON->HTML generata:", mapping)
    return mapping


def compila_scheda_da_json(dati_json, template_html):
    """
    Compila il template HTML con i dati del paziente utilizzando BeautifulSoup.

    Args:
        dati_json (dict): Dizionario con i dati del paziente
        template_html (str): Contenuto del template HTML

    Returns:
        str: HTML compilato con i dati del paziente
    """
    soup = BeautifulSoup(template_html, 'html.parser')
    mapping = mappa_campi_json_a_html(dati_json)

    # Compila tutti i campi
    for campo_name, valore in mapping.items():
        if not valore:
            continue

        elemento = soup.find(attrs={"name": campo_name})
        
        if elemento:
            if elemento.name == 'input':
                elemento['value'] = str(valore)
                print(f"✅ Input compilato: {campo_name} = {valore}")
            elif elemento.name == 'textarea':
                elemento.string = str(valore)
                print(f"✅ Textarea compilato: {campo_name} = {valore}")

    return str(soup)


def genera_scheda_da_json(dati_json, output_html=None, template_path=template_path):
    """
    Genera scheda HTML da dizionario JSON.

    Args:
        dati_json (dict): Dizionario completo con i dati del paziente
        output_html (str, optional): Percorso file HTML output
        template_path (str): Percorso del template HTML

    Returns:
        dict: {"html": path, "success": bool, "error": msg}
    """
    
    # Carica template
    template_html = carica_template_html(template_path)
    if not template_html:
        return {
            "html": None, 
            "success": False, 
            "error": f"Template HTML non trovato: {template_path}"
        }
    
    # Genera nome file se non specificato
    if not output_html:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        lastname = dati_json.get('lastname', '')
        firstname = dati_json.get('firstname', '')
        
        if lastname and firstname:
            nome_paziente = f"{firstname}{lastname}".replace(' ', '_')
            nome_paziente = ''.join(c for c in nome_paziente if c.isalnum() or c == '_')
            output_html = f"{timestamp}_{nome_paziente}-Report.html"
        else:
            output_html = f"{timestamp}-Paziente-Report.html"
        
        print(f"📝 Nome file auto-generato: {output_html}")
    
    # Compila template
    try:
        html_compilato = compila_scheda_da_json(dati_json, template_html)
        print("✅ Template compilato con successo")
    except Exception as e:
        return {
            "html": None,
            "success": False,
            "error": f"Errore durante la compilazione del template: {str(e)}"
        }
    
    # Salva file
    try:
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_compilato)
        print(f"✅ Scheda paziente generata con successo: {output_html}")
        return {
            "html": os.path.abspath(output_html),
            "success": True
        }
    except Exception as e:
        return {
            "html": None,
            "success": False,
            "error": f"Errore nel salvataggio del file: {str(e)}"
        }


def stampa_html_in_pdf(html_path, output_pdf):
    """
    Converte un file HTML in PDF utilizzando Playwright e Chromium.

    Args:
        html_path (str): Percorso assoluto del file HTML
        output_pdf (str): Percorso dove salvare il PDF

    Returns:
        None

    Raises:
        Exception: Per errori durante la conversione
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f'file://{html_path}')
            
            page.pdf(
                path=output_pdf, 
                format="A4", 
                print_background=True,
                margin={
                    "top": "5mm",
                    "bottom": "5mm", 
                    "left": "5mm",
                    "right": "5mm"
                }
            )
            
            browser.close()
            
        print(f"✅ PDF generato con successo: {output_pdf}")
        
    except Exception as e:
        print(f"❌ Errore durante la conversione HTML->PDF: {e}")
        raise


def genera_scheda_pdf_da_json(dati_json, output_pdf=None, template_path=template_path, mantieni_html=False):
    """
    Funzione completa che genera una scheda paziente PDF partendo da dati JSON.
    Correzioni:
     - assicura che output_pdf abbia estensione .pdf
     - se output_pdf è una directory la usa come cartella di destinazione
    """
    # Prepara nome paziente per i fallback
    lastname = dati_json.get('lastname', '')
    firstname = dati_json.get('firstname', '')
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    # Costruzione del nome PDF di default (corretto con .pdf)
    if lastname and firstname:
        nome_paziente = f"{lastname}_{firstname}".replace(' ', '_')
        nome_paziente = ''.join(c for c in nome_paziente if c.isalnum() or c == '_')
        default_pdf_name = f"{timestamp}_{nome_paziente}-Report.pdf"
    else:
        default_pdf_name = f"{timestamp}_{nome_paziente}-Report.pdf"

    # Se non è stato passato output_pdf -> usa default dentro cartella "pdf"
    if not output_pdf:
        output_pdf = os.path.join("pdf", default_pdf_name)
    else:
        # Se l'utente ha passato una directory, mette il file lì dentro
        if os.path.isdir(output_pdf):
            output_pdf = os.path.join(output_pdf, default_pdf_name)
        else:
            root, ext = os.path.splitext(output_pdf)
            # se non c'è estensione, aggiungi .pdf
            if ext == "":
                output_pdf = output_pdf + ".pdf"
            # se estensione diversa da .pdf, sostituiscila con .pdf
            elif ext.lower() != ".pdf":
                output_pdf = root + ".pdf"
            # altrimenti: ha già .pdf -> lascia così

    # Assicura che le cartelle esistano
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    os.makedirs("html", exist_ok=True)

    # Genera HTML temporaneo (sempre nella cartella "html")
    pdf_name = os.path.splitext(os.path.basename(output_pdf))[0]
    html_temporaneo = os.path.join("html", f"{pdf_name}_temp.html")

    # Genera HTML (usa la funzione esistente)
    risultato_html = genera_scheda_da_json(
        dati_json,
        output_html=html_temporaneo,
        template_path=template_path
    )

    if not risultato_html["success"]:
        return {
            "pdf": None,
            "html": None,
            "success": False,
            "error": f"Errore nella generazione HTML: {risultato_html['error']}"
        }

    html_path = risultato_html["html"]

    # Converti HTML -> PDF
    try:
        stampa_html_in_pdf(html_path, output_pdf)
    except Exception as e:
        # pulizia in caso di errore
        if not mantieni_html and os.path.exists(html_path):
            try:
                os.remove(html_path)
            except:
                pass
        return {
            "pdf": None,
            "html": html_path if mantieni_html else None,
            "success": False,
            "error": f"Errore nella conversione PDF: {str(e)}"
        }

    # Cleanup opzionale
    risultato_finale = {
        "pdf": os.path.abspath(output_pdf),
        "success": True
    }

    if mantieni_html:
        risultato_finale["html"] = os.path.abspath(html_path)
    else:
        try:
            os.remove(html_path)
            risultato_finale["html"] = None
        except Exception as e:
            risultato_finale["html"] = os.path.abspath(html_path)

    return risultato_finale



def crea_report_medico(dati_report, filename, template_path=template_path):
    """
    Funzione "ponte" compatibile con l'applicazione Streamlit esistente.
    
    Riceve i dati dall'applicazione e avvia la generazione del PDF.

    Args:
        dati_report (dict): Dizionario con chiave 'data' contenente i dati paziente
        filename (str): Percorso completo dove salvare il PDF
        template_path (str): Percorso del template HTML
    
    Returns:
        dict: Risultato dell'operazione di generazione PDF
    """
    dati_paziente_json = dati_report.get('data')

    if not dati_paziente_json:
        print("❌ Errore: la chiave 'data' non è stata trovata nel dizionario del report.")
        return {
            "pdf": None,
            "success": False,
            "error": "Dati del paziente non trovati (chiave 'data' mancante)."
        }
    
    return genera_scheda_pdf_da_json(
        dati_json=dati_paziente_json,
        output_pdf=filename,
        template_path=template_path,
        mantieni_html=False
    )


# ============= ESEMPIO DI UTILIZZO =============
if __name__ == "__main__":
    # Dati di esempio dal tuo MongoDB
    dati_esempio = {
        "data": "2025-10-04",
        "diagnosi": "Tonsillite acuta",
        "sintomi": "Mal di gola, febbre, difficoltà a deglutire",
        "trattamento": "Antibiotico e riposo",
        "decisione": "Pronto soccorso necessario",
        "motivazione": "Febbre alta persistente e difficoltà respiratorie",
        "id": {"$numberInt": "2"},
        "social_sec_number": "CMPLAE01M49F839Z",
        "firstname": "Ale",
        "lastname": "Campanella",
        "birth_date": "2001-08-09",
        "sex": "F",
        "created_at": "2025-10-04T12:42:57.201078"
    }
    
    print("=" * 60)
    print("TEST GENERAZIONE PDF")
    print("=" * 60)
    
    risultato = genera_scheda_pdf_da_json(dati_esempio, mantieni_html=True)
    
    if risultato["success"]:
        print(f"\n🎉 PDF generato con successo!")
        print(f"📄 PDF: {risultato['pdf']}")
        if risultato.get('html'):
            print(f"📝 HTML: {risultato['html']}")
    else:
        print(f"\n❌ Errore: {risultato['error']}")