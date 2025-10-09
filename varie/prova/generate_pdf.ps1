# ================================
#  Test per la route PDF FastAPI
#  Autore: ChatGPT
#  Uso:
#    .\test_pdf_route.ps1 -ReportId "1234"
#    .\test_pdf_route.ps1 -ReportId "1234" -OutputFile "C:\temp\report.pdf" -BaseUrl "http://localhost:8001"
# ================================

param(
    [string]$ReportId = "1234",
    [string]$OutputFile = "report.pdf",
    [string]$BaseUrl = "http://localhost:8005"
)

# Costruisci l'URL della richiesta
$Url = "$BaseUrl/report/pdf/$ReportId"

Write-Host "----------------------------------------"
Write-Host "📄 Richiesta al server FastAPI:"
Write-Host "➡️  URL: $Url"
Write-Host "➡️  Salvataggio file in: $OutputFile"
Write-Host "----------------------------------------"

try {
    # Fai la richiesta GET e salva il PDF
    $response = Invoke-WebRequest -Uri $Url -OutFile $OutputFile -ErrorAction Stop

    Write-Host "✅ PDF scaricato correttamente!"
    Write-Host "📁 File salvato in: $OutputFile"
}
catch {
    Write-Host "❌ Errore nella richiesta HTTP!"
    Write-Host $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $errorBody = $reader.ReadToEnd()
        Write-Host "🔍 Dettagli risposta server:"
        Write-Host $errorBody
    }
}

Write-Host "----------------------------------------"
Write-Host "Operazione terminata."
Write-Host "----------------------------------------"
