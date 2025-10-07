@echo off

chcp 65001 > nul

echo ========================================
echo   Avvio HealthGate System (Schede)
echo ========================================
echo.

:: Avvia tutti i servizi in Windows Terminal con schede separate
start "" wt ^
    --title "Gateway" -d ".\microservices\api-gateway" cmd /k "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" ^; ^
    new-tab --title "Auth" -d ".\microservices\auth" cmd /k "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001" ^; ^
    new-tab --title "Ingest" -d ".\microservices\ingestion" cmd /k "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8002" ^; ^
    new-tab --title "Decision" -d ".\microservices\decision-engine" cmd /k "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8003" ^; ^
    new-tab --title "Report" -d ".\microservices\report-management" cmd /k "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8005" ^; ^
    new-tab --title "Chroma" -d ".\microservices\decision-engine" cmd /k "python -m chroma run --host localhost --port 8010" ^; ^
    new-tab --title "HealthGate" -d "." cmd /k "python -m streamlit run HealthGate.py"

echo.
echo ========================================
echo   Tutti i servizi avviati in Windows Terminal!
echo ========================================
echo.
echo Servizi attivi:
echo   - Gateway:  http://localhost:8000
echo   - Auth:     http://localhost:8001
echo   - Ingest:   http://localhost:8002
echo   - Decision: http://localhost:8003
echo   - Chroma:   http://localhost:8010
echo   - Frontend: http://localhost:8501
echo.
echo Usa Ctrl+Tab per navigare tra le schede
echo Premi un tasto per chiudere questa finestra...
pause > nul