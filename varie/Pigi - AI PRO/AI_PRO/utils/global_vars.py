import cv2
import mediapipe as mp

# Dichiarazione delle variabili globali
workout_history = {}
rest_duration = 60
start_timer = 5
current_exercise = "Not recognized"
current_reps = 0
target_repetitions = 10
# Etichette degli esercizi
exercise_label = ["squat", "pushup", "", "military press"]

cap = cv2.VideoCapture(0)  # Apre la webcam predefinita

# Inizializza MediaPipe per il rilevamento della posa
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Variabili globali per il conteggio delle ripetizioni e lo stato dell'allenamento
count = 0  # Conteggio delle ripetizioni
count_max = 0  # Massimo numero di ripetizioni
stage = None  # Stato attuale (es. "su" o "giù")
resting = False  # Indica se si è in pausa
rest_start_time = 0  # Timestamp di inizio pausa
start_time = 0  # Timestamp di inizio esercizio
start_delay_time = 5  # Ritardo iniziale prima di iniziare
remaining_start_delay = start_delay_time  # Tempo rimanente per il ritardo iniziale
exercise_recognized = False  # Indica se un esercizio è stato riconosciuto
min_time_between_reps = 1  # Minimo tempo tra due ripetizioni
last_rep_time = 0  # Timestamp dell'ultima ripetizione