import os
import pandas as pd

# --- Pfade definieren ---
base_dir = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.dirname(base_dir)
data_folder = os.path.join(project_folder, "Data")

# --- CSV-Datei laden ---
def load_csv(filename):
    return pd.read_csv(os.path.join(data_folder, filename))

merged_data = load_csv("merged_data.csv")

# --- Hilfsfunktion zur Datenerstellung ---
def create_custom_dataframe(df, group_a_prefix, group_b_prefix, new_prefix):
    output_rows = []
    for _, row in df.iterrows():
        group = row['Group']
        patient_id = row['Patient ID']
        if group == 'A':
            prefix = group_a_prefix
        elif group == 'B':
            prefix = group_b_prefix
        else:
            continue

        selected_cols = {col: val for col, val in row.items() if col.startswith(prefix)}
        renamed_cols = {}

        for col, val in selected_cols.items():
            new_col = col.replace(prefix, new_prefix)

            # "_score" entfernen, aber nur bei bestimmten Spalten
            for suffix in ['total_score', 'competence_score', 'adaptability_score', 'self_esteem_score']:
                if new_col.endswith(f"_{suffix}"):
                    new_col = new_col.replace(f"_{suffix}", f"_{suffix.replace('_score','')}")
            renamed_cols[new_col] = val

        # Sicherstellen, dass Patient ID die erste Spalte ist
        row_dict = {'Patient ID': patient_id}
        row_dict.update(renamed_cols)
        output_rows.append(row_dict)

    return pd.DataFrame(output_rows)

# --- Daten aufteilen ---
bro_data = create_custom_dataframe(merged_data, 'M1_', 'M2_', 'BRO_')
permobil_data = create_custom_dataframe(merged_data, 'M2_', 'M1_', 'Permobil_')

# --- Speichern der Dateien ---
output_files = {
    "bro_data.xlsx": bro_data.to_excel,
    "bro_data.csv": lambda path: bro_data.to_csv(path, index=False, sep=","),
    "permobil_data.xlsx": permobil_data.to_excel,
    "permobil_data.csv": lambda path: permobil_data.to_csv(path, index=False, sep=",")
}

os.makedirs(data_folder, exist_ok=True)
for filename, save_func in output_files.items():
    output_path = os.path.join(data_folder, filename)
    if filename.endswith(".xlsx"):
        save_func(output_path, index=False)
    else:
        save_func(output_path)
    print(f"The file was saved in the 'Data' folder ({output_path})")
