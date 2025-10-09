# ============================================
# 🧪 Test Report Management Service API
# ============================================

# Imposta l'endpoint base (modifica se usi un host diverso)
$baseUrl = "http://127.0.0.1:8005"

Write-Host "🚀 Test Report Management Service su $baseUrl`n"


$patient_id = 1
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/report/$patient_id" -Method GET
    Write-Host "✅ Risposta:" ($response | ConvertTo-Json -Depth 5) "`n"
}
catch {
    Write-Host "❌ Errore:" $_.Exception.Message "`n"
}


