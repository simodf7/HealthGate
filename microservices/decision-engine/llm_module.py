import os
import json
import re
import logging
import copy
from typing import Dict, Tuple
import requests
from pprint import pprint

# disattivato perché il microservizio non ha il modulo database
# from database.constants import (
#     Sesso, Coscienza, Cute, Respiro, PupilleDiametro, CodiceUscita, CodiceRientro,
#     LesioniParti, LesioniTipi, LESIONI_PARTI_VALUES, LESIONI_TIPI_VALUES
# )


logging.basicConfig(level=logging.INFO)

# === CLIENT SETUP ===

def create_client(api_key: str) -> str:
    """Crea un client remoto verso l'API di Google AI Studio."""
    if not api_key:
        raise EnvironmentError(
            "Impossibile inizializzare il client: API key mancante. "
            "Imposta la variabile d'ambiente GEMINI_API_KEY oppure passa api_key esplicitamente."
        )

    logging.info("Client inizializzato correttamente con API key fornita.")
    return api_key


# === FUNZIONI DI VALIDAZIONE CON COSTANTI ===

def validate_and_normalize_values(json_data: Dict) -> Dict:
    """Valida e normalizza i valori usando le costanti definite."""
    
    corrected_data = copy.deepcopy(json_data)
    
    # Validazione e correzione sesso
    if 'dati_paziente' in corrected_data and 'sesso' in corrected_data['dati_paziente']:
        sesso_raw = corrected_data['dati_paziente']['sesso'].lower() if corrected_data['dati_paziente']['sesso'] else ""
        if sesso_raw in ['maschio', 'uomo', 'm', 'male']:
            corrected_data['dati_paziente']['sesso'] = Sesso.MASCHIO.value
        elif sesso_raw in ['femmina', 'donna', 'f', 'female']:
            corrected_data['dati_paziente']['sesso'] = Sesso.FEMMINA.value
    
    # Validazione e correzione coscienza nelle rilevazioni
    if 'rilevazioni' in corrected_data:
        for rilevazione in corrected_data['rilevazioni']:
            if 'coscienza' in rilevazione and rilevazione['coscienza']:
                coscienza_raw = rilevazione['coscienza'].lower()
                if any(word in coscienza_raw for word in ['incosciente', 'unresponsive', 'non responsivo']):
                    rilevazione['coscienza'] = Coscienza.INCOSCIENTE.value
                elif any(word in coscienza_raw for word in ['sveglio', 'alert', 'cosciente', 'vigile']):
                    rilevazione['coscienza'] = Coscienza.SVEGLIO.value
                elif any(word in coscienza_raw for word in ['voce', 'voice', 'verbale']):
                    rilevazione['coscienza'] = Coscienza.VOCE.value
                elif any(word in coscienza_raw for word in ['dolore', 'pain', 'doloroso']):
                    rilevazione['coscienza'] = Coscienza.DOLORE.value
            
            # Validazione cute
            if 'cute' in rilevazione and rilevazione['cute']:
                cute_raw = rilevazione['cute'].lower()
                if 'pallida' in cute_raw or 'pallid' in cute_raw:
                    rilevazione['cute'] = Cute.PALLIDA.value
                elif 'cianotica' in cute_raw or 'cianotic' in cute_raw or 'blu' in cute_raw:
                    rilevazione['cute'] = Cute.CIANOTICA.value
                elif 'sudata' in cute_raw or 'sudorazione' in cute_raw or 'umida' in cute_raw:
                    rilevazione['cute'] = Cute.SUDATA.value
                elif 'normale' in cute_raw:
                    rilevazione['cute'] = Cute.NORMALE.value
            
            # Validazione respiro
            if 'respiro' in rilevazione and rilevazione['respiro']:
                respiro_raw = rilevazione['respiro'].lower()
                if 'assente' in respiro_raw or 'apnea' in respiro_raw:
                    rilevazione['respiro'] = Respiro.ASSENTE.value
                elif 'tachipnoic' in respiro_raw or 'rapido' in respiro_raw or 'veloce' in respiro_raw:
                    rilevazione['respiro'] = Respiro.TACHIPNOICO.value
                elif 'bradipnoic' in respiro_raw or 'lento' in respiro_raw:
                    rilevazione['respiro'] = Respiro.BRADIPNOICO.value
                elif 'normale' in respiro_raw or 'regular' in respiro_raw:
                    rilevazione['respiro'] = Respiro.NORMALE.value
    
    # Validazione pupille
    if 'pupille' in corrected_data:
        for campo in ['dx', 'sx']:
            if campo in corrected_data['pupille'] and corrected_data['pupille'][campo]:
                pupilla_raw = corrected_data['pupille'][campo].lower()
                if 'piccola' in pupilla_raw or 'small' in pupilla_raw or 'miotic' in pupilla_raw:
                    corrected_data['pupille'][campo] = PupilleDiametro.PICCOLA.value
                elif 'grande' in pupilla_raw or 'large' in pupilla_raw or 'midriatic' in pupilla_raw:
                    corrected_data['pupille'][campo] = PupilleDiametro.GRANDE.value
                elif 'media' in pupilla_raw or 'medium' in pupilla_raw or 'normale' in pupilla_raw:
                    corrected_data['pupille'][campo] = PupilleDiametro.MEDIA.value
      # Validazione codici di uscita e rientro
    if 'chiamata' in corrected_data:
        # Codice uscita
        if 'codice_uscita' in corrected_data['chiamata'] and corrected_data['chiamata']['codice_uscita']:
            codice_raw = corrected_data['chiamata']['codice_uscita'].upper()
            if codice_raw in ['B', 'BIANCO', 'WHITE']:
                corrected_data['chiamata']['codice_uscita'] = CodiceUscita.BIANCO.value
            elif codice_raw in ['V', 'VERDE', 'GREEN']:
                corrected_data['chiamata']['codice_uscita'] = CodiceUscita.VERDE.value
            elif codice_raw in ['G', 'GIALLO', 'YELLOW']:
                corrected_data['chiamata']['codice_uscita'] = CodiceUscita.GIALLO.value
            elif codice_raw in ['R', 'ROSSO', 'RED']:
                corrected_data['chiamata']['codice_uscita'] = CodiceUscita.ROSSO.value
        
        # Codice rientro
        if 'codice_rientro' in corrected_data['chiamata'] and corrected_data['chiamata']['codice_rientro']:
            rientro_raw = corrected_data['chiamata']['codice_rientro']
            if rientro_raw in ['0', '1', '2', '3', '4']:
                # È già nel formato corretto
                pass
            elif 'non necessario' in rientro_raw.lower():
                corrected_data['chiamata']['codice_rientro'] = CodiceRientro.NON_NECESSARIO.value
            elif 'non trasportato' in rientro_raw.lower():
                corrected_data['chiamata']['codice_rientro'] = CodiceRientro.NON_TRASPORTATO.value
            elif 'non urgente' in rientro_raw.lower():
                corrected_data['chiamata']['codice_rientro'] = CodiceRientro.NON_URGENTE.value
            elif 'urgente' in rientro_raw.lower():
                corrected_data['chiamata']['codice_rientro'] = CodiceRientro.URGENTE.value
            elif 'critico' in rientro_raw.lower():
                corrected_data['chiamata']['codice_rientro'] = CodiceRientro.CRITICO.value
    
    # Validazione lesioni
    if 'lesioni' in corrected_data and isinstance(corrected_data['lesioni'], list):
        lesioni_corrette = []
        for lesione in corrected_data['lesioni']:
            if isinstance(lesione, dict):
                lesione_corretta = lesione.copy()
                
                # Validazione parte anatomica
                if 'parte' in lesione and lesione['parte']:
                    parte_raw = lesione['parte'].strip()
                    # Cerca corrispondenza con parti anatomiche standard
                    for parte_enum in LesioniParti:
                        if (parte_raw.lower() in parte_enum.value.lower() or 
                            parte_enum.value.lower() in parte_raw.lower()):
                            lesione_corretta['parte'] = parte_enum.value
                            break
                    else:
                        # Se non trova corrispondenza esatta, mantieni l'originale
                        # ma normalizza la capitalizzazione
                        lesione_corretta['parte'] = parte_raw.title()
                
                # Validazione tipo di lesione
                if 'tipo' in lesione and lesione['tipo']:
                    tipo_raw = str(lesione['tipo']).strip().upper()
                    
                    # Mappa descrittiva per i codici
                    mapping_tipi = {
                        'AMPUTAZIONE': LesioniTipi.AMPUTAZIONE.value,
                        'DEFORMITA': LesioniTipi.DEFORMITA.value,
                        'DEFORMITÀ': LesioniTipi.DEFORMITA.value,
                        'DOLORE': LesioniTipi.DOLORE.value,
                        'EMORRAGIA': LesioniTipi.EMORRAGIA.value,
                        'FERITA PROFONDA': LesioniTipi.FERITA_PROFONDA.value,
                        'FERITA SUPERFICIALE': LesioniTipi.FERITA_SUPERFICIALE.value,
                        'TRAUMA CHIUSO': LesioniTipi.TRAUMA_CHIUSO.value,
                        'USTIONE': LesioniTipi.USTIONE.value,
                        'DEFICIT MOTORIO': LesioniTipi.DEFICIT_MOTORIO.value,
                        'SENSIBILITA ASSENTE': LesioniTipi.SENSIBILITA_ASSENTE.value,
                        'SENSIBILITÀ ASSENTE': LesioniTipi.SENSIBILITA_ASSENTE.value,
                        'FRATTURA': LesioniTipi.FRATTURA_SOSPETTA.value,
                        'FRATTURA SOSPETTA': LesioniTipi.FRATTURA_SOSPETTA.value,
                        'LUSSAZIONE': LesioniTipi.LUSSAZIONE_SOSPETTA.value,
                        'LUSSAZIONE SOSPETTA': LesioniTipi.LUSSAZIONE_SOSPETTA.value
                    }
                    
                    # Verifica se è già un codice valido
                    if tipo_raw in LESIONI_TIPI_VALUES:
                        lesione_corretta['tipo'] = tipo_raw
                    # Verifica se corrisponde a una descrizione
                    elif tipo_raw in mapping_tipi:
                        lesione_corretta['tipo'] = mapping_tipi[tipo_raw]
                    # Cerca corrispondenze parziali
                    else:
                        for desc, codice in mapping_tipi.items():
                            if desc in tipo_raw or tipo_raw in desc:
                                lesione_corretta['tipo'] = codice
                                break
                        else:
                            # Mantieni l'originale se non trova corrispondenze
                            lesione_corretta['tipo'] = tipo_raw
                
                lesioni_corrette.append(lesione_corretta)
        
        corrected_data['lesioni'] = lesioni_corrette
    
    logging.info("Validazione con costanti completata")
    return corrected_data


