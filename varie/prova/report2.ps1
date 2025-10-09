
'''
# ============================================
# 2️⃣ Test Ottieni report per patient_id
# ============================================
$patientId = 1  # Sostituisci con un ID valido nel tuo DB
Write-Host "➡️  [2] Ottieni report per patient_id = $patientId..."
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/reports/$patientId" -Method GET
    Write-Host "✅ Risposta:" ($response | ConvertTo-Json -Depth 5) "`n"
}
catch {
    Write-Host "❌ Errore:" $_.Exception.Message "`n"
}
'''


''' 
# ============================================
# 3️⃣ Test Ottieni report per codice fiscale
# ============================================
$cf = "RSSMRA80A01H501U"  # Codice fiscale di esempio
Write-Host "➡️  [3] Ottieni report per CF = $cf..."
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/reports/$cf" -Method GET
    Write-Host "✅ Risposta:" ($response | ConvertTo-Json -Depth 5) "`n"
}
catch {
    Write-Host "❌ Errore:" $_.Exception.Message "`n"
}


# ============================================
# 4️⃣ Test Creazione nuovo report
# ============================================
Write-Host "➡️  [4] Creazione nuovo report..."
$headers = @{
    "Content-Type" = "application/json"
    "X-user-id" = "123"   # header richiesto dal tuo endpoint
}

$body = @{
    social_sec_number = "RSSMRA80A01H501U"
    date = "2025-10-08"
    sintomi = @("febbre", "tosse")
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/report" -Method POST -Headers $headers -Body $body
    Write-Host "✅ Report creato:" ($response | ConvertTo-Json -Depth 5) "`n"
}
catch {
    Write-Host "❌ Errore nella creazione report:" $_.Exception.Message "`n"
}
''' 