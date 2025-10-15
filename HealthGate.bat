@echo off
chcp 65001 > nul

echo ========================================
echo   Avvio HealthGate System tramite Docker
echo ========================================
echo.

:: Controlla che Docker sia attivo
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Errore: Docker non è in esecuzione.
    echo Avvia Docker Desktop e riprova.
    pause
    exit /b
)

:: Costruisce e avvia i container in background
echo Costruzione e avvio dei container...
docker compose up -d --build

if %errorlevel% neq 0 (
    echo Errore durante l'avvio dei container.
    pause
    exit /b
)

echo.
echo ========================================
echo   Tutti i servizi sono stati avviati!
echo ========================================
echo.
echo Servizi attivi:
echo   - Frontend:  http://localhost:8501
echo   - Gateway:   http://localhost:8000
echo   - Auth:      http://localhost:8001
echo   - Ingestion: http://localhost:8002
echo   - Decision:  http://localhost:8003
echo   - Report:    http://localhost:8004
echo   - Aggregator:http://localhost:8005
echo   - Chroma:    http://localhost:8010
echo.
echo Per vedere i log: docker compose logs -f
echo Per fermare tutto: docker compose down
echo.
pause