# === CORREZIONE ERRORI DI TRASCRIZIONE ===

def correct_transcription_errors(api_key: str, transcribed_text: str, *, temperature: float = 0.2, max_tokens: int = 1024) -> str:
    """Corregge errori di trascrizione audio tipici in contesto medico/sanitario."""
    
    correction_prompt = f"""
Sei un assistente esperto in medicina d'emergenza e trascrizioni audio.
Il seguente testo proviene dalla trascrizione automatica di un audio registrato durante un intervento di soccorso.

La trascrizione potrebbe contenere errori dovuti a:
- Rumore di fondo (sirene, radio, ambiente ospedaliero)
- Termini medici complessi pronunciati velocemente
- Nomi di farmaci o procedure mediche
- Codici e sigle sanitarie
- Nomi propri di persone e luoghi
- Orari e date pronunciati rapidamente
- Interruzioni o sovrapposizioni nel parlato

COMPITO:
Correggi SOLO gli errori evidenti di trascrizione mantenendo il significato originale.
NON aggiungere informazioni non presenti nel testo originale.
NON correggere informazioni che sembrano corrette anche se inusuali.

ESEMPI DI CORREZIONI TIPICHE:
- "spazio due" → "SpO2"
- "frequenza cardiaca bpm" → "FC bpm" 
- "pressione arteriosa" → "PA"
- "glasgow coma scale" → "GCS"
- "via venosa" → "accesso venoso"
- "collare server calle" → "collare cervicale"
- "pronto soccorso" → "PS"
- "dottor essa" → "dott.ssa"
- "codice fiscale" seguito da lettere/numeri malformati
- Date e orari con formato errato
- Nomi di farmaci comuni (paracetamolo, morfina, etc.)
- Termini anatomici (caviglia, braccio, torace, etc.)

Restituisci SOLO il testo corretto, senza commenti aggiuntivi.

Testo da correggere:
\"\"\"{transcribed_text}\"\"\"
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": correction_prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            corrected_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Rimuovi eventuali marker di citazione se presenti
            corrected_text = corrected_text.strip()
            if corrected_text.startswith('"""') and corrected_text.endswith('"""'):
                corrected_text = corrected_text[3:-3].strip()
            
            logging.info("Correzione errori di trascrizione completata")
            return corrected_text
            
        else:
            logging.warning("Errore nella correzione trascrizione: %s", response.text)
            return transcribed_text  # Ritorna il testo originale se c'è un errore
            
    except Exception as e:
        logging.warning("Errore durante la correzione trascrizione: %s", e)
        return transcribed_text  # Ritorna il testo originale se c'è un errore


# === PROMPT TEMPLATE ===

def build_prompt(text: str) -> str:
    return f"""
