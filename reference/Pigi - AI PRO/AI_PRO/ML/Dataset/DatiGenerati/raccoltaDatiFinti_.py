import numpy as np
import pandas as pd

# Numero di esempi sintetici per esercizio
num_examples = 500

# Funzione migliorata per generare pose sintetiche
def generate_pose_with_angles(angle_hip, angle_knee, angle_ankle, angle_shoulder, angle_elbow, angle_wrist, label, noise_level=0.01):
    num_landmarks = 33
    base_pose = np.zeros((num_landmarks, 3))  # Crea un array per 33 landmarks (x, y, z)
    
    # Posizione di base del bacino (punto centrale)
    base_pose[0, :] = [0.5, 0.5, 0.5]
    
    # Simulazione per la parte inferiore del corpo
    hip_offset = np.random.uniform(-5, 5)
    knee_offset = np.random.uniform(-5, 5)
    ankle_offset = np.random.uniform(-5, 5)
    
    # Fianchi
    base_pose[11] = base_pose[0] + [0.1 * np.cos(np.radians(angle_hip + hip_offset)), 
                                    0.2 * np.sin(np.radians(angle_hip + hip_offset)), 
                                    -0.1]
    base_pose[12] = base_pose[0] + [-0.1 * np.cos(np.radians(angle_hip + hip_offset)), 
                                    0.2 * np.sin(np.radians(angle_hip + hip_offset)), 
                                    -0.1]
    
    # Ginocchia
    base_pose[13] = base_pose[11] + [0.2 * np.cos(np.radians(angle_knee + knee_offset)), 
                                     0.3 * np.sin(np.radians(angle_knee + knee_offset)), 
                                     -0.1]
    base_pose[14] = base_pose[12] + [-0.2 * np.cos(np.radians(angle_knee + knee_offset)), 
                                     0.3 * np.sin(np.radians(angle_knee + knee_offset)), 
                                     -0.1]
    
    # Caviglie
    base_pose[15] = base_pose[13] + [0.15 * np.cos(np.radians(angle_ankle + ankle_offset)), 
                                     0.1 * np.sin(np.radians(angle_ankle + ankle_offset)), 
                                     -0.2]
    base_pose[16] = base_pose[14] + [-0.15 * np.cos(np.radians(angle_ankle + ankle_offset)), 
                                     0.1 * np.sin(np.radians(angle_ankle + ankle_offset)), 
                                     -0.2]
    
    # Simulazione per la parte superiore del corpo
    shoulder_offset = np.random.uniform(-3, 3)
    elbow_offset = np.random.uniform(-3, 3)
    wrist_offset = np.random.uniform(-3, 3)
    
    # Spalle
    base_pose[23] = base_pose[0] + [0.15 * np.cos(np.radians(angle_shoulder + shoulder_offset)), 
                                    0.4, 
                                    0.1]
    base_pose[24] = base_pose[0] + [-0.15 * np.cos(np.radians(angle_shoulder + shoulder_offset)), 
                                    0.4, 
                                    0.1]
    
    # Gomiti
    base_pose[25] = base_pose[23] + [0.2 * np.cos(np.radians(angle_elbow + elbow_offset)), 
                                     0.2 * np.sin(np.radians(angle_elbow + elbow_offset)), 
                                     0]
    base_pose[26] = base_pose[24] + [-0.2 * np.cos(np.radians(angle_elbow + elbow_offset)), 
                                     0.2 * np.sin(np.radians(angle_elbow + elbow_offset)), 
                                     0]
    
    # Polsi
    base_pose[27] = base_pose[25] + [0.1 * np.cos(np.radians(angle_wrist + wrist_offset)), 
                                     0.1 * np.sin(np.radians(angle_wrist + wrist_offset)), 
                                     0]
    base_pose[28] = base_pose[26] + [-0.1 * np.cos(np.radians(angle_wrist + wrist_offset)), 
                                     0.1 * np.sin(np.radians(angle_wrist + wrist_offset)), 
                                     0]

    # Appiattisci e aggiungi rumore
    flat_pose = base_pose.flatten()
    noise = np.random.normal(0, noise_level, flat_pose.shape)
    synthetic_pose = flat_pose + noise
    
    # Aggiungi la label alla posa
    return np.append(synthetic_pose, label)

# Lista per contenere i dati sintetici
data = []

# Genera i dati sintetici per ogni esercizio
for _ in range(num_examples):
    # Esercizi con pose più realistiche
    squat_pose = generate_pose_with_angles(angle_hip=60, angle_knee=90, angle_ankle=15, angle_shoulder=0, angle_elbow=180, angle_wrist=0, label=0)  # Squat
    pushup_pose = generate_pose_with_angles(angle_hip=0, angle_knee=160, angle_ankle=90, angle_shoulder=45, angle_elbow=90, angle_wrist=0, label=1)  # Pushup
    curl_pose = generate_pose_with_angles(angle_hip=0, angle_knee=180, angle_ankle=90, angle_shoulder=10, angle_elbow=45, angle_wrist=0, label=2)    # Bicep Curl
    
    # Aggiungi ciascuna pose ai dati
    data.append(squat_pose)
    data.append(pushup_pose)
    data.append(curl_pose)

# Crea un DataFrame con i dati sintetici
df = pd.DataFrame(data)

# Imposta i nomi delle colonne per chiarezza (99 caratteristiche + 1 label)
columns = [f"feature_{i+1}" for i in range(99)]
columns.append('label')

df.columns = columns

# Salva il dataframe come CSV
df.to_csv('pose_data_realistic_99_features_500_piu_realistico.csv', index=False)

print("Dati sintetici più realistici generati e salvati in 'pose_data_realistic_99_features_500.csv'")
