# python -m streamlit run c:\HealthGate\HealthGate.py
"""
[FRONTEND] HealtGate.py

Modulo principale per l'applicazione HealthGate.
"""

import sys
import os

# Ottieni la directory del file corrente
current_dir = os.path.dirname(os.path.abspath(__file__))

# Aggiungi la sottocartella "frontend" al path
frontend_path = os.path.join(current_dir, 'frontend')
sys.path.append(frontend_path)

import main

# Avvio dell'interfaccia principale
main.interface()