# This is the main file for data analysis

"""
The script needs the following packages to be installed in a virtual environment:
- pandas
- numpy
- matplotlib
- os
- openpyxl
In the terminal, navigate to the folder where this file is located and run the following command:
pip install pandas numpy matplotlib openpyxl
This will install the required packages in the virtual environment.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Define path and function to load data
base_dir = os.path.dirname(os.path.abspath(__file__))
def load_csv(filename):
    file_path = os.path.join(base_dir, "../Data", filename)
    return pd.read_csv(file_path)

# Load data
measurement_data_M1 = load_csv("M1.csv")
measurement_data_M2 = load_csv("M2.csv")
screening_data = load_csv("Screening.csv")
piads_data = load_csv("PIADS.csv")
interview_data = load_csv("Interview.csv")
print("CSV-files loaded successfully!")

"""
Merge all data to Screening data so the merged DataFrame will have to following order:
- Screening ¦ Measurement M1 ¦ Interview M1 ¦ PIADS M1 ¦ Measurement M2 ¦ Interview M2 ¦ PIADS M2
- The 'Patient ID' is the unique identifier for the data
- The randomization is set in the Screening dataframe
- The prefixes 'M1_' and 'M2_' are the identifiers for the measurementscores and -times 
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

# Path to the project-folder (one level above the code-folder)
project_folder = os.path.dirname(os.path.dirname(__file__))

# Define the output-folder in the project-folder
output_folder = os.path.join(project_folder, "Output")

# Make the folder if it does not exist
os.makedirs(output_folder, exist_ok=True)

# Path for the excel-file in the output-folder
output_path = os.path.join(output_folder, "merged_data.xlsx")

# Save the merged data to an excel-file
merged_data.to_excel(output_path, index=False)

print(f"The excel-file was saved in the 'Output' folder ({output_path})")

# Path for the csv-file in the output-folder
output_csv_path = os.path.join(output_folder, "merged_data.csv")

# Save the merged data to an csv-file
merged_data.to_csv(output_csv_path, index=False, sep=",")

print(f"The CSV-file was saved in the 'Output' folder ({output_csv_path})")