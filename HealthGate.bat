@echo off

chcp 65001 > nul

start "HealthGate" python -m streamlit run ".\HealthGate.py"