import cv2 #
import mediapipe as mp
import numpy as np
import pandas as pd
import time

# Inizializzazione di MediaPipe per il rilevamento della posa
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Impostazioni della videocamera
cap = cv2.VideoCapture(0)

# Dizionario per associare l'esercizio alla label e al nome del file
exercise_options = {
    '0': ('squat', 'squat_data.csv'),
    '1': ('pushup', 'pushup_data.csv'),
    '2': ('biceps_curl', 'biceps_curl_data.csv'),
    '3': ('mil_press', 'mil_press_data.csv')
}

# Selezione dell'esercizio
print("Seleziona l'esercizio:")
print("0 - Squat")
print("1 - Push-up")
print("2 - Biceps Curl")
print("3 - Military Press")
exercise_choice = input("Inserisci il numero dell'esercizio: ")

# Verifica scelta valida
if exercise_choice not in exercise_options:
    print("Scelta non valida. Uscita dal programma.")
    cap.release()
    cv2.destroyAllWindows()
else:
    # Imposta nome esercizio, nome file, e label per il salvataggio
    exercise_name, filename = exercise_options[exercise_choice]
    label = int(exercise_choice)  # Label per l'esercizio
    print(f"Raccolta dati per: {exercise_name}. Premi 'q' per terminare.")

    # Variabili per raccolta dati
    data = []

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Converti l'immagine a RGB per MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb_frame)

            # Se vengono rilevati landmarks, raccogli i dati
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                keypoints = np.array([[lm.x, lm.y, lm.z] for lm in landmarks]).flatten()
                keypoints = np.append(keypoints, label)  # Aggiungi la label ai keypoints
                data.append(keypoints)

                # Visualizza la posa sull'immagine
                mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Mostra l'esercizio corrente sull'immagine
            cv2.putText(frame, f"Esercizio: {exercise_name}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Data Collection', frame)

            # Premi 'q' per uscire
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

        # Salva i dati in un file CSV separato per ogni esercizio
        df = pd.DataFrame(data)
        # Creazione dei nomi delle colonne per 99 caratteristiche + label
        column_names = [f'landmark_{i}_{axis}' for i in range(33) for axis in ['x', 'y', 'z']]
        column_names.append('label')
        df.columns = column_names
        df.to_csv(filename, index=False)

        print(f"Dati salvati nel file '{filename}'.")
