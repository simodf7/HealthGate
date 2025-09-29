"""
[BACKEND] data_check_visualizer.py

Modulo per la visualizzazione e verifica della correttezza dei dati JSON dei pazienti.
"""

import streamlit as st
import json
import datetime

def data_scheme(json_file):
    CUSTOM_LABELS = {
        "is_ricorrente": "Paziente ricorrente",
        "temperatura_c": "Temperatura corporea",
        "h": "Orario di",
        "altro_descrizione": "Altro",
        "citta": "Città",
        "cognome_nome": "Cognome e nome",
        "fonte_dati_altro": "Altre fonti dati"
    }

    EXCLUDED_KEYS = {"id", "paziente_id", "rilevazioni"}

    TIME_FIELDS = [
        "trasporto_non_effettuato.decesso.ora_decesso",
        "chiamata.orari.h_chiamata",
        "chiamata.orari.h_partenza",
        "chiamata.orari.h_arrivo_sul_posto",
        "chiamata.orari.h_partenza_dal_posto",
        "chiamata.orari.h_arrivo_ps",
        "chiamata.orari.h_libero_operativo"
    ]

    DATE_FIELDS = [
        "dati_paziente.data_nascita",
        "chiamata.data",
        "chiamata.orari.data_arrivo_ps"
    ]

    CHECKBOX_FIELDS = [
        "dati_generali.is_ricorrente",
        "pupille.reagenti",
        "autorita_presenti.carabinieri",
        "autorita_presenti.polizia_stradale",
        "autorita_presenti.polizia_municipale",
        "autorita_presenti.vigili_del_fuoco",
        "autorita_presenti.guardia_medica",
        "autorita_presenti.altra_ambulanza",
        "autorita_presenti.automedica",
        "autorita_presenti.elisoccorso",
        "trasporto_non_effettuato.decesso.selezionato",
        "trasporto_non_effettuato.rifiuto.selezionato",
        "provvedimenti.respiro.aspirazione",
        "provvedimenti.respiro.cannula_orofaringea",
        "provvedimenti.respiro.monitor_spo2",
        "provvedimenti.respiro.ventilazione",
        "provvedimenti.respiro.intubazione_num",
        "provvedimenti.circolo.emostasi",
        "provvedimenti.circolo.accesso_venoso",
        "provvedimenti.circolo.monitor_ecg",
        "provvedimenti.circolo.monitor_nibp",
        "provvedimenti.immobilizzazione.collare_cervicale",
        "provvedimenti.immobilizzazione.ked",
        "provvedimenti.immobilizzazione.barella_cucchiaio",
        "provvedimenti.immobilizzazione.tavola_spinale",
        "provvedimenti.immobilizzazione.steccobenda",
        "provvedimenti.immobilizzazione.materassino_depressione",
        "provvedimenti.altro.coperta_isotermica",
        "provvedimenti.altro.medicazione",
        "provvedimenti.altro.ghiaccio",
        "provvedimenti.altro.osservazione"
    ]

    SELECT_FIELDS_OPTIONS = {
        "dati_paziente.sesso": ["None", "M", "F"],
        "trasporto_non_effettuato.causa": [
            "None", 
            "Effettuato da altra ambulanza",
            "Effettuato da elisoccorso",
            "Non necessita",
            "Trattato sul posto",
            "Sospeso da centrale",
            "Non reperito",
            "Scherzo"
        ],
        "chiamata.codice_uscita": ["None", "B", "V", "G", "R"],
        "chiamata.codice_rientro": ["None", "0", "1", "2", "3", "4"],
        "dati_paziente.fonte_dati": ["None", "paziente", "parente", "documento", "altro"],
        "pupille.dx": ["None", "piccola", "media", "grande"],
        "pupille.sx": ["None", "piccola", "media", "grande"]
    }

    RILEVAZIONI_SELECT_FIELDS = {
        "coscienza": ["None", "A", "V", "P", "U"],
        "cute": ["None", "normale", "pallida", "cianotica", "sudata"],
        "respiro": ["None", "normale", "tachipnoico", "bradipnoico", "assente"],
        "gcs.apertura_occhi": ["None", "4", "3", "2", "1"],
        "gcs.risposta_verbale": ["None", "5", "4", "3", "2", "1"],
        "gcs.risposta_motoria": ["None", "6", "5", "4", "3", "2", "1"]
    }

    RILEVAZIONI_TIME_FIELDS = ["ora"]

    NUMERIC_FIELDS = {
        "dati_generali.episodio_numero",
        "provvedimenti.respiro.ossigeno_l_min",
        "provvedimenti.circolo.mce_min",
        "provvedimenti.circolo.dae_num_shock",
        # "dati_paziente.residenza.numero_civico",
        "spo2_percent",
        "fc_bpm",
        "glicemia_mg_dl",
        "temperatura_c"
    }

    PRIORITY_ORDER = [
        "dati_generali",
        "dati_paziente",
        "chiamata",
        "ambulanza",
        "pupille",
        "provvedimenti",
        "trasporto_non_effettuato",
        "autorita_presenti"
    ]

    def format_label(key):
        key_lower = key.lower()
        if key_lower in CUSTOM_LABELS:
            return CUSTOM_LABELS[key_lower]
        label = key.replace("_", " ").lower()
        label = label.replace(" ps", " pronto soccorso").replace("ps ", "pronto soccorso ").replace(" ps ", " pronto soccorso ")
        label = label.replace("autorita", "autorità")

        if label.startswith("h "):
            label = label.replace("h ", "orario di ", 1)

        return label.capitalize()

    def render_section(section_data, section_name, container, path="root", level=1, parent_path=None):
        formatted_section = format_label(section_name)
        container.markdown(f"{'#' * level} {formatted_section}")

        for key, value in section_data.items():
            if key.lower() in EXCLUDED_KEYS:
                continue

            current_path = f"{path}.{key}"
            formatted_key = format_label(key)

            if "rilevazioni" in path.lower():
                path_tail = current_path.split(".")[-1]
                parent_tail = current_path.split(".")[-2] if "." in current_path else ""
                full_key = f"{parent_tail}.{path_tail}" if parent_tail == "gcs" else path_tail

                if full_key in RILEVAZIONI_SELECT_FIELDS:
                    options = RILEVAZIONI_SELECT_FIELDS[full_key]
                    default_value = str(value) if str(value) in options else options[0]
                    container.selectbox(label=formatted_key, options=options, index=options.index(default_value), key=current_path)
                    continue
                elif full_key in RILEVAZIONI_TIME_FIELDS:
                    try:
                        time_str = str(value).strip()
                        if time_str:
                            try:
                                time_value = datetime.datetime.strptime(time_str, "%H:%M:%S").time()
                            except ValueError:
                                time_value = datetime.datetime.strptime(time_str, "%H:%M").time()
                        else:
                            time_value = None
                    except Exception:
                        time_value = None
                    container.time_input(label=formatted_key, value=time_value, key=current_path)
                    continue
                elif format_label(key).lower() == "tempo":
                    continue

            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)

            if current_path in DATE_FIELDS:
                try:
                    date_value = datetime.date.fromisoformat(str(value))
                except Exception:
                    date_value = None
                container.date_input(label=formatted_key, value=date_value, key=current_path)
            elif current_path in TIME_FIELDS:
                try:
                    time_str = str(value).strip()
                    if time_str:
                        try:
                            time_value = datetime.datetime.strptime(time_str, "%H:%M:%S").time()
                        except ValueError:
                            time_value = datetime.datetime.strptime(time_str, "%H:%M").time()
                    else:
                        time_value = None
                except Exception:
                    time_value = None
                container.time_input(label=formatted_key, value=time_value, key=current_path)
            elif current_path in CHECKBOX_FIELDS:
                checkbox_value = bool(value)
                container.checkbox(label=formatted_key, value=checkbox_value, key=current_path)
            elif current_path in SELECT_FIELDS_OPTIONS:
                options = SELECT_FIELDS_OPTIONS[current_path]
                default_value = str(value) if value in options else options[0]
                container.selectbox(label=formatted_key, options=options, index=options.index(default_value), key=current_path)
            elif current_path.lower() in NUMERIC_FIELDS or key.lower() in NUMERIC_FIELDS:
                try:
                    container.number_input(label=formatted_key, value=float(value), key=current_path)
                except:
                    container.number_input(label=formatted_key, key=current_path)
            elif isinstance(value, dict):
                render_section(value, key, container, current_path, level + 1)
            else:
                container.text_input(label=formatted_key, value=str(value), key=current_path)

    if json_file is not None:
        try:
            col1, col2, col3 = st.columns(3)
            columns = [col1, col2, col3]
            macro_index = 0

            macro_sections = {}
            general_fields = {}

            for key, value in json_file.items():
                if key.lower() in EXCLUDED_KEYS:
                    continue
                if isinstance(value, dict):
                    macro_sections[key.lower()] = (key, value)
                else:
                    general_fields[key] = value

            if general_fields:
                macro_sections["dati_generali"] = ("dati_generali", general_fields)

            sorted_keys = PRIORITY_ORDER + sorted([k for k in macro_sections if k not in PRIORITY_ORDER])

            for key in sorted_keys:
                if key in macro_sections and key not in {"provvedimenti", "autorita_presenti", "trasporto_non_effettuato", "rilevazioni"}:
                    original_key, section_data = macro_sections[key]
                    col = columns[macro_index % 3]
                    render_section(section_data, original_key, col, path=original_key)
                    macro_index += 1

            if "autorita_presenti" in macro_sections or "trasporto_non_effettuato" in macro_sections:
                colA, colB = st.columns(2)
                if "autorita_presenti" in macro_sections:
                    original_key, section_data = macro_sections["autorita_presenti"]
                    render_section(section_data, original_key, colA, path=original_key)
                if "trasporto_non_effettuato" in macro_sections:
                    original_key, section_data = macro_sections["trasporto_non_effettuato"]
                    render_section(section_data, original_key, colB, path=original_key)

            if "provvedimenti" in macro_sections:
                original_key, section_data = macro_sections["provvedimenti"]
                st.markdown("# Provvedimenti")
                sottosezioni = ["respiro", "circolo", "immobilizzazione", "altro"]
                colA, colB, colC, colD = st.columns(4)
                colonne = [colA, colB, colC, colD]
                for i, sottosezione in enumerate(sottosezioni):
                    if sottosezione in section_data:
                        render_section(section_data[sottosezione], sottosezione, colonne[i], path=f"{original_key}.{sottosezione}", level=2)

            if "rilevazioni" in json_file:
                rilevazioni_data = json_file["rilevazioni"]
                st.markdown("# Rilevazioni")
                rilevazioni_cols = st.columns(3)
                if isinstance(rilevazioni_data, dict):
                    render_section(rilevazioni_data, "rilevazioni", rilevazioni_cols[0], path="rilevazioni")
                elif isinstance(rilevazioni_data, list):
                    for i, item in enumerate(rilevazioni_data):
                        col_relevations = rilevazioni_cols[i % 3]
                        render_section(item, f"rilevazione {i+1}", col_relevations, path=f"rilevazioni.{i}", level=2)

        except Exception as e:
            st.error(f"Errore nel parsing del JSON: {e}")