Sei un assistente esperto in medicina d'emergenza.
Dal testo clinico che segue, estrai i dati e restituisci un oggetto JSON valido e compatibile con MongoDB.

REGOLE IMPORTANTI:
- Sesso: usa "M" per maschio, "F" per femmina
- Coscienza: usa codici A (sveglio), V (voce), P (dolore), U (incosciente)
- Cute: usa "normale", "pallida", "cianotica", "sudata"
- Respiro: usa "normale", "tachipnoico", "bradipnoico", "assente"
- Pupille: usa "piccola", "media", "grande"
- Codici uscita: B (bianco), V (verde), G (giallo), R (rosso)
- Codici rientro: 0 (non necessario), 1 (non trasportato), 2 (non urgente), 3 (urgente), 4 (critico)
- Lesioni parti: usa "Testa", "Collo", "Braccio Sx/Dx", "Avambraccio Sx/Dx", "Mano Sx/Dx", "Torace", "Addome", "Schiena", "Pelvi", "Coscia Sx/Dx", "Gamba Sx/Dx", "Piede Sx/Dx", "Caviglia Sx/Dx"
- Lesioni tipi: usa codici 1=Amputazione, 2=Deformità, 3=Dolore, 4=Emorragia, 5=Ferita profonda, 6=Ferita superficiale, 7=Trauma chiuso, 8=Ustione, 9=Deficit motorio, A=Sensibilità assente, B=Frattura/sosp., C=Lussazione/sosp.
- ID: lascia sempre vuoto ""
- episodio_numero: sempre 1 se non specificato
- Valori vuoti: usa "" per stringhe vuote, mai null
- Array vuoti: se non ci sono lesioni, usa array vuoto []
- Boolean: usa false per valori non specificati
- Valori numerici: usa null solo per misurazioni non effettuate
- Monitor: se viene misurato SpO2/FC/PA, imposta i relativi monitor a true
- Orari: se menzionato trasporto a ospedale, calcola orari mancanti logicamente
- GCS: se fornito totale, calcola anche i sottocampi (apertura_occhi + risposta_verbale + risposta_motoria)

