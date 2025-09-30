@echo off
REM Avvio il server Keycloak in una nuova finestra
start "Keycloak Server" cmd /k "cd /d keycloak-26.1.0 && bin\kc.bat start-dev"

REM Attendo 20 secondi per dare il tempo al server di avviarsi
timeout /t 20 >nul

REM Avvio l'applicazione Python in una nuova finestra
start "App Python" cmd /k "python .\app.py"

REM Attendo 20 secondi (eventuale tempo di inizializzazione dell'app Python)
timeout /t 20 >nul

REM Apro il browser alla pagina http://localhost:5000
start "" "http://localhost:5000"

exit
