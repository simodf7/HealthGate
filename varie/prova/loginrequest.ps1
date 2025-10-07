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
