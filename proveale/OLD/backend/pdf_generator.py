"""
[BACKEND] pdf_generator.py

Libreria per la generazione automatica di schede paziente HTML e PDF da dati JSON.

================================================================================

Questa libreria converte dati JSON strutturati di pazienti in schede 
paziente HTML compilate e opzionalmente in documenti PDF utilizzando 
un template HTML di base.

Funzioni principali:
- genera_scheda_da_json(json_data, output_html=None, template_path=None): 
  Genera scheda HTML da dizionario JSON
- genera_scheda_pdf_da_json(json_data, output_pdf=None, template_path=None, mantieni_html=False):
  Genera scheda PDF completa da dizionario JSON (workflow completo JSON→HTML→PDF)
- stampa_html_in_pdf(html_path, output_pdf): Converte file HTML esistente in PDF
- carica_template_html(percorso_template): Carica il template HTML base
- mappa_campi_json_a_html(dati_json): Converte dati JSON in mappatura per HTML
- compila_scheda_da_json(dati_json, template_html): Compila il template con i dati

Dipendenze richieste:
- BeautifulSoup4 (bs4): Per manipolazione HTML
- Playwright: Per conversione HTML→PDF con rendering Chromium
- json: Per gestione dati JSON (built-in)
- datetime: Per timestamp (built-in)
- os: Per operazioni su file (built-in)

Workflow supportati:
1. Solo HTML: JSON → HTML
2. Solo conversione: HTML → PDF  
3. Completo: JSON → HTML → PDF (con cleanup automatico)
"""

import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import traceback

base_dir = os.path.dirname(os.path.abspath(__file__))

template_path = os.path.abspath(os.path.join(base_dir, "scheda_paziente_cartacea.html"))

