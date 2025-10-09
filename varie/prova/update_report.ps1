# test_update_report.ps1
# Script PowerShell per testare l'endpoint PUT /report/id/{report_id}

# Imposta l'ID del report da aggiornare
$report_id = "68e6e2b34f8a46304842c2e7"   # 🔹 Sostituisci con un ID reale del tuo DB

# Corpo della richiesta JSON
$body = @{
    report_id   = $report_id
    diagnosi    = "Paziente affetto da influenza stagionale"
    trattamento = "Somministrazione di antipiretici e riposo"
} | ConvertTo-Json

# URL dell'endpoint
$url = "http://localhost:8005/report/$report_id"

# Esegui la richiesta PUT
$response = Invoke-RestMethod -Uri $url -Method Put -Body $body -ContentType "application/json"

# Mostra la risposta
Write-Host "`n✅ Risposta dal server:`n"
$response | ConvertTo-Json -Depth 5
