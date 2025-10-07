# --- Configurazione ---
$baseUrl = "http://localhost:8000"

# --- 1. Dati del paziente da inserire ---
$signupBody = @{
    firstname   = "Rita"
    lastname    = "Castaldi"
    birth_date  = "2001-08-09"
    sex         = "F"
    birth_place = "Napoli"
    password    = "Password124"
} | ConvertTo-Json

# --- 2. Chiamata API di signup ---
$signupResponse = Invoke-RestMethod -Uri "$baseUrl/signup/patient" -Method POST `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body $signupBody

# --- 3. Mostra risultato ---
Write-Host "Registrazione completata. ID nuovo paziente:" $signupResponse.id
