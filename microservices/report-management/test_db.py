from mongodb import save_report_with_anagrafica, get_reports_by_patient

# Simula un nuovo referto clinico
report = {
    "data": "2025-10-04",
    "diagnosi": "Tonsillite acuta",
    "sintomi": "Mal di gola, febbre, difficoltà a deglutire",
    "trattamento": "Antibiotico e riposo",
    "decisione": "Pronto soccorso necessario",
    "motivazione": "Febbre alta persistente e difficoltà respiratorie"
}

# ID paziente presente nella tabella patients di Postgres (es. 2 = Ale Campanella)
patient_id = 2

# Salva il report con anagrafica
save_report_with_anagrafica(patient_id, report)

# Recupera tutti i report del paziente da Mongo
reports = get_reports_by_patient(patient_id)

print(f"\nReport salvato per paziente {patient_id}:")
for r in reports:
    print(r)