Restituisci SOLO l'oggetto JSON, senza altri commenti.

Esempio di output:
{{
  "codice_fiscale": "",
  "id": "",
  "episodio_numero": 1,
  "is_ricorrente": false,
  "condizioni_croniche": [],
  "chiamata": {{
    "data": "2025-06-12",
    "orari": {{
      "h_chiamata": "14:45",
      "h_partenza": "15:00",
      "h_arrivo_sul_posto": "15:00",
      "h_partenza_dal_posto": "15:35",
      "h_arrivo_ps": "15:35",
      "h_libero_operativo": "",
      "data_arrivo_ps": ""
    }},
    "luogo_intervento": "PS dell'Ospedale San Giovanni",
    "condizione_riferita": "perdita di coscienza",
    "recapito_telefonico": "",
    "codice_uscita": "",
    "codice_rientro": ""
  }},
  "ambulanza": {{
    "sigla": {{"CRI": "", "Sel": ""}},
    "equipaggio": {{
      "autista": "Paolo Rizzo",
      "soccorritore_1": "",
      "soccorritore_2": "",
      "soccorritore_3": "",
      "infermiere": "",
      "medico": "Dr.ssa Laura Neri"
    }}
  }},
  "autorita_presenti": {{
    "carabinieri": false,
    "polizia_stradale": false,
    "polizia_municipale": false,
    "vigili_del_fuoco": false,
    "guardia_medica": false,
    "altra_ambulanza": false,
    "automedica": false,
    "elisoccorso": false,
    "altro_descrizione": ""
  }},
  "dati_paziente": {{
    "cognome_nome": "Mario Verdi",
    "sesso": "M",
    "data_nascita": "1975-06-15",
    "luogo_nascita": "Bari",
    "provincia_nascita": "",
    "residenza": {{
      "citta": "Roma",
      "provincia": "",
      "via": "Via della Libertà",
      "numero_civico": "12"
    }},
    "telefono": "",
    "fonte_dati": "",
    "fonte_dati_altro": ""
  }},
  "rilevazioni": [
    {{
      "tempo": "T1",
      "ora": "15:00",
      "coscienza": "U",
      "cute": "sudata",
      "respiro": "normale",
      "spo2_percent": 89,
      "fc_bpm": 105,
      "pa_mmhg": "95/60",
      "glicemia_mg_dl": 312,
      "temperatura_c": 38.2,
      "gcs": {{
        "apertura_occhi": null,
        "risposta_verbale": null,
        "risposta_motoria": null,
        "totale": 6
      }}
    }}
  ],
  "pupille": {{
    "reagenti": false,
    "dx": "",
    "sx": ""
  }},
  "lesioni": [
    {{
      "parte": "Caviglia Dx",
      "tipo": "B"
    }}
  ],
  "trasporto_non_effettuato": {{
    "causa": "",
    "decesso": {{
      "selezionato": false,
      "ora_decesso": "",
      "firma_medico": ""
    }},
    "rifiuto": {{
      "selezionato": false,
      "firma_interessato": ""
    }}
  }},
  "provvedimenti": {{
    "respiro": {{
      "aspirazione": false,
      "cannula_orofaringea": false,
      "monitor_spo2": true,
      "ossigeno_l_min": null,
      "ventilazione": false,
      "intubazione_num": null
    }},
    "circolo": {{
      "emostasi": false,
      "accesso_venoso": true,
      "monitor_ecg": true,
      "monitor_nibp": false,
      "mce_min": null,
      "dae_num_shock": null
    }},
    "immobilizzazione": {{
      "collare_cervicale": true,
      "ked": false,
      "barella_cucchiaio": false,
      "tavola_spinale": false,
      "steccobenda": false,
      "materassino_depressione": false
    }},
    "altro": {{
      "coperta_isotermica": false,
      "medicazione": false,
      "ghiaccio": false,
      "osservazione": false,
      "custom_1": "",
      "custom_2": ""
    }},
    "infusioni_farmaci": "soluzione fisiologica endovena e Paracetamolo 1000mg i.m."
  }},
  "annotazioni": "Il paziente non ricordava l'evento"
}}

