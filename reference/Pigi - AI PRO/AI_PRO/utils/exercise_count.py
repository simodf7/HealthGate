import time
import numpy as np
import utils.global_vars

# Funzione per il conteggio delle ripetizioni del Military Press
def count_reps_military_press(landmarks, count, stage):
    current_time = time.time()

    # Punti di riferimento di Mediapipe
    spalla = landmarks.landmark[utils.global_vars.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    gomito = landmarks.landmark[utils.global_vars.mp_pose.PoseLandmark.LEFT_ELBOW.value]
    polso = landmarks.landmark[utils.global_vars.mp_pose.PoseLandmark.LEFT_WRIST.value]
    fianco = landmarks.landmark[utils.global_vars.mp_pose.PoseLandmark.LEFT_HIP.value]
    
    # Calcolo dell'angolo tra spalla, gomito e polso
    angle = np.degrees(np.arctan2(polso.y - gomito.y, polso.x - gomito.x) - 
                       np.arctan2(spalla.y - gomito.y, spalla.x - gomito.x))
    
    # Aggiunta di logica basata sulla posizione del corpo
    shoulder_angle = np.degrees(np.arctan2(spalla.y - fianco.y, spalla.x - fianco.x))
    
    # Controlla se l'angolo della spalla è nella posizione giusta per il military press
    if angle > 160 and shoulder_angle < 45:
        utils.global_vars.stage = "su"  # La posizione "su" (quando il braccio è sollevato)
    
    # Quando l'angolo è sotto una certa soglia, si considera che il movimento è giù
    if angle < 90 and utils.global_vars.stage == "su" and (current_time - utils.global_vars.last_rep_time) > utils.global_vars.min_time_between_reps:
        utils.global_vars.stage = "giù"
        utils.global_vars.count += 1
        utils.global_vars.last_rep_time = current_time
        utils.global_vars.workout_history["military press"] = utils.global_vars.workout_history.get("military press", 0) + 1
    
    return utils.global_vars.count, utils.global_vars.stage

# Funzione per il conteggio delle ripetizioni per il pushup
def count_reps_pushup(landmarks, count, stage):
    current_time = time.time()
    spalla = landmarks.landmark[utils.global_vars.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    gomito = landmarks.landmark[utils.global_vars.mp_pose.PoseLandmark.LEFT_ELBOW.value]
    polso = landmarks.landmark[utils.global_vars.mp_pose.PoseLandmark.LEFT_WRIST.value]
    angle = np.degrees(np.arctan2(polso.y - gomito.y, polso.x - gomito.x) - 
                       np.arctan2(spalla.y - gomito.y, spalla.x - gomito.x))

    if angle > 160:
        utils.global_vars.stage = "su"
    if angle < 90 and utils.global_vars.stage == "su" and (current_time - utils.global_vars.last_rep_time) > utils.global_vars.min_time_between_reps:
        utils.global_vars.stage = "giù"
        utils.global_vars.count += 1
        utils.global_vars.last_rep_time = current_time
        utils.global_vars.workout_history["pushup"] = utils.global_vars.workout_history.get("pushup", 0) + 1
    
    return utils.global_vars.count, utils.global_vars.stage

# Funzione per il conteggio delle ripetizioni per lo squat
def count_reps_squat(landmarks, count, stage):
    current_time = time.time()
    anca = landmarks.landmark[utils.global_vars.mp_pose.PoseLandmark.LEFT_HIP.value]
    ginocchio = landmarks.landmark[utils.global_vars.mp_pose.PoseLandmark.LEFT_KNEE.value]
    caviglia = landmarks.landmark[utils.global_vars.mp_pose.PoseLandmark.LEFT_ANKLE.value]

    angle = np.degrees(np.arctan2(ginocchio.y - anca.y, ginocchio.x - anca.x) - 
                       np.arctan2(caviglia.y - ginocchio.y, caviglia.x - ginocchio.x))

    if angle > 170:
        utils.global_vars.stage = "su"
    if angle < 90 and utils.global_vars.stage == "su" and (current_time - utils.global_vars.last_rep_time) > utils.global_vars.min_time_between_reps:
        utils.global_vars.stage = "giù"
        utils.global_vars.count += 1
        utils.global_vars.last_rep_time = current_time
        utils.global_vars.workout_history["squat"] = utils.global_vars.workout_history.get("squat", 0) + 1
    
    return utils.global_vars.count, utils.global_vars.stage
