# python -m streamlit run c:\HealthGate\proveale\frontend\HealthGate.py
"""
[FRONTEND] HealtGate.py

Modulo principale per l'applicazione HealthGate.
"""

import sys

# Percorsi ai moduli
sys.path.append('./frontend')

import main_page as mp

# Avvio dell'interfaccia principale
mp.main_interface()