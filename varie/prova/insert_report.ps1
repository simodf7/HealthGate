# ===============================
# Test per l'endpoint POST /report
# ===============================

# URL del tuo servizio FastAPI
$Url = "http://localhost:8005/report"

# Corpo della richiesta in formato JSON
$Body = @{
    patient_id = "123456"
    social_sec_number = "RSSMRA85T10A562S"
    date = "2025-10-09"
    diagnosi = "Influenza stagionale"
    sintomi = "Febbre, tosse, mal di testa"
    trattamento = "Paracetamolo e riposo"
} | ConvertTo-Json

# Header HTTP
$Headers = @{
    "Content-Type" = "application/json"
}

# Invia la richiesta POST e cattura la risposta
try {
    Write-Host "Invio richiesta a $Url..."
    $Response = Invoke-RestMethod -Uri $Url -Method Post -Headers $Headers -Body $Body
    Write-Host "`n✅ Risposta dal server:"
    $Response | ConvertTo-Json -Depth 5
}
catch {
    Write-Host "`n❌ Errore durante la richiesta:"
    Write-Host $_.Exception.Message
}
