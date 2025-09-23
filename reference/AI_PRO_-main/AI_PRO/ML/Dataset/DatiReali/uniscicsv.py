import pandas as pd

# Percorsi dei file CSV
file1_path = r"dataset\datiReali\mil_press_data.csv"
file2_path = r"dataset\datiReali\pushup_data.csv"
file3_path = r"dataset\datiReali\squat_data.csv"

# Caricamento dei file CSV in DataFrame
df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)
df3 = pd.read_csv(file3_path)

# Unione dei DataFrame
merged_df = pd.concat([df1, df2, df3], ignore_index=True)

# Salva il DataFrame unito in un nuovo file CSV
merged_df.to_csv(r"dataset\datiReali\merged_data.csv", index=False)

print("File CSV uniti con successo!")