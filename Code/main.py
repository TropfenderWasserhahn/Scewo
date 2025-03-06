# This is the main file for data analysis

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
print("Module erfolgreich geladen!")

x = int(input("Zahl: "))

# Load data
measurement_data_M1 = pd.read_csv("Data/M1.csv")
measurement_data_M2 = pd.read_csv("Data/M2.csv")
screening_data = pd.read_csv("Data/Screening.csv")
piads_data = pd.read_csv("Data/PIADS.csv")
interview_data = pd.read_csv("Data/Interview.csv")

# Data exploration (just for first visualisation, will be deleted later)
def data_exploration(data):
    print(data.head(10))
    print(data.shape)
    print(data.columns)
    print(data.info())
    print(data.describe())
    print(data.isna().sum())
    print('############################################################')

"""
Merge all data to Screening data so the merged DataFrame will have to following order:
Screening ¦ Measurement M1 ¦ Interview M1 ¦ PIADS M1 ¦ Measurement M2 ¦ Interview M2 ¦ PIADS M2
The 'Patient ID' is the unique identifier for the data
The randomization is set in the Screening dataframe
The prefixes 'M1_' and 'M2_' are the identifiers for the measurementscores and -times 
"""

# Set Screening data as base
merged_data = screening_data
# List of dataframes that wil be merged in correct order
dfs = [measurement_data_M1, measurement_data_M2, interview_data, piads_data]
# Function for selective merging according to prefix M1_ or M2_
def merge_selected_columns(df_base, dfs, prefix, id_col):
    for df in dfs:
        selected_cols = [id_col] + [col for col in df.columns if col.startswith(prefix)]
        if len(selected_cols) > 1:  # Nur mergen, wenn Spalten mit dem Präfix existieren
            df_base = pd.merge(df_base, df[selected_cols], on=id_col, how="left")
    return df_base

# Merge all columns from the dataframes that start with 'M1_'
merged_data = merge_selected_columns(merged_data, dfs, "M1_", "Patient ID")

# Merge all columns from the dataframes that start with 'M2_'
merged_data = merge_selected_columns(merged_data, dfs, "M2_", "Patient ID")

data_exploration(merged_data)

# Der Pfad zum Projektordner (eine Ebene höher vom Code-Ordner)
project_folder = os.path.dirname(os.path.dirname(__file__))

# Der Output-Ordner im Projektordner
output_folder = os.path.join(project_folder, "Output")

# Wenn der Ordner noch nicht existiert, erstelle ihn
os.makedirs(output_folder, exist_ok=True)

# Pfad für die Excel-Datei im Output-Ordner
output_path = os.path.join(output_folder, "merged_data.xlsx")

# Speichern des gemergten DataFrames als Excel-Datei
merged_data.to_excel(output_path, index=False)

print(f"Die Datei wurde im Output-Ordner gespeichert: {output_path}")