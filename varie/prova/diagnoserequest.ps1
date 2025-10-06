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

# --- 2. Invia file per diagnosi completa ---
$filePath = "C:\Users\simon\Desktop\HealthGate\HealthGate\prove_audio\rumore_rita.mp3"

$headers = @{
    "Authorization" = "Bearer $token"
}

$form = @{
    file = Get-Item $filePath
}

$response = Invoke-WebRequest -Uri "$baseUrl/diagnose" -Method Post -Headers $headers -Form $form

# --- 3. Mostra risposta ---
Write-Host "Risposta da /diagnose:"
$response.Content | Format-List