def carica_template_html(percorso_template=template_path):
    """
    Carica il template HTML per la scheda paziente dal file system.
    
    Il template HTML deve contenere i campi form con attributi 'name' 
    corrispondenti ai dati del paziente che verranno compilati automaticamente.

    Args:
        percorso_template (str): Percorso relativo o assoluto del file HTML template.
                               Default: "scheda_paziente_cartacea.html"

    Returns:
        str: Contenuto del file HTML template come stringa, 
             None se il file non viene trovato o si verifica un errore

    Raises:
        FileNotFoundError: Se il template HTML non esiste
        Exception: Per altri errori di lettura file (encoding, permessi, etc.)
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
    Converte i dati JSON del paziente in una mappatura per i campi HTML del form.
    
    Questa funzione è il cuore della conversione: analizza la struttura JSON
    del paziente e crea una mappatura (dizionario) dove le chiavi sono i nomi
    dei campi HTML e i valori sono i dati da inserire nel form.
    
    Gestisce tutti i tipi di campo:
    - Campi di testo semplici (nome, cognome, ecc.)
    - Checkbox singoli (sesso M/F, fonte dati)
    - Checkbox multipli (autorità presenti, provvedimenti) 
    - Rilevazioni parametri vitali per T1, T2, T3
    - Glasgow Coma Scale (GCS) con punteggi
    - Lesioni anatomiche con validazione
    - Gestione trasporto, decesso, rifiuto

    Args:
        dati_json (dict): Dizionario contenente tutti i dati del paziente
                         strutturati secondo lo schema JSON predefinito

    Returns:
        dict: Mappatura campo_html -> valore_da_inserire
              Le chiavi corrispondono agli attributi 'name' dei campi HTML
              I valori possono essere stringhe, liste (per checkbox multipli) 
              o valori specifici per il tipo di campo
              
    Note:
        - Gestisce conversioni case-insensitive per robustezza
        - Supporta format MongoDB ($numberInt, $numberDouble)
        - Valida i dati contro costanti predefinite (parti anatomiche, ecc.)
        - Include debug print per tracciare il processo di mappatura
    """
    mapping = {}

    # ========================================
    # SEZIONE 1: INFORMAZIONI ANAGRAFICHE
    # ========================================
    # Estrae i dati personali del paziente dalla sezione 'dati_paziente'
    mapping['cognome_nome'] = dati_json.get('dati_paziente', {}).get('cognome_nome', '')
    mapping['codice_fiscale'] = dati_json.get('codice_fiscale', '')
    mapping['data_nascita'] = dati_json.get('dati_paziente', {}).get('data_nascita', '')
    mapping['luogo_nascita'] = dati_json.get('dati_paziente', {}).get('luogo_nascita', '')
    mapping['provincia_nascita'] = dati_json.get('dati_paziente', {}).get('provincia_nascita', '')
    
    # Dati di residenza (struttura nidificata nel JSON)
    mapping['residente_a'] = dati_json.get('dati_paziente', {}).get('residenza', {}).get('citta', '')
    mapping['provincia_residenza'] = dati_json.get('dati_paziente', {}).get('residenza', {}).get('provincia', '')
    mapping['via'] = dati_json.get('dati_paziente', {}).get('residenza', {}).get('via', '')
    mapping['numero_civico_residenza'] = dati_json.get('dati_paziente', {}).get('residenza', {}).get('numero_civico', '')
    mapping['telefono'] = dati_json.get('dati_paziente', {}).get('telefono', '')

    # Gestione sesso come checkbox (M/F) con conversione maiuscola
    sesso_paziente = str(dati_json.get('dati_paziente', {}).get('sesso') or '').upper()
    if sesso_paziente == 'M':
        mapping['sesso'] = 'M'
    elif sesso_paziente == 'F':
        mapping['sesso'] = 'F'
    
    # ========================================
    # SEZIONE 2: FONTE DATI 
    # ========================================
    # Gestisce da dove provengono i dati (paziente, parente, documento)
    # Conversione case-insensitive per robustezza dei dati in input
    fonte_dati = str(dati_json.get('dati_paziente', {}).get('fonte_dati') or '').lower()
    if fonte_dati == 'paziente':
        mapping['fonte_dati_paziente'] = 'paziente'
    elif fonte_dati == 'parente':
        mapping['fonte_dati_parente'] = 'parente'
    elif fonte_dati == 'documento':
        mapping['fonte_dati_documento'] = 'documento'
    
    # Campo testo libero per specificare tipo documento o altra fonte
    mapping['documento_altro'] = dati_json.get('dati_paziente', {}).get('fonte_dati_altro', '')
    
    # ========================================
    # SEZIONE 3: INFORMAZIONI CHIAMATA
    # ========================================
    # Estrae tutti i dati relativi alla chiamata di emergenza
    chiamata = dati_json.get('chiamata', {})
    mapping['data'] = chiamata.get('data', '')
    
    # Orari della chiamata e intervento (struttura nidificata 'orari')
    orari_chiamata = chiamata.get('orari', {})
    mapping['h_chiamata'] = orari_chiamata.get('h_chiamata', '')
    mapping['h_partenza'] = orari_chiamata.get('h_partenza', '')
    mapping['h_sul_posto'] = orari_chiamata.get('h_arrivo_sul_posto', '')
    mapping['h_partenza_posto'] = orari_chiamata.get('h_partenza_dal_posto', '')
    mapping['h_in_ps'] = orari_chiamata.get('h_arrivo_ps', '')
    mapping['h_libero_operativo'] = orari_chiamata.get('h_libero_operativo', '')
    
    # Informazioni aggiuntive della chiamata
    mapping['luogo_intervento'] = chiamata.get('luogo_intervento', '')
    mapping['condizione_riferita'] = chiamata.get('condizione_riferita', '')
    mapping['recapito_telefonico'] = chiamata.get('recapito_telefonico', '')
    
    # Codici operativi (uscita e rientro) - conversione a stringa maiuscola
    mapping['codice_uscita'] = str(chiamata.get('codice_uscita', '')).upper()
    mapping['codice_rientro'] = str(chiamata.get('codice_rientro', ''))   
    # ========================================
    # SEZIONE 4: DATI AMBULANZA ED EQUIPAGGIO
    # ========================================
    # Gestisce informazioni su ambulanza e personale intervenuto
    ambulanza = dati_json.get('ambulanza', {})
    
    # Sigle organizzazioni (CRI, SEL, etc.)
    sigle_ambulanza = ambulanza.get('sigla', {})
    mapping['cri'] = sigle_ambulanza.get('CRI', '')
    mapping['sel'] = sigle_ambulanza.get('Sel', '')
    
    # Composizione equipaggio
    equipaggio = ambulanza.get('equipaggio', {})
    mapping['aut'] = equipaggio.get('autista', '')
    mapping['socc1'] = equipaggio.get('soccorritore_1', '')
    mapping['socc2'] = equipaggio.get('soccorritore_2', '')
    mapping['socc3'] = equipaggio.get('soccorritore_3', '')
    mapping['ip'] = equipaggio.get('infermiere', '')
    mapping['medico'] = equipaggio.get('medico', '')
    
    # ========================================
    # SEZIONE 5: AUTORITÀ PRESENTI SUL POSTO
    # ========================================
    # Gestisce checkbox multipli per le varie autorità che possono essere presenti
    autorita_presenti = dati_json.get('autorita_presenti', {})
    autorità_selezionate = []
    
    # Mappatura per gestire eventuali discrepanze tra nomi JSON e template HTML
    mappatura_autorita = {
        'vigili_del_fuoco': 'vigili_fuoco',  # Esempio: JSON usa underscore, HTML no
        'polizia_locale': 'polizia_municipale' 
    }
    
    # Elabora ogni autorità presente (escluso il campo descrittivo)
    for key, value in autorita_presenti.items():
        if key != 'altro_descrizione' and value:
            # Usa la mappatura se esiste, altrimenti mantieni il nome originale
            html_key = mappatura_autorita.get(key, key)
            autorità_selezionate.append(html_key)
    
    # Se c'è una descrizione per "altro", aggiungi anche il checkbox "altro"
    if autorita_presenti.get('altro_descrizione', '').strip():
        autorità_selezionate.append('altro')
    
    mapping['autorita_presenti'] = autorità_selezionate
    mapping['autorita_altro'] = autorita_presenti.get('altro_descrizione', '')   
    # ========================================
    # SEZIONE 6: RILEVAZIONI PARAMETRI VITALI (T1, T2, T3)
    # ========================================
    # Gestisce le rilevazioni dei parametri vitali effettuate in tre momenti diversi
    rilevazioni = dati_json.get('rilevazioni', [])
    
    # Mappe di conversione per standardizzare i valori dei parametri vitali
    # secondo la terminologia medica standard
    mappatura_coscienza = {
        'A': 'sveglio',        # Alert - paziente sveglio e cosciente
        'V': 'risp_voce',      # Voice - risponde agli stimoli vocali
        'P': 'risp_dolore',    # Pain - risponde solo al dolore
        'U': 'incosciente'     # Unresponsive - incosciente
    }
    
    mappatura_cute = {
        'normale': 'normale',
        'pallida': 'pallida', 
        'cianotica': 'cianotica',  # Colorazione bluastra da carenza ossigeno
        'sudata': 'sudata'
    }
    
    mappatura_respiro = {
        'normale': 'normale',
        'tachipnoico': 'tachipnoico',    # Respirazione accelerata
        'bradipnoico': 'bradipnoico',    # Respirazione rallentata
        'assente': 'assente'
    }
    
    # Elabora ogni rilevazione per i tempi T1, T2, T3
    for rilevazione in rilevazioni:
        tempo = str(rilevazione.get('tempo') or '').upper()
        if tempo in ['T1', 'T2', 'T3']:
            t_num = tempo.lower()  # Converte in t1, t2, t3 per i nomi dei campi
            
            # Orario della rilevazione
            mapping[f'orario_{t_num}'] = rilevazione.get('ora', '')
            
            # Stato di coscienza (usando la mappatura AVPU standard)
            coscienza_val = str(rilevazione.get('coscienza') or '').upper()
            if coscienza_val in mappatura_coscienza:
                mapping[f'coscienza_{t_num}'] = mappatura_coscienza[coscienza_val]
            
            # Stato della cute
            cute_val = str(rilevazione.get('cute') or '').lower()
            if cute_val in mappatura_cute:
                mapping[f'cute_{t_num}'] = mappatura_cute[cute_val]
            
            # Tipo di respirazione
            respiro_val = str(rilevazione.get('respiro') or '').lower()
            if respiro_val in mappatura_respiro:
                mapping[f'respiro_{t_num}'] = mappatura_respiro[respiro_val]
            
            # Parametri numerici vitali - gestisce sia valori diretti che formato MongoDB
            # SpO2 (saturazione ossigeno percentuale)
            spo2_data = rilevazione.get('spo2_percent', '')
            if isinstance(spo2_data, dict) and '$numberInt' in spo2_data:
                mapping[f'spo2_{t_num}'] = str(spo2_data['$numberInt'])
            else:
                mapping[f'spo2_{t_num}'] = str(spo2_data) if spo2_data else ''
            
            # FC (frequenza cardiaca in battiti per minuto)
            fc_data = rilevazione.get('fc_bpm', '')
            if isinstance(fc_data, dict) and '$numberInt' in fc_data:
                mapping[f'fc_{t_num}'] = str(fc_data['$numberInt'])
            else:
                mapping[f'fc_{t_num}'] = str(fc_data) if fc_data else ''
            
            # PA (pressione arteriosa in mmHg)
            mapping[f'pa_{t_num}'] = rilevazione.get('pa_mmhg', '')
            
            # Glicemia (in mg/dl)
            glicemia_data = rilevazione.get('glicemia_mg_dl', '')
            if isinstance(glicemia_data, dict) and '$numberInt' in glicemia_data:
                mapping[f'glicemia_{t_num}'] = str(glicemia_data['$numberInt'])
            else:
                mapping[f'glicemia_{t_num}'] = str(glicemia_data) if glicemia_data else ''
            
            # Temperatura corporea (in gradi Celsius)
            temp_data = rilevazione.get('temperatura_c', '')
            if isinstance(temp_data, dict) and '$numberDouble' in temp_data:
                mapping[f'temperatura_{t_num}'] = str(temp_data['$numberDouble'])
            else:
                mapping[f'temperatura_{t_num}'] = str(temp_data) if temp_data else ''
            
            # ========================================
            # GLASGOW COMA SCALE (GCS) - Valutazione neurologica
            # ========================================
            # La GCS valuta il livello di coscienza su tre parametri:
            # - Apertura occhi (1-4), Risposta verbale (1-5), Risposta motoria (1-6)
            gcs_data = rilevazione.get('gcs', {})
            if gcs_data:
                # Estrae valori gestendo formato MongoDB ($numberInt)
                def estrai_valore_numerico(dato):
                    if isinstance(dato, dict) and '$numberInt' in dato:
                        return str(dato['$numberInt'])
                    return str(dato) if dato else ''
                
                apertura_occhi = estrai_valore_numerico(gcs_data.get('apertura_occhi', ''))
                risposta_verbale = estrai_valore_numerico(gcs_data.get('risposta_verbale', ''))
                risposta_motoria = estrai_valore_numerico(gcs_data.get('risposta_motoria', ''))
                totale_gcs = estrai_valore_numerico(gcs_data.get('totale', ''))
                
                # Mappatura dei punteggi GCS per questo tempo di rilevazione
                mapping[f'gcs_apertura_occhi_{t_num}'] = apertura_occhi
                mapping[f'gcs_risposta_verbale_{t_num}'] = risposta_verbale
                mapping[f'gcs_risposta_motoria_{t_num}'] = risposta_motoria
                mapping[f'gcs_totale_{t_num}'] = totale_gcs    
    # ========================================
    # SEZIONE 7: ANNOTAZIONI LIBERE
    # ========================================
    # Campo di testo libero per note aggiuntive del personale sanitario
    mapping['annotazioni'] = dati_json.get('annotazioni', '')

    # ========================================
    # SEZIONE 8: PROVVEDIMENTI TERAPEUTICI
    # ========================================
    # Gestisce tutti i trattamenti e procedure effettuate sul paziente
    # Organizzati per categorie: respiro, circolo, immobilizzazione, altro
    
    provvedimenti_data = dati_json.get('provvedimenti', {})
    
    # Struttura per tracciare i checkbox selezionati per ogni categoria
    provvedimenti_selezionati = {
        'respiro': [],
        'circolo': [],
        'immobilizzazione': [],
        'altro': []
    }
    
    # ----------------------------------------
    # CATEGORIA RESPIRO - Supporto respiratorio
    # ----------------------------------------
    respiro_data = provvedimenti_data.get('respiro', {})
    
    # Checkbox semplici (boolean true/false)
    if respiro_data.get('aspirazione', False):
        provvedimenti_selezionati['respiro'].append('aspirazione')
    if respiro_data.get('cannula_orofaringea', False):
        provvedimenti_selezionati['respiro'].append('cannula_orofaringea')
    if respiro_data.get('monitor_spo2', False):
        provvedimenti_selezionati['respiro'].append('o2_monitor')  # Note: template usa nome diverso
    if respiro_data.get('ventilazione', False):
        provvedimenti_selezionati['respiro'].append('ventilazione')
    
    # Ossigeno con valore numerico (litri/minuto)
    # Se ha un valore valido, seleziona checkbox e salva il valore
    ossigeno_val = respiro_data.get('ossigeno_l_min')
    if ossigeno_val is not None and ossigeno_val is not False and str(ossigeno_val).strip():
        provvedimenti_selezionati['respiro'].append('ossigeno_lt')
        mapping['ossigeno_l_min'] = str(ossigeno_val) 
    
    # Intubazione con numero (dimensione tubo)
    # Gestisce anche formato MongoDB
    intubazione_val = respiro_data.get('intubazione_num')
    if intubazione_val is not None and intubazione_val is not False:
        if isinstance(intubazione_val, dict) and '$numberInt' in intubazione_val:
            intubazione_val = intubazione_val['$numberInt']
        if str(intubazione_val).strip():
            provvedimenti_selezionati['respiro'].append('intubazione')
            mapping['intubazione_num'] = str(intubazione_val) 
    
    # ----------------------------------------
    # CATEGORIA CIRCOLO - Supporto cardiovascolare
    # ----------------------------------------
    circolo_data = provvedimenti_data.get('circolo', {})
    
    # Checkbox semplici
    if circolo_data.get('emostasi', False):
        provvedimenti_selezionati['circolo'].append('emostasi')
    if circolo_data.get('accesso_venoso', False):
        provvedimenti_selezionati['circolo'].append('accesso_venoso')
    if circolo_data.get('monitor_ecg', False):
        provvedimenti_selezionati['circolo'].append('monitor_ecg')
    if circolo_data.get('monitor_nibp', False):
        provvedimenti_selezionati['circolo'].append('monitor_nibp')
    
    # MCE (Massaggio Cardiaco Esterno) con durata in minuti
    mce_val = circolo_data.get('mce_min')
    if mce_val is not None and mce_val is not False:
        if isinstance(mce_val, dict) and '$numberInt' in mce_val:
            mce_val = mce_val['$numberInt']
        if str(mce_val).strip():
            provvedimenti_selezionati['circolo'].append('mce_min')
            mapping['mce_min'] = str(mce_val)
    
    # DAE (Defibrillatore Automatico Esterno) con numero shock
    dae_val = circolo_data.get('dae_num_shock')
    if dae_val is not None and dae_val is not False:
        if isinstance(dae_val, dict) and '$numberInt' in dae_val:
            dae_val = dae_val['$numberInt']
        if str(dae_val).strip():
            provvedimenti_selezionati['circolo'].append('dae_num_shock')
            mapping['dae_num_shock'] = str(dae_val) 
    
    # ----------------------------------------
    # CATEGORIA IMMOBILIZZAZIONE - Stabilizzazione traumi
    # ----------------------------------------
    immobilizzazione_data = provvedimenti_data.get('immobilizzazione', {})
    
    if immobilizzazione_data.get('collare_cervicale', False):
        provvedimenti_selezionati['immobilizzazione'].append('collare_cervicale')
    if immobilizzazione_data.get('ked', False):
        provvedimenti_selezionati['immobilizzazione'].append('ked')
    if immobilizzazione_data.get('barella_cucchiaio', False):
        provvedimenti_selezionati['immobilizzazione'].append('barella_cucchiaio')
    if immobilizzazione_data.get('tavola_spinale', False):
        provvedimenti_selezionati['immobilizzazione'].append('tavola_spinale')
    if immobilizzazione_data.get('steccobenda', False):
        provvedimenti_selezionati['immobilizzazione'].append('steccobenda')
    if immobilizzazione_data.get('materassino_depressione', False):
        # Note: template HTML usa nome leggermente diverso
        provvedimenti_selezionati['immobilizzazione'].append('materasso_depressione')
    
    # ----------------------------------------
    # CATEGORIA ALTRO - Provvedimenti vari
    # ----------------------------------------
    altro_data = provvedimenti_data.get('altro', {})
    
    if altro_data.get('coperta_isotermica', False):
        provvedimenti_selezionati['altro'].append('coperta_isotermica')
    if altro_data.get('medicazione', False):
        provvedimenti_selezionati['altro'].append('medicazione')
    if altro_data.get('ghiaccio', False):
        provvedimenti_selezionati['altro'].append('ghiaccio')
    if altro_data.get('osservazione', False):
        provvedimenti_selezionati['altro'].append('osservazione')
    
    # Provvedimenti personalizzati (custom 1 e 2) con descrizione libera
    custom1_val = altro_data.get('custom_1', '')
    if custom1_val and str(custom1_val).strip():
        provvedimenti_selezionati['altro'].append('altro1')
        mapping['custom_1_value'] = str(custom1_val)
    
    custom2_val = altro_data.get('custom_2', '')
    if custom2_val and str(custom2_val).strip():
        provvedimenti_selezionati['altro'].append('altro2')
        mapping['custom_2_value'] = str(custom2_val)
    
    # Salva tutti i provvedimenti selezionati nella mappatura finale
    for categoria, valori in provvedimenti_selezionati.items():
        if valori:  # Solo se ci sono effettivamente valori selezionati
            mapping[categoria] = valori    
    
    # ========================================
    # SEZIONE 9: VALUTAZIONE PUPILLE
    # ========================================
    # Valutazione neurologica delle pupille: reattività e dimensioni
    pupille_data = dati_json.get('pupille', {})
    
    # Reattività pupillare (reagenti o no alla luce)
    if pupille_data.get('reagenti', False):
        mapping['pupille_reagenti'] = 'si'
    else:
        mapping['pupille_reagenti'] = 'no'
    
    # Diametro pupilla destra (piccola, media, grande)
    dx_val = str(pupille_data.get('dx') or '').lower()
    if dx_val in ['piccola', 'media', 'grande']:
        mapping['pupilla_dx'] = dx_val
    
    # Diametro pupilla sinistra (piccola, media, grande)
    sx_val = str(pupille_data.get('sx') or '').lower()
    if sx_val in ['piccola', 'media', 'grande']:
        mapping['pupilla_sx'] = sx_val

    # ========================================
    # SEZIONE 10: LESIONI ANATOMICHE
    # ========================================
    # Sistema di codifica lesioni per parti anatomiche con validazione rigorosa
    lesioni_data = dati_json.get('lesioni', [])
    
    # Costanti di validazione - parti anatomiche standard ospedaliere
    LESIONI_PARTI = [
        "Testa", "Collo", "Braccio Sx", "Braccio Dx", "Avambraccio Sx", "Avambraccio Dx",
        "Mano Sx", "Mano Dx", "Torace", "Addome", "Schiena", "Pelvi", "Coscia Sx",
        "Coscia Dx", "Gamba Sx", "Gamba Dx", "Piede Sx", "Piede Dx", "Caviglia Sx", "Caviglia Dx"
    ]
    
    # Codici tipo lesione standard (numerico 1-9, alfabetico A-C)
    LESIONI_TIPI = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C"]
    
    # Mappatura nomi JSON -> nomi campi HTML template
    mappatura_parti_lesioni = {
        'Testa': 'lesioni_testa',
        'Collo': 'lesioni_collo', 
        'Braccio Sx': 'lesioni_braccio_sx',
        'Braccio Dx': 'lesioni_braccio_dx',
        'Avambraccio Sx': 'lesioni_avambraccio_sx',
        'Avambraccio Dx': 'lesioni_avambraccio_dx',
        'Mano Sx': 'lesioni_mano_sx',
        'Mano Dx': 'lesioni_mano_dx',
        'Torace': 'lesioni_torace',
        'Addome': 'lesioni_addome',
        'Schiena': 'lesioni_schiena',
        'Pelvi': 'lesioni_pelvi',
        'Coscia Sx': 'lesioni_coscia_sx',
        'Coscia Dx': 'lesioni_coscia_dx',
        'Gamba Sx': 'lesioni_gamba_sx',
        'Gamba Dx': 'lesioni_gamba_dx',
        'Piede Sx': 'lesioni_piede_sx',
        'Piede Dx': 'lesioni_piede_dx',
        'Caviglia Sx': 'lesioni_caviglia_sx',
        'Caviglia Dx': 'lesioni_caviglia_dx'
    }
    
    # Processa ogni lesione con validazione rigorosa
    for lesione in lesioni_data:
        parte = str(lesione.get('parte') or '').strip()
        tipo = str(lesione.get('tipo') or '').strip().upper()
        
        # Validazione parte anatomica (case insensitive)
        parte_valida = None
        for parte_standard in LESIONI_PARTI:
            if parte_standard.lower() == parte.lower():
                parte_valida = parte_standard
                break
        
        # Validazione tipo lesione (case insensitive)
        tipo_valido = None
        for tipo_standard in LESIONI_TIPI:
            if tipo_standard.upper() == tipo.upper():
                tipo_valido = tipo_standard.upper()
                break
        
        # Procede solo se entrambi parte e tipo sono validi
        if parte_valida and tipo_valido:
            html_parte = mappatura_parti_lesioni.get(parte_valida)
            
            if html_parte:
                # Crea lista per questa parte anatomica se non esiste
                if html_parte not in mapping:
                    mapping[html_parte] = []
                # Aggiungi tipo lesione evitando duplicati
                if tipo_valido not in mapping[html_parte]:
                    mapping[html_parte].append(tipo_valido)
                    print(f"Lesione validata e aggiunta: {parte_valida} -> {html_parte}, tipo: {tipo_valido}")
            else:
                print(f"⚠️ Parte anatomica valida ma nome HTML non trovato: {parte_valida}")
        else:
            # Messaggi di warning per dati non validi
            if not parte_valida:
                print(f"⚠️ Parte anatomica non valida ignorata: '{parte}' (valori accettati: {LESIONI_PARTI})")
            if not tipo_valido:
                print(f"⚠️ Tipo lesione non valido ignorato: '{tipo}' (valori accettati: {LESIONI_TIPI})")

    # ========================================
    # SEZIONE 11: TRASPORTO NON EFFETTUATO
    # ========================================
    # Gestisce i casi in cui il paziente non viene trasportato in ospedale
    trasporto_data = dati_json.get('trasporto_non_effettuato', {})
    
    # Causa del mancato trasporto con validazione contro valori template
    causa = str(trasporto_data.get('causa') or '').strip()
    if causa:
        # Valori validi secondo il template HTML
        cause_valide = ["altra_ambulanza", "elisoccorso", "non_necessita",
                       "trattato_posto", "sospeso_centrale", "non_reperito", "scherzo"]
        
        # Ricerca case-insensitive della causa
        causa_mappata = None
        for causa_valida in cause_valide:
            if causa.lower() == causa_valida.lower():
                causa_mappata = causa_valida
                break
        
        if causa_mappata:
            mapping['trasporto_non_effettuato'] = causa_mappata
    
    # ----------------------------------------
    # SOTTOSEZIONE: DECESSO
    # ----------------------------------------
    # Gestione decesso del paziente durante l'intervento
    decesso_data = trasporto_data.get('decesso', {})
    decesso_selezionato = decesso_data.get('selezionato', '')
    
    # Converte valori booleani e stringhe in checkbox value
    if decesso_selezionato is True or str(decesso_selezionato).lower() == 'true':
        mapping['decesso'] = 'si'
    
    # Dati aggiuntivi solo se presente decesso
    ora_decesso = decesso_data.get('ora_decesso', '').strip()
    if ora_decesso:
        mapping['ora_decesso'] = ora_decesso
        
    firma_medico = decesso_data.get('firma_medico', '').strip()
    if firma_medico:
        mapping['firma_medico'] = firma_medico
    
    # ----------------------------------------
    # SOTTOSEZIONE: RIFIUTO TRASPORTO
    # ----------------------------------------
    # Gestione rifiuto del trasporto da parte del paziente
    rifiuto_data = trasporto_data.get('rifiuto', {})
    rifiuto_selezionato = rifiuto_data.get('selezionato', '')
    
    # Logica analoga al decesso
    if rifiuto_selezionato is True or str(rifiuto_selezionato).lower() == 'true':
        mapping['rifiuto'] = 'si'
    
    # Firma del paziente che rifiuta
    firma_interessato = rifiuto_data.get('firma_interessato', '').strip()
    if firma_interessato:
        mapping['firma_interessato'] = firma_interessato

    # ========================================
    # SEZIONE 12: INFUSIONI E FARMACI
    # ========================================
    # Campo di testo libero per farmaci e infusioni somministrate
    mapping['infusioni_farmaci'] = provvedimenti_data.get('infusioni_farmaci', '')

    # Debug: mostra la mappatura completa generata
    print("Mappatura JSON->HTML generata:", mapping)
    return mapping

