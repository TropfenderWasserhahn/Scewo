import pandas as pd
import os
import re

# --- Pfade definieren ---
base_dir = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.dirname(base_dir)
data_folder = os.path.join(project_folder, "Data")

# --- CSV-Dateien automatisch laden ---
def load_all_icf_files():
    pattern = re.compile(r"P\d{2}_M[12]_ICF_linking.*\.csv", re.IGNORECASE)
    all_files = [f for f in os.listdir(data_folder) if pattern.match(f)]
    all_dataframes = []

    for filename in sorted(all_files):
        filepath = os.path.join(data_folder, filename)
        try:
            df = pd.read_csv(filepath)
            all_dataframes.append(df)
            print(f"Geladen: {filename}")
        except Exception as e:
            print(f"Fehler beim Laden von {filename}: {e}")

    if not all_dataframes:
        raise FileNotFoundError("Keine passenden ICF-Dateien gefunden.")

    return pd.concat(all_dataframes, ignore_index=True)

# --- Daten zusammenführen ---
merged_ICF = load_all_icf_files()

# --- Mutterdatei speichern ---
output_files = {
    "merged_ICF.xlsx": merged_ICF.to_excel,
    "merged_ICF.csv": lambda path: merged_ICF.to_csv(path, index=False, sep=",")
}

os.makedirs(data_folder, exist_ok=True)
for filename, save_func in output_files.items():
    output_path = os.path.join(data_folder, filename)
    if filename.endswith(".xlsx"):
        save_func(output_path, index=False)
    else:
        save_func(output_path)
    print(f"Die Datei wurde gespeichert: {output_path}")