Testo clinico:
\"\"\"{text}\"\"\"
"""


# === FUNZIONE DI PARSING ROBUSTO DEL JSON ===
def parse_json_output(text: str) -> Dict:
    # Cerca blocco JSON
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not match:
        match = re.search(r"(\{.*\})", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as e:
            logging.warning("Errore nel parsing JSON: %s", e)
            return {
                "error": f"Errore nel parsing JSON: {str(e)}",
                "output_grezzo": text
            }
    else:
        return {
            "error": "Nessun JSON valido trovato",
            "output_grezzo": text
        }


# === POST-PROCESSING MIGLIORATO ===
def post_process_medical_data(json_data: Dict) -> Dict:
    """Applica correzioni specifiche ai dati medici per standardizzarli."""
    
    # Prima applica la validazione con le costanti
    corrected_data = validate_and_normalize_values(json_data)
    
    # Correzione valori null -> stringhe vuote per campi stringa
    def fix_null_values(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if value is None:
                    # Campi che devono essere stringhe vuote invece di null
                    string_fields = [
                        'infermiere', 'soccorritore_1', 'soccorritore_2', 'soccorritore_3',
                        'CRI', 'Sel', 'recapito_telefonico', 'telefono', 'fonte_dati',
                        'provincia_nascita', 'provincia', 'h_libero_operativo', 
                        'data_arrivo_ps', 'h_partenza_dal_posto', 'altro_descrizione',
                        'causa', 'ora_decesso', 'firma_medico', 'firma_interessato',
                        'dx', 'sx', 'parte', 'tipo'
                    ]
                    
                    # Campi che devono essere numeri di default
                    numeric_fields = ['episodio_numero']
                    
                    # Campi che devono essere boolean di default
                    boolean_fields = ['reagenti']
                    
                    if key in string_fields:
                        obj[key] = ""
                    elif key in numeric_fields:
                        obj[key] = 1 if key == 'episodio_numero' else None
                    elif key in boolean_fields:
                        obj[key] = False
                else:
                    fix_null_values(value, f"{path}.{key}" if path else key)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                fix_null_values(item, f"{path}[{i}]")
    
    fix_null_values(corrected_data)
    
    # Rimozione rilevazioni duplicate con valori null
    if 'rilevazioni' in corrected_data:
        rilevazioni_valide = []
        for rilevazione in corrected_data['rilevazioni']:
            # Conta quanti campi non sono null/vuoti
            campi_validi = sum(1 for k, v in rilevazione.items() 
                             if v is not None and v != '' and k != 'gcs')
            # Controlla anche GCS
            if rilevazione.get('gcs', {}).get('totale') is not None:
                campi_validi += 1
            
            # Mantieni solo rilevazioni con almeno 2 campi validi
            if campi_validi >= 2:
                rilevazioni_valide.append(rilevazione)
        
        corrected_data['rilevazioni'] = rilevazioni_valide
    
    # Pulizia array lesioni - rimuovi elementi vuoti
    if 'lesioni' in corrected_data:
        lesioni_valide = []
        for lesione in corrected_data['lesioni']:
            if (lesione.get('parte') and lesione.get('parte') != '' and 
                lesione.get('tipo') and lesione.get('tipo') != ''):
                lesioni_valide.append(lesione)
        corrected_data['lesioni'] = lesioni_valide
      # Correzione orari mancanti e logica orari
    if 'chiamata' in corrected_data and 'orari' in corrected_data['chiamata']:
        orari = corrected_data['chiamata']['orari']
        # Se h_partenza è vuoto ma h_arrivo_sul_posto è presente, 
        # probabile che partenza sia poco prima dell'arrivo
        if not orari.get('h_partenza') and orari.get('h_arrivo_sul_posto'):
            orari['h_partenza'] = orari['h_arrivo_sul_posto']
        
        # Se viene menzionato il trasporto al PS ma mancano orari di arrivo
        if (orari.get('h_partenza_dal_posto') == '' and 
            orari.get('h_arrivo_sul_posto') and 
            'trasporto' in corrected_data.get('annotazioni', '').lower()):
            # Stima orario partenza dal posto (es. 30 min dopo arrivo)
            try:
                arrivo_parts = orari['h_arrivo_sul_posto'].split(':')
                if len(arrivo_parts) == 2:
                    ore = int(arrivo_parts[0])
                    minuti = int(arrivo_parts[1]) + 30
                    if minuti >= 60:
                        ore += 1
                        minuti -= 60
                    orari['h_partenza_dal_posto'] = f"{ore:02d}:{minuti:02d}"
            except (ValueError, IndexError):
                pass
          # Se c'è partenza dal posto ma non arrivo PS, stima arrivo PS
        if (orari.get('h_partenza_dal_posto') and 
            orari.get('h_arrivo_ps') == '' and
            ('ps' in corrected_data.get('annotazioni', '').lower() or 
             'trasportato' in corrected_data.get('annotazioni', '').lower() or
             'ospedale' in corrected_data.get('annotazioni', '').lower())):
            try:
                partenza_parts = orari['h_partenza_dal_posto'].split(':')
                if len(partenza_parts) == 2:
                    ore = int(partenza_parts[0])
                    minuti = int(partenza_parts[1]) + 15  # Stima 15 min di viaggio
                    if minuti >= 60:
                        ore += 1
                        minuti -= 60
                    orari['h_arrivo_ps'] = f"{ore:02d}:{minuti:02d}"
            except (ValueError, IndexError):
                pass
      # Correzione monitoraggio SpO2 e altri parametri se presenti valori misurati
    if 'rilevazioni' in corrected_data and 'provvedimenti' in corrected_data:
        for rilevazione in corrected_data['rilevazioni']:
            # Monitor SpO2
            if (rilevazione.get('spo2_percent') is not None and 
                'respiro' in corrected_data['provvedimenti']):
                corrected_data['provvedimenti']['respiro']['monitor_spo2'] = True
            
            # Monitor ECG per FC
            if (rilevazione.get('fc_bpm') is not None and 
                'circolo' in corrected_data['provvedimenti']):
                corrected_data['provvedimenti']['circolo']['monitor_ecg'] = True
            
            # Monitor NIBP per pressione arteriosa
            if (rilevazione.get('pa_mmhg') is not None and 
                'circolo' in corrected_data['provvedimenti']):
                corrected_data['provvedimenti']['circolo']['monitor_nibp'] = True
    
    # Correzione GCS - calcola sottocampi se totale è presente ma sottocampi sono null
    if 'rilevazioni' in corrected_data:
        for rilevazione in corrected_data['rilevazioni']:
            gcs = rilevazione.get('gcs', {})
            if (gcs.get('totale') is not None and 
                gcs.get('apertura_occhi') is None and
                gcs.get('risposta_verbale') is None and 
                gcs.get('risposta_motoria') is None):
                
                totale = gcs['totale']
                if totale == 15:  # GCS normale
                    gcs['apertura_occhi'] = 4
                    gcs['risposta_verbale'] = 5
                    gcs['risposta_motoria'] = 6
                elif totale >= 13:  # Trauma minore
                    gcs['apertura_occhi'] = 4
                    gcs['risposta_verbale'] = 4 if totale == 13 else 5
                    gcs['risposta_motoria'] = 5 if totale == 13 else 6
                elif totale >= 9:  # Trauma moderato
                    gcs['apertura_occhi'] = 3
                    gcs['risposta_verbale'] = 3
                    gcs['risposta_motoria'] = totale - 6
                else:  # Trauma grave
                    gcs['apertura_occhi'] = 2 if totale > 6 else 1
                    gcs['risposta_verbale'] = 2 if totale > 4 else 1
                    gcs['risposta_motoria'] = max(1, totale - 4)
    
    logging.info("Post-processing avanzato completato")
    return corrected_data


# === CORREZIONE STRUTTURA JSON ===
def correct_json_structure(api_key: str, json_data: Dict, *, temperature: float = 0.1, max_tokens: int = 2048) -> Dict:
    """Corregge la struttura del JSON per farla combaciare perfettamente con lo schema richiesto."""
      # Schema di riferimento per la correzione
    reference_schema = {
        "codice_fiscale": "",
        "id": "",
        "episodio_numero": 1,
        "is_ricorrente": False,
        "condizioni_croniche": [],
        "chiamata": {
            "data": "2018-04-02",
            "orari": {
                "h_chiamata": "12:32",
                "h_partenza": "12:35",
                "h_arrivo_sul_posto": "12:44",
                "h_partenza_dal_posto": "13:02",
                "h_arrivo_ps": "13:15",
                "h_libero_operativo": "13:26",
                "data_arrivo_ps": ""
            },
            "luogo_intervento": "Contrada Ughi, 28, 67032, Pescasseroli (AQ)",
            "condizione_riferita": "Malore sul lavoro",
            "recapito_telefonico": "353353104",
            "codice_uscita": "R",
            "codice_rientro": "3"
        },
        "ambulanza": {
            "sigla": {"CRI": "CRI-37", "Sel": "4893"},
            "equipaggio": {
                "autista": "Armani Serena",
                "soccorritore_1": "Finazzi Fulvio",
                "soccorritore_2": "Benassi Giorgia",
                "soccorritore_3": "",
                "infermiere": "Drago Orlando",
                "medico": "Costanzo Omar"
            }
        },
        "autorita_presenti": {
            "carabinieri": True,
            "polizia_stradale": False,
            "polizia_municipale": False,
            "vigili_del_fuoco": True,
            "guardia_medica": False,
            "altra_ambulanza": False,
            "automedica": False,
            "elisoccorso": False,
            "altro_descrizione": ""
        },
        "dati_paziente": {
            "cognome_nome": "Campana Vilma",
            "sesso": "F",
            "data_nascita": "1960-12-28",
            "luogo_nascita": "Andriano",
            "provincia_nascita": "VT",
            "residenza": {
                "citta": "Selvatelle",
                "provincia": "VT",
                "via": "Piazza Saracino",
                "numero_civico": "121"
            },
            "telefono": "353353104",
            "fonte_dati": "documento",
            "fonte_dati_altro": ""
        },
        "rilevazioni": [
            {
                "tempo": "T1",
                "ora": "12:32",
                "coscienza": "V",
                "cute": "cianotica",
                "respiro": "assente",
                "spo2_percent": 93,
                "fc_bpm": 66,
                "pa_mmhg": "171/116",
                "glicemia_mg_dl": 103,
                "temperatura_c": 36.3,
                "gcs": {
                    "apertura_occhi": 2,
                    "risposta_verbale": 4,
                    "risposta_motoria": 1,
                    "totale": 7
                }
            }
        ],
        "pupille": {
            "reagenti": True,
            "dx": "piccola",
            "sx": "grande"
        },
        "lesioni": [
            {
                "parte": "Caviglia Dx",
                "tipo": "B"
            }
        ],
        "trasporto_non_effettuato": {
            "causa": "non_necessita",
            "decesso": {
                "selezionato": False,
                "ora_decesso": "",
                "firma_medico": ""
            },
            "rifiuto": {
                "selezionato": True,
                "firma_interessato": "Filippi Monica"
            }
        },
        "provvedimenti": {
            "respiro": {
                "aspirazione": False,
                "cannula_orofaringea": False,
                "monitor_spo2": True,
                "ossigeno_l_min": None,
                "ventilazione": True,
                "intubazione_num": None
            },
            "circolo": {
                "emostasi": True,
                "accesso_venoso": True,
                "monitor_ecg": True,
                "monitor_nibp": True,
                "mce_min": None,
                "dae_num_shock": None
            },
            "immobilizzazione": {
                "collare_cervicale": False,
                "ked": False,
                "barella_cucchiaio": True,
                "tavola_spinale": False,
                "steccobenda": False,
                "materassino_depressione": False
            },
            "altro": {
                "coperta_isotermica": True,
                "medicazione": True,
                "ghiaccio": False,
                "osservazione": False,
                "custom_1": "",
                "custom_2": ""            },
            "infusioni_farmaci": ""
        },
        "annotazioni": ""
    }
    
    correction_prompt = f"""
