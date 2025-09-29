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


$llmHeaders = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json"
}

# --- 3. Chiamata al microservizio /llm ---
$llmResponse = Invoke-RestMethod -Uri "$baseUrl/llm" -Method GET `
    -Headers $llmHeaders `

# --- 4. Mostra risposta ---
Write-Host "Risposta da /llm:"
$llmResponse | ConvertTo-Json -Depth 5
