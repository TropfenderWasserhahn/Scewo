import pandas as pd
import os

# Define paths
base_dir = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.dirname(base_dir)
data_folder = os.path.join(project_folder, "Data")

# Helper function to load CSV files
def load_csv(filename):
    return pd.read_csv(os.path.join(data_folder, filename))

# Load data
data_files = ["M1.csv", "M2.csv", "Screening.csv", "PIADS.csv", "Interview.csv"]
measurement_data_M1, measurement_data_M2, screening_data, piads_data, interview_data = map(load_csv, data_files)
print("CSV-files loaded successfully!")

# Merge dataframes based on prefixes
def merge_data(base_df, dfs, prefixes, id_col="Patient ID"):
    for prefix in prefixes:
        for df in dfs:
            selected_cols = [id_col] + [col for col in df.columns if col.startswith(prefix)]
            if len(selected_cols) > 1:  # Merge only if columns with the prefix exist
                base_df = pd.merge(base_df, df[selected_cols], on=id_col, how="left")
    return base_df

# Merge all data into the screening data
merged_data = merge_data(screening_data, [measurement_data_M1, measurement_data_M2, interview_data, piads_data], ["M1_", "M2_"])

# Save merged data to Excel and CSV
output_files = {
    "merged_data.xlsx": merged_data.to_excel,
    "merged_data.csv": lambda path: merged_data.to_csv(path, index=False, sep=",")
}

os.makedirs(data_folder, exist_ok=True)
for filename, save_func in output_files.items():
    output_path = os.path.join(data_folder, filename)
    if filename.endswith(".xlsx"):
        save_func(output_path, index=False)
    else:
        save_func(output_path)
    print(f"The file was saved in the 'Data' folder ({output_path})")