Sei un assistente per la correzione della struttura JSON.
Ricevi un JSON che contiene dati medici e devi correggerlo per farlo combaciare PERFETTAMENTE con lo schema di riferimento fornito.

IMPORTANTE:
1. I nomi dei campi devono essere IDENTICI a quelli dello schema di riferimento
2. La struttura annidata deve essere IDENTICA
3. I tipi di dati devono essere mantenuti (string, number, boolean, array, object)
4. Mantieni TUTTI i valori originali, cambia solo i nomi dei campi se necessario
5. Se un campo non esiste nel JSON originale, aggiungilo con valore appropriato (stringa vuota, null, false, array vuoto, etc.)
6. Il campo ID deve rimanere vuoto se non presente nel JSON originale

Schema di riferimento (struttura):
{json.dumps(reference_schema, indent=2, ensure_ascii=False)}

JSON da correggere:
{json.dumps(json_data, indent=2, ensure_ascii=False)}

Restituisci SOLO il JSON corretto, senza altri commenti o spiegazioni.
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": correction_prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        try:
            corrected_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
            corrected_json = parse_json_output(corrected_text)
            
            # Se la correzione ha avuto successo, ritorna il JSON corretto
            if "error" not in corrected_json:
                logging.info("Struttura JSON corretta con successo")
                return corrected_json
            else:
                logging.warning("Errore nella correzione JSON: %s", corrected_json.get("error"))
                return json_data  # Ritorna il JSON originale se la correzione fallisce
        except (KeyError, IndexError) as e:
            logging.warning("Errore nell'estrazione del JSON corretto: %s", e)
            return json_data
    else:
        logging.warning("Errore nella richiesta di correzione: %s", response.text)
        return json_data


# === ESTRAZIONE DATI CLINICI ===
def extract_clinical_info(api_key: str, clinical_text: str, *, temperature: float = 0.1, max_tokens: int = 2048) -> Dict:
    """Interroga l'API di Google AI Studio con processo a quattro fasi:
    1. Fase 0: correzione errori di trascrizione audio
    2. Prima fase: estrazione iniziale dei dati clinici dal testo
    3. Seconda fase: correzione della struttura JSON per farla combaciare con lo schema richiesto
    4. Terza fase: post-processing avanzato con validazione delle costanti
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json",
    }
    
    # FASE 0: Correzione errori di trascrizione
    logging.info("Fase 0 - Correzione errori di trascrizione")
    corrected_text = correct_transcription_errors(api_key, clinical_text, temperature=0.2)
    logging.info("Fase 0 completata - Testo corretto per errori di trascrizione")
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": build_prompt(corrected_text)  # Usa il testo corretto
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
        }
    }

    # FASE 1: Estrazione iniziale dei dati
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        try:
            decoded_output = response_data["candidates"][0]["content"]["parts"][0]["text"]
            initial_json = parse_json_output(decoded_output)
            
            # Se ci sono errori nel parsing, ritorna l'errore
            if "error" in initial_json:
                return initial_json
            
            logging.info("Prima fase completata - JSON estratto")
            
            # FASE 2: Correzione della struttura
            corrected_json = correct_json_structure(api_key, initial_json, temperature=temperature)
            logging.info("Seconda fase completata - Struttura corretta")
            
            # FASE 3: Post-processing avanzato con validazione delle costanti
            final_json = post_process_medical_data(corrected_json)
            logging.info("Terza fase completata - Valori validati con costanti")
            
            return final_json
            
        except (KeyError, IndexError) as e:
            logging.warning("Errore nell'estrazione del testo dalla risposta API: %s", e)
            return {"error": f"Errore nell'estrazione del testo: {e}", "response_data": response_data}
    else:
        logging.warning("Errore nella richiesta API: %s", response.text)
        return {"error": response.text}