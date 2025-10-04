# --- Configurazione ---
$baseUrl = "http://localhost:8000"
$social_sec_number = "CSTRTI01M49F839N"
$password = "Password124"

# --- 1. Login e recupero token ---
$loginBody = @{
    social_sec_number = $social_sec_number
    password = $password
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "$baseUrl/login/patient" -Method POST `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body $loginBody

# Estrai l'access token
$token = $loginResponse.access_token
Write-Host "Token ottenuto:" $token

# --- 2. Prepara la richiesta di diagnosi ---
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$diagnoseBody = @{
    storia  = "Donna di 43 anni, senza particolari precedenti medici."
    sintomi = "Da questa mattina riferisce congestione nasale e lieve cefalea frontale. Non ha febbre, tosse o mal di gola. Riferisce sonno disturbato nella notte precedente a causa del naso chiuso. Le condizioni generali sono buone."
} | ConvertTo-Json

# --- 3. Invia richiesta al endpoint /llm/diagnose ---
$response = Invoke-RestMethod -Uri "$baseUrl/llm/diagnose" -Method POST `
    -Headers $headers `
    -Body $diagnoseBody

# Stampa verticale con colori
Write-Host "Decisione:" -ForegroundColor Green
Write-Host $response.decisione

Write-Host "`nMotivazione:" -ForegroundColor Green
Write-Host $response.motivazione