def compila_scheda_da_json(dati_json, template_html):
    """
    Compila il template HTML con i dati del paziente utilizzando BeautifulSoup.
    
    Questa funzione prende un template HTML e i dati JSON del paziente,
    crea la mappatura dei campi e modifica il DOM HTML per inserire
    i valori nei rispettivi campi form.
    
    Gestisce diversi tipi di elementi HTML:
    - Input text: inserisce il valore nell'attributo 'value'
    - Checkbox: aggiunge attributo 'checked' se il valore corrisponde
    - Textarea: inserisce il contenuto come testo interno
    - Select: marca l'option corrispondente come 'selected'
    
    Args:
        dati_json (dict): Dizionario con i dati strutturati del paziente
        template_html (str): Contenuto del template HTML come stringa

    Returns:
        str: HTML compilato con tutti i campi popolati dai dati del paziente
        
    Note:
        - Utilizza BeautifulSoup per la manipolazione DOM sicura
        - Include debug print per tracciare il processo di compilazione
        - Gestisce checkbox multipli e singoli con logiche diverse
        - Supporta campi personalizzati e valori numerici
    """
    # Inizializza parser BeautifulSoup per manipolazione DOM
    soup = BeautifulSoup(template_html, 'html.parser')
    
    # Ottieni la mappatura completa campo_html -> valore
    mapping = mappa_campi_json_a_html(dati_json)
    
    # ========================================
    # CICLO PRINCIPALE: COMPILA TUTTI I CAMPI
    # ========================================
    # Itera su ogni campo mappato e lo compila nel template HTML
    for campo_name, valore in mapping.items():
        
        # ----------------------------------------
        # GRUPPO 1: CHECKBOX MULTIPLI SPECIALI
        # ----------------------------------------
        # Gestisce campi con più checkbox che condividono lo stesso 'name'
        # ma hanno 'value' diversi (es. codice_uscita, codice_rientro)
        
        if campo_name in ['codice_uscita', 'codice_rientro']:
            elementi = soup.find_all(attrs={"name": campo_name})
            print(f"🔍 Trovati {len(elementi)} checkbox per {campo_name}")
            for elemento in elementi:
                if elemento.name == 'input' and elemento.get('type') == 'checkbox':
                    if elemento.get('value') == str(valore):
                        elemento['checked'] = 'checked'
                        print(f"✅ Checkbox selezionato: {campo_name} = {valore}")
        
        # ----------------------------------------
        # GRUPPO 2: CHECKBOX SINGOLI FONTE DATI
        # ----------------------------------------
        # Gestisce selezione esclusiva della fonte dati (paziente, parente, documento)
        
        elif campo_name in ['fonte_dati_paziente', 'fonte_dati_parente', 'fonte_dati_documento']:
            elemento = soup.find(attrs={"name": campo_name})
            if elemento and elemento.name == 'input' and elemento.get('type') == 'checkbox':
                if elemento.get('value') == str(valore):
                    elemento['checked'] = 'checked'
                    print(f"✅ Fonte dati selezionata: {campo_name} = {valore}")
        
        # ----------------------------------------
        # GRUPPO 3: AUTORITÀ PRESENTI (LISTA)
        # ----------------------------------------
        # Gestisce selezione multipla delle autorità presenti sul posto
        
        elif campo_name == 'autorita_presenti':
            elementi = soup.find_all(attrs={"name": campo_name})
            print(f"🔍 Trovati {len(elementi)} checkbox autorità")
            print(f"📋 Autorità da selezionare: {valore}")
            for elemento in elementi:
                if elemento.name == 'input' and elemento.get('type') == 'checkbox':
                    # valore è una lista di autorità selezionate
                    if elemento.get('value') in valore:
                        elemento['checked'] = 'checked'
                        print(f"✅ Autorità selezionata: {elemento.get('value')}")
        
        # ----------------------------------------
        # GRUPPO 4: RILEVAZIONI PARAMETRI VITALI
        # ----------------------------------------
        # Gestisce checkbox per coscienza, cute, respiro nei tempi T1,T2,T3
        
        elif campo_name.startswith(('coscienza_', 'cute_', 'respiro_')):
            elementi = soup.find_all(attrs={"name": campo_name})
            print(f"🔍 Trovati {len(elementi)} checkbox per rilevazione {campo_name}")
            for elemento in elementi:
                if elemento.name == 'input' and elemento.get('type') == 'checkbox':
                    if elemento.get('value') == str(valore):
                        elemento['checked'] = 'checked'
                        print(f"✅ Rilevazione selezionata: {campo_name} = {valore}")
        
        # ----------------------------------------
        # GRUPPO 5: GLASGOW COMA SCALE (GCS)
        # ----------------------------------------
        # Gestisce punteggi GCS per apertura occhi, risposta verbale, motoria
        
        elif campo_name.startswith(('gcs_apertura_occhi_', 'gcs_risposta_verbale_', 'gcs_risposta_motoria_')):
            elementi = soup.find_all(attrs={"name": campo_name})
            print(f"🔍 Trovati {len(elementi)} checkbox GCS per {campo_name}")
            for elemento in elementi:
                if elemento.name == 'input' and elemento.get('type') == 'checkbox':
                    if elemento.get('value') == str(valore):
                        elemento['checked'] = 'checked'
                        print(f"✅ GCS selezionato: {campo_name} = {valore}")
        
        # ----------------------------------------
        # GRUPPO 6: VALUTAZIONE PUPILLE
        # ----------------------------------------
        # Gestisce diametro pupille (dx/sx) e reattività
        
        elif campo_name in ['pupilla_dx', 'pupilla_sx', 'pupille_reagenti']:
            elementi = soup.find_all(attrs={"name": campo_name})
            print(f"🔍 Trovati {len(elementi)} checkbox pupille per {campo_name}")
            for elemento in elementi:
                if elemento.name == 'input' and elemento.get('type') == 'checkbox':
                    if elemento.get('value') == str(valore):
                        elemento['checked'] = 'checked'
                        print(f"✅ Pupille selezionate: {campo_name} = {valore}")
        
        # ----------------------------------------
        # GRUPPO 7: LESIONI ANATOMICHE (LISTE)
        # ----------------------------------------
        # Gestisce selezione multipla dei tipi di lesione per ogni parte anatomica
        
        elif campo_name.startswith('lesioni_'):
            if isinstance(valore, list):  # valore è una lista di tipi lesione
                elementi = soup.find_all(attrs={"name": campo_name})
                print(f"🔍 Trovati {len(elementi)} checkbox per lesioni {campo_name}")
                print(f"📋 Tipi lesione da selezionare: {valore}")
                for elemento in elementi:
                    if elemento.name == 'input' and elemento.get('type') == 'checkbox':
                        if elemento.get('value') in valore:
                            elemento['checked'] = 'checked'
                            print(f"✅ Lesione selezionata: {campo_name} = {elemento.get('value')}")

        # ----------------------------------------
        # GRUPPO 8: PROVVEDIMENTI TERAPEUTICI (LISTE)
        # ----------------------------------------
        # Gestisce selezione multipla dei provvedimenti per categoria
        
        elif campo_name in ['respiro', 'circolo', 'immobilizzazione', 'altro']:
            if isinstance(valore, list):  # valore è una lista di provvedimenti
                elementi = soup.find_all(attrs={"name": campo_name})
                print(f"🔍 Trovati {len(elementi)} checkbox per provvedimenti {campo_name}")
                print(f"📋 Provvedimenti da selezionare: {valore}")
                for elemento in elementi:
                    if elemento.name == 'input' and elemento.get('type') == 'checkbox':
                        if elemento.get('value') in valore:
                            elemento['checked'] = 'checked'
                            print(f"✅ Provvedimento selezionato: {campo_name} = {elemento.get('value')}")
        
        # ----------------------------------------
        # GRUPPO 9: VALORI NUMERICI PROVVEDIMENTI
        # ----------------------------------------
        # Gestisce campi di testo con valori numerici associati ai provvedimenti
        
        elif campo_name in ['ossigeno_l_min_value', 'intubazione_num_value', 'mce_min_value', 
                           'dae_num_shock_value', 'custom_1_value', 'custom_2_value']:
            elemento = soup.find(attrs={"name": campo_name})
            print(f"🔍 Campo valore provvedimento trovato: {campo_name}")
            if elemento and elemento.name == 'input' and elemento.get('type') == 'text':
                elemento['value'] = str(valore)
                print(f"✅ Valore provvedimento compilato: {campo_name} = {valore}")

        # ----------------------------------------
        # GRUPPO 10: TOTALE GCS (CAMPO TESTO)
        # ----------------------------------------
        # Gestisce il punteggio totale della Glasgow Coma Scale
        
        elif campo_name.startswith('gcs_totale_'):
            elemento = soup.find(attrs={"name": campo_name})
            print(f"🔍 Campo totale GCS trovato: {campo_name}")
            if elemento and elemento.name == 'input' and elemento.get('type') == 'text':
                elemento['value'] = str(valore)
                print(f"✅ Totale GCS compilato: {campo_name} = {valore}")
        
        # ----------------------------------------
        # GRUPPO 11: TRASPORTO NON EFFETTUATO
        # ----------------------------------------
        # Gestisce le cause del mancato trasporto
        
        elif campo_name == 'trasporto_non_effettuato':
            elementi = soup.find_all(attrs={"name": campo_name})
            print(f"🔍 Trovati {len(elementi)} checkbox trasporto")
            for elemento in elementi:
                if elemento.name == 'input' and elemento.get('type') == 'checkbox':
                    if elemento.get('value') == str(valore):
                        elemento['checked'] = 'checked'
                        print(f"✅ Trasporto non effettuato: {campo_name} = {valore}")
        
        # ----------------------------------------
        # GRUPPO 12: DECESSO E RIFIUTO
        # ----------------------------------------
        # Gestisce checkbox per decesso e rifiuto trasporto
        
        elif campo_name in ['decesso', 'rifiuto']:
            elemento = soup.find(attrs={"name": campo_name})
            if elemento and elemento.name == 'input' and elemento.get('type') == 'checkbox':
                if elemento.get('value') == str(valore):
                    elemento['checked'] = 'checked'
                    print(f"✅ Checkbox selezionato: {campo_name} = {valore}")
        
        # ----------------------------------------
        # GRUPPO 13: CAMPI TESTO SPECIALI
        # ----------------------------------------
        # Gestisce campi di testo per ora decesso, firme, etc.
        
        elif campo_name in ['ora_decesso', 'firma_medico', 'firma_interessato']:
            elemento = soup.find(attrs={"name": campo_name})
            print(f"🔍 Campo testo speciale trovato: {campo_name}")
            if elemento:
                if elemento.name == 'input':
                    elemento['value'] = str(valore)
                elif elemento.name == 'textarea':
                    elemento.string = str(valore)
                print(f"✅ Campo compilato: {campo_name} = {valore}")
        
        # ----------------------------------------
        # GRUPPO 14: GESTIONE GENERALE
        # ----------------------------------------
        # Gestisce tutti gli altri tipi di campo con logica generica
        
        else:
            elemento = soup.find(attrs={"name": campo_name})
            print(f"🔍 Campo generico trovato: {campo_name}")
            if elemento:
                if elemento.name == 'input':
                    if elemento.get('type') in ['checkbox', 'radio']:
                        # Checkbox/radio: seleziona se valore corrisponde
                        if elemento.get('value') == str(valore):
                            elemento['checked'] = 'checked'
                    else:
                        # Input di testo: imposta valore
                        elemento['value'] = str(valore)
                elif elemento.name == 'textarea':
                    # Textarea: imposta contenuto
                    elemento.string = str(valore)
                elif elemento.name == 'select':
                    # Select: marca l'option corrispondente come selected
                    for option in elemento.find_all('option'):
                        if option.get('value') == str(valore) or option.string == str(valore):
                            option['selected'] = 'selected'
                            break
                print(f"✅ Campo generico compilato: {campo_name} = {valore}")

    # Restituisce l'HTML compilato come stringa
    return str(soup)

