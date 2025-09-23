import cv2
from utils.global_vars import *

def draw_landmarks(frame, landmarks):
    # Disegna i punti
    for landmark in landmarks.landmark:
        x = int(landmark.x * frame.shape[1])
        y = int(landmark.y * frame.shape[0])
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
    
    # Disegna le linee di connessione
    connections = mp_pose.POSE_CONNECTIONS
    for connection in connections:
        start_idx = connection[0]
        end_idx = connection[1]
        start_point = landmarks.landmark[start_idx]
        end_point = landmarks.landmark[end_idx]
        start_coords = (int(start_point.x * frame.shape[1]), int(start_point.y * frame.shape[0]))
        end_coords = (int(end_point.x * frame.shape[1]), int(end_point.y * frame.shape[0]))
        cv2.line(frame, start_coords, end_coords, (0, 255, 0), 2)


# Funzione per disegnare il timer sul frame
def draw_start_timer(frame, timer):
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, f'Starting in: {timer}', (50, 50), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
