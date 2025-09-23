import cv2
import mediapipe as mp
import numpy as np
import joblib
import pandas as pd
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Carica il modello addestrato
model = joblib.load(r"file pkl\datireali\svm_model.pkl")

# Inizializza MediaPipe per il rilevamento della posa
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Impostazioni della videocamera
cap = cv2.VideoCapture(0)

# Esercizi
exercise_label = ["squat", "pushup", "","military press"]

# Finestra principale
root = tk.Tk()
root.title("Exercise Recognition")

# Frame per il video
video_frame = ttk.Frame(root)
video_frame.pack(pady=10)

# Canvas per visualizzare il video
video_canvas = tk.Canvas(video_frame, width=640, height=480)
video_canvas.pack()

# Frame per l'etichetta dell'esercizio riconosciuto
exercise_label_var = tk.StringVar()
exercise_label_var.set("Exercise: Not recognized")
exercise_name_label = ttk.Label(root, textvariable=exercise_label_var, font=("Arial", 16))
exercise_name_label.pack(pady=10)

# Funzione per disegnare un pallino di riconoscimento
def draw_recognition_indicator(frame):
    if exercise_label_var.get() != "Exercise: Not recognized":
        cv2.circle(frame, (630, 30), 10, (0, 255, 0), -1)
    else:
        cv2.circle(frame, (630, 30), 10, (0, 0, 255), -1)

# Ciclo principale aggiornato per visualizzare il video e riconoscere l'esercizio
def update_video():
    ret, frame = cap.read()
    if ret:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks
            keypoints = np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark]).flatten().reshape(1, -1)
            # Adjust feature names based on model's expectations (e.g., landmark_0_x, landmark_0_y, etc.)
            num_landmarks = keypoints.shape[1] // 3 #sempre 33?
            feature_names = [f"landmark_{i}_{axis}" for i in range(num_landmarks) for axis in ['x', 'y', 'z']]
            keypoints_df = pd.DataFrame(keypoints, columns=feature_names)


            exercise_class = model.predict(keypoints_df)[0]
            exercise_class = int(exercise_class)

            # Aggiorna l'etichetta del nome dell'esercizio riconosciuto
            exercise_label_var.set(f"Exercise: {exercise_label[exercise_class]}")

        # Converti l'immagine in un formato compatibile con Tkinter
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_image = Image.fromarray(frame)
        frame_image = ImageTk.PhotoImage(image=frame_image)
        video_canvas.create_image(0, 0, anchor=tk.NW, image=frame_image)
        video_canvas.image = frame_image
        
        # Disegna il pallino di riconoscimento
        draw_recognition_indicator(frame)

    root.after(33, update_video)

# Avvio del ciclo di aggiornamento del video
update_video()

# Avvia la finestra principale
root.mainloop()
