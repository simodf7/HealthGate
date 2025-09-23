import cv2
import time
import numpy as np
import pandas as pd
import joblib
import utils.global_vars
from utils.exercise_count import count_reps_military_press, count_reps_pushup, count_reps_squat
from utils.draw import draw_landmarks, draw_start_timer

# Carica il modello SVM pre-addestrato per il riconoscimento delle pose
model = joblib.load('model\svm_model.pkl')


def generate_video_stream():

    while True:
        ret, frame = utils.global_vars.cap.read()  # Legge un frame dalla webcam
        if not ret:
            break  # Interrompe il loop se non riesce a leggere un frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Converte l'immagine in RGB
        results = utils.global_vars.pose.process(rgb_frame)  # Processa il frame con MediaPipe

        if utils.global_vars.start_timer > 0:
            draw_start_timer(frame, utils.global_vars.start_timer)
            time.sleep(1)
            utils.global_vars.start_timer -= 1
            continue

        if utils.global_vars.resting:
            # Controlla se il periodo di riposo è terminato
            rest_remaining = max(0, utils.global_vars.rest_duration - (time.time() - utils.global_vars.rest_start_time))
            if rest_remaining > 0:
                cv2.putText(frame, f'Rest time remaining: {int(rest_remaining)}s', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                ret, jpeg = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                frame = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                continue
            else:
                utils.global_vars.resting = False

        if results.pose_landmarks and not utils.global_vars.resting:  # Se ci sono landmarks e non si è in pausa
            landmarks = results.pose_landmarks  # Ottieni i landmarks
            draw_landmarks(frame, landmarks)  # Disegna i landmark e le linee sul frame
            keypoints = np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark]).flatten().reshape(1, -1)  # Crea un array di punti chiave
            feature_names = [f"landmark_{i}_{axis}" for i in range(len(landmarks.landmark)) for axis in ["x", "y", "z"]]
            keypoints_df = pd.DataFrame(keypoints, columns=feature_names)  # Converte in DataFrame per il modello

            # Predice l'esercizio
            exercise_class = int(model.predict(keypoints_df)[0])  # Usa il modello SVM per classificare l'esercizio

            if exercise_class < len(utils.global_vars.exercise_label):
                exercise_name = utils.global_vars.exercise_label[exercise_class]
                utils.global_vars.current_exercise = exercise_name  # Aggiorna l'esercizio corrente

                # Esegui il conteggio in base all'esercizio rilevato
                if exercise_name == "military press":
                    utils.global_vars.count, utils.global_vars.stage = count_reps_military_press(landmarks, utils.global_vars.count, utils.global_vars.stage)
                elif exercise_name == "pushup":
                    utils.global_vars.count, utils.global_vars.stage = count_reps_pushup(landmarks, utils.global_vars.count, utils.global_vars.stage)
                elif exercise_name == "squat":
                    utils.global_vars.count, utils.global_vars.stage = count_reps_squat(landmarks, utils.global_vars.count, utils.global_vars.stage)
                
                utils.global_vars.current_reps = utils.global_vars.count

                # Modifica la logica di riposo basata su count_max
                if utils.global_vars.count >= utils.global_vars.target_repetitions and utils.global_vars.target_repetitions > 0 and utils.global_vars.resting == False:
                    utils.global_vars.resting = True
                    utils.global_vars.rest_start_time = time.time()
                    # Resetta il conteggio
                    utils.global_vars.count = 0
                    utils.global_vars.current_reps = 0

        # Codifica il frame in JPEG per lo streaming
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue  # Salta il frame se non riesce a codificarlo
        frame = jpeg.tobytes()  # Converte il frame in byte
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')  # Ritorna il frame per il video stream