def genera_scheda_da_json(dati_json, output_html=None, template_path=template_path):
    """
    Funzione principale che orchestra l'intero processo di generazione della scheda paziente.
    
    Questa è la funzione di alto livello che coordina tutti i passaggi:
    1. Carica il template HTML dal file system
    2. Genera un nome file automatico se non specificato
    3. Compila il template con i dati del paziente
    4. Salva il file HTML risultante su disco
    5. Fornisce feedback sull'operazione

    Args:
        dati_json (dict): Dizionario completo con tutti i dati del paziente
                         strutturati secondo lo schema JSON predefinito
        output_html (str, optional): Percorso completo del file HTML di output.
                                   Se None, viene generato automaticamente dal nome paziente
                                   o da un timestamp se il nome non è disponibile
        template_path (str): Percorso del file template HTML da utilizzare.
                           Default: "scheda_paziente_cartacea.html"

    Returns:
        dict: Dizionario con risultato dell'operazione:
              {
                  "html": "percorso/file/generato.html" o None se errore,
                  "success": True/False,
                  "error": "messaggio errore" (solo se success=False)
              }
              
    Example:
        >>> dati_paziente = {...}  # Dati JSON strutturati
        >>> risultato = genera_scheda_da_json(dati_paziente, "mario_rossi.html")
        >>> if risultato["success"]:
        ...     print(f"Scheda generata: {risultato['html']}")
        ... else:
        ...     print(f"Errore: {risultato['error']}")
    """
    
    # ========================================
    # FASE 1: CARICAMENTO TEMPLATE
    # ========================================
    template_html = carica_template_html(template_path)
    if not template_html:
        return {
            "html": None, 
            "success": False, 
            "error": f"Template HTML non trovato: {template_path}"
        }
    
    # ========================================
    # FASE 2: GENERAZIONE NOME FILE OUTPUT
    # ========================================
    if not output_html:
        # Prova a generare nome file dal cognome/nome paziente
        cognome = dati_json.get('dati_paziente', {}).get('cognome_nome', '').split()[0] if dati_json.get('dati_paziente', {}).get('cognome_nome') else ''
        nome = dati_json.get('dati_paziente', {}).get('cognome_nome', '').split()[1] if len(dati_json.get('dati_paziente', {}).get('cognome_nome', '').split()) > 1 else ''
        
        if cognome and nome:
            # Crea nome file da cognome e nome (sanitizzato)
            nome_paziente = f"{cognome}_{nome}".replace(' ', '_').replace('-', '_').lower()
            # Rimuovi caratteri non validi per nome file
            nome_paziente = ''.join(c for c in nome_paziente if c.isalnum() or c == '_')
            output_html = f"scheda_{nome_paziente}.html"
        else:
            # Fallback: usa timestamp corrente
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_html = f"scheda_paziente_{timestamp}.html"
        
        print(f"📝 Nome file auto-generato: {output_html}")
    
    # ========================================
    # FASE 3: COMPILAZIONE TEMPLATE
    # ========================================
    try:
        html_compilato = compila_scheda_da_json(dati_json, template_html)
        print("✅ Template compilato con successo")
    except Exception as e:
        return {
            "html": None,
            "success": False,
            "error": f"Errore durante la compilazione del template: {str(e)}"
        }
    
    # ========================================
    # FASE 4: SALVATAGGIO FILE
    # ========================================
    try:
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_compilato)
        print(f"✅ Scheda paziente generata con successo: {output_html}")
        return {
            "html": os.path.abspath(output_html),  # Restituisce percorso assoluto
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
    
    Questa funzione prende un file HTML e lo converte in un documento PDF
    mantenendo la formattazione, i CSS e gli elementi grafici del file originale.
    Utilizza il motore di rendering Chromium per garantire una conversione
    fedele e di alta qualità.

    Args:
        html_path (str): Percorso assoluto del file HTML da convertire in PDF.
                        Deve essere un file esistente e accessibile.
        output_pdf (str): Percorso dove salvare il file PDF generato.
                         Include nome file e estensione .pdf

    Returns:
        None

    Raises:
        FileNotFoundError: Se il file HTML specificato non esiste
        Exception: Per errori durante la conversione o il salvataggio PDF

    Example:
        >>> stampa_html_in_pdf("/path/to/scheda_paziente.html", "/path/to/output.pdf")
        >>> # Genera un PDF della scheda paziente
        
    Note:
        - Richiede che Playwright sia installato con i browser necessari
        - Il formato è fisso su A4 con background stampato
        - Il browser viene lanciato in modalità headless per efficienza
    """
    try:
        with sync_playwright() as p:
            # Lancia browser Chromium in modalità headless
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # Carica il file HTML utilizzando protocollo file://
            page.goto(f'file://{html_path}')
            
            # Genera PDF con impostazioni ottimizzate per schede mediche
            page.pdf(
                path=output_pdf, 
                format="A4", 
                print_background=True,  # Include sfondi e colori CSS
                margin={  # Margini ottimizzati per documenti medici
                    "top": "20px",
                    "bottom": "20px", 
                    "left": "20px",
                    "right": "20px"
                }
            )
            
            # Chiude il browser per liberare risorse
            browser.close()
            
        print(f"✅ PDF generato con successo: {output_pdf}")
        
    except Exception as e:
        print(f"❌ Errore durante la conversione HTML->PDF: {e}")
        raise


def genera_scheda_pdf_da_json(dati_json, output_pdf=None, template_path=template_path, mantieni_html=False):
    """
    Funzione completa che genera una scheda paziente PDF partendo da dati JSON.
    
    Questa funzione orchestra l'intero workflow:
    1. Genera il file HTML dalla struttura JSON del paziente
    2. Converte automaticamente l'HTML in PDF usando Playwright
    3. Opzionalmente rimuove il file HTML temporaneo
    
    È la funzione più conveniente per ottenere direttamente un PDF
    senza dover gestire manualmente i passaggi intermedi.

    Args:
        dati_json (dict): Dizionario completo con tutti i dati del paziente
                         strutturati secondo lo schema JSON predefinito
        output_pdf (str, optional): Percorso completo del file PDF di output.
                                   Se None, viene generato automaticamente dal nome paziente
                                   o da un timestamp se il nome non è disponibile
        template_path (str): Percorso del file template HTML da utilizzare.
                           Default: "scheda_paziente_cartacea.html"
        mantieni_html (bool): Se True, mantiene il file HTML temporaneo dopo la conversione.
                             Se False, rimuove automaticamente il file HTML.
                             Default: False

    Returns:
        dict: Dizionario con risultato dell'operazione:
              {
                  "pdf": "percorso/file/generato.pdf" o None se errore,
                  "html": "percorso/file/temporaneo.html" (se mantieni_html=True),
                  "success": True/False,
                  "error": "messaggio errore" (solo se success=False)
              }
              
    Example:
        >>> dati_paziente = {...}  # Dati JSON strutturati
        >>> risultato = genera_scheda_pdf_da_json(dati_paziente)
        >>> if risultato["success"]:
        ...     print(f"PDF generato: {risultato['pdf']}")
        ... else:
        ...     print(f"Errore: {risultato['error']}")
        
        >>> # Con nome file personalizzato e mantenimento HTML
        >>> risultato = genera_scheda_pdf_da_json(
        ...     dati_paziente, 
        ...     output_pdf="mario_rossi.pdf",
        ...     mantieni_html=True
        ... )
        
    Note:
        - Richiede che Playwright sia installato con Chromium
        - Il file HTML temporaneo viene creato nella stessa directory del PDF
        - Se mantieni_html=False, solo il PDF rimane al termine dell'operazione
    """
    
    # ========================================
    # FASE 1: GENERAZIONE NOME FILE PDF
    # ========================================
    if not output_pdf:
        # Genera sempre timestamp per evitare conflitti
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prova a generare nome file dal cognome/nome paziente
        cognome = dati_json.get('dati_paziente', {}).get('cognome_nome', '').split()[0] if dati_json.get('dati_paziente', {}).get('cognome_nome') else ''
        nome = dati_json.get('dati_paziente', {}).get('cognome_nome', '').split()[1] if len(dati_json.get('dati_paziente', {}).get('cognome_nome', '').split()) > 1 else ''
        
        if cognome and nome:
            # Crea nome file da cognome e nome (sanitizzato) + timestamp
            nome_paziente = f"{cognome}_{nome}".replace(' ', '_').replace('-', '_').lower()
            # Rimuovi caratteri non validi per nome file
            nome_paziente = ''.join(c for c in nome_paziente if c.isalnum() or c == '_')
            output_pdf = f"scheda_{nome_paziente}_{timestamp}.pdf"
        else:
            # Fallback: usa solo timestamp
            output_pdf = f"scheda_paziente_{timestamp}.pdf"
        
        print(f"📄 Nome file PDF auto-generato: {output_pdf}")
    
    # ========================================
    # FASE 2: GENERAZIONE HTML TEMPORANEO
    # ========================================
    # Crea nome file HTML temporaneo basato sul nome PDF
    base_name = os.path.splitext(output_pdf)[0]  # Rimuove estensione .pdf
    html_temporaneo = f"{base_name}_temp.html"
    
    print(f"🔄 Generazione HTML temporaneo: {html_temporaneo}")
    
    # Genera il file HTML usando la funzione esistente
    risultato_html = genera_scheda_da_json(
        dati_json, 
        output_html=html_temporaneo, 
        template_path=template_path
    )
    
    # Verifica che la generazione HTML sia riuscita
    if not risultato_html["success"]:
        return {
            "pdf": None,
            "html": None,
            "success": False,
            "error": f"Errore nella generazione HTML: {risultato_html['error']}"
        }

    html_path = risultato_html["html"]
    print(f"✅ HTML generato con successo: {html_path}")
    
    # ========================================
    # FASE 3: CONVERSIONE HTML → PDF
    # ========================================
    try:
        print(f"🔄 Conversione HTML → PDF: {output_pdf}")
        
        # Converte HTML in PDF usando la funzione esistente
        stampa_html_in_pdf(html_path, output_pdf)
        
        print(f"✅ PDF generato con successo: {output_pdf}")
        
    except Exception as e:
        # Stampa l'errore completo (traceback) per capire cosa è successo in Playwright
        error_details = traceback.format_exc()
        print("!!! ERRORE CRITICO DURANTE LA CONVERSIONE PDF (stampa_html_in_pdf) !!!")
        print(error_details)
        # In caso di errore, cleanup del file HTML se richiesto
        if not mantieni_html and os.path.exists(html_path):
            try:
                os.remove(html_path)
                print(f"🧹 File HTML temporaneo rimosso dopo errore")
            except:
                pass
        
        return {
            "pdf": None,
            "html": html_path if mantieni_html else None,
            "success": False,
            "error": f"Errore nella conversione PDF: {str(e)}"
        }
    
    # ========================================
    # FASE 4: CLEANUP OPZIONALE
    # ========================================
    risultato_finale = {
        "pdf": os.path.abspath(output_pdf),
        "success": True
    }
    
    if mantieni_html:
        # Mantieni il file HTML e restituisci il percorso
        risultato_finale["html"] = os.path.abspath(html_path)
        print(f"📄 File HTML mantenuto: {html_path}")
    else:
        # Rimozione del file HTML temporaneo
        try:
            os.remove(html_path)
            print(f"🧹 File HTML temporaneo rimosso: {html_path}")
            risultato_finale["html"] = None
        except Exception as e:
            # Non è un errore critico se non riusciamo a rimuovere il file temporaneo
            print(f"⚠️ Impossibile rimuovere file HTML temporaneo: {e}")
            risultato_finale["html"] = os.path.abspath(html_path)
    
    print(f"🎉 PROCESSO COMPLETATO CON SUCCESSO!")
    print(f"📄 PDF finale: {risultato_finale['pdf']}")
    
    return risultato_finale

def crea_report_medico(dati_report, filename, template_path=template_path):
    """
    Funzione "ponte" che riceve i dati dall'applicazione Streamlit e
    avvia il processo di generazione del PDF.
    
    Questa funzione è progettata per essere compatibile con le chiamate
    esistenti in 'record_and_trascribe.py' e 'filter_data.py'.

    Args:
        dati_report (dict): Dizionario contenente i dati del report, 
                           tipicamente con una chiave 'data' che contiene 
                           il record completo del paziente.
        filename (str): Percorso completo dove salvare il file PDF di output.
        template_path (str): Percorso del template HTML.
    
    Returns:
        dict: Il risultato dell'operazione di generazione del PDF.
    """
    #print(f"📄 Avvio generazione report per: {filename}")
    # Estraiamo questo dizionario per passarlo alla funzione di generazione.
    dati_paziente_json = dati_report.get('data')

    if not dati_paziente_json:
        print("❌ Errore: la chiave 'data' non è stata trovata nel dizionario del report.")
        return {
            "pdf": None,
            "success": False,
            "error": "Dati del paziente non trovati nel dizionario di input (chiave 'data' mancante)."
        }
    
    # Chiama la funzione principale di generazione PDF con i dati corretti.
    return genera_scheda_pdf_da_json(
        dati_json=dati_paziente_json,
        output_pdf=filename,
        template_path=template_path,
        mantieni_html=False  # Di solito non serve mantenere l'HTML intermedio
    )