'''
[BACKEND/DATABASE] constants.py

Costanti e enumerazioni per la codifica standard dei dati paziente.
'''

from enum import Enum

class CodiceUscita(Enum):
    BIANCO = "B"
    VERDE = "V"
    GIALLO = "G"
    ROSSO = "R"

class CodiceRientro(Enum):
    NON_NECESSARIO = "0"
    NON_TRASPORTATO = "1"
    NON_URGENTE = "2"
    URGENTE = "3"
    CRITICO = "4"

class Sesso(Enum):
    MASCHIO = "M"
    FEMMINA = "F"

class Coscienza(Enum):
    SVEGLIO = "A"
    VOCE = "V"
    DOLORE = "P"
    INCOSCIENTE = "U"

class Cute(Enum):
    NORMALE = "normale"
    PALLIDA = "pallida"
    CIANOTICA = "cianotica"
    SUDATA = "sudata"

class Respiro(Enum):
    NORMALE = "normale"
    TACHIPNOICO = "tachipnoico"
    BRADIPNOICO = "bradipnoico"
    ASSENTE = "assente"

class PupilleDiametro(Enum):
    PICCOLA = "piccola"
    MEDIA = "media"
    GRANDE = "grande"

class LesioniParti(Enum):
    """Parti anatomiche traumatizzabili per mappatura lesioni realistiche"""
    TESTA = "Testa"
    COLLO = "Collo"
    BRACCIO_SX = "Braccio Sx"
    BRACCIO_DX = "Braccio Dx"
    AVAMBRACCIO_SX = "Avambraccio Sx"
    AVAMBRACCIO_DX = "Avambraccio Dx"
    MANO_SX = "Mano Sx"
    MANO_DX = "Mano Dx"
    TORACE = "Torace"
    ADDOME = "Addome"
    SCHIENA = "Schiena"
    PELVI = "Pelvi"
    COSCIA_SX = "Coscia Sx"
    COSCIA_DX = "Coscia Dx"
    GAMBA_SX = "Gamba Sx"
    GAMBA_DX = "Gamba Dx"
    PIEDE_SX = "Piede Sx"
    PIEDE_DX = "Piede Dx"
    CAVIGLIA_SX = "Caviglia Sx"
    CAVIGLIA_DX = "Caviglia Dx"

class LesioniTipi(Enum):
    """Codificazione standard dei tipi di lesione (sistema ospedaliero)"""
    AMPUTAZIONE = "1"
    DEFORMITA = "2"
    DOLORE = "3"
    EMORRAGIA = "4"
    FERITA_PROFONDA = "5"
    FERITA_SUPERFICIALE = "6"
    TRAUMA_CHIUSO = "7"
    USTIONE = "8"
    DEFICIT_MOTORIO = "9"
    SENSIBILITA_ASSENTE = "A"
    FRATTURA_SOSPETTA = "B"
    LUSSAZIONE_SOSPETTA = "C"

# Liste per facilità di accesso
LESIONI_PARTI_VALUES = [parte.value for parte in LesioniParti]
LESIONI_TIPI_VALUES = [tipo.value for tipo in LesioniTipi]
