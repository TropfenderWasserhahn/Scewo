import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns

print("Module erfolgreich geladen!")

# Load data
measurement_data_M1 = pd.read_csv("Data/M1.csv")
measurement_data_M2 = pd.read_csv("Data/M2.csv")
screening_data = pd.read_csv("Data/Screening.csv")
piads_data = pd.read_csv("Data/PIADS.csv")
interview_data = pd.read_csv("Data/Interview.csv")

# Set Screening data as base
merged_data = screening_data

# List of dataframes that will be merged in correct order
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

# Sicherstellen, dass df_filtered definiert ist
df_filtered = merged_data

# **Fix: Original-Spaltennamen beibehalten**
score_columns = [col for col in merged_data.columns]

# Output-Ordner für die Plots
project_folder = os.getcwd()  
output_folder = os.path.join(project_folder, "Output")
os.makedirs(output_folder, exist_ok=True)

# **Funktion für M1 von A & M2 von B**
def save_stacked_bar_for_tasks(task_prefix, title_suffix, filename):
    task_columns = [col for col in df_filtered.columns if f"_{task_prefix}." in col]

    if not task_columns:
        print(f"⚠️ Keine passenden Spalten für Aufgabe {task_prefix}.x gefunden.")
        return None

    print(f"📝 Gefundene Spalten für Aufgabe {task_prefix}.x: {task_columns}")

    score_distribution = {col: {0: 0, 1: 0, 2: 0, 3: 0} for col in task_columns}

    for col in task_columns:
        for _, row in df_filtered.iterrows():
            score = None
            if row["Group"] == "A" and col.startswith("M1_"):  # M1 für A
                score = row[col]
            elif row["Group"] == "B" and col.startswith("M2_"):  # M2 für B
                score = row[col]

            if pd.notna(score):
                try:
                    score = int(float(score))
                    if score in score_distribution[col]:
                        score_distribution[col][score] += 1
                except ValueError:
                    print(f"⚠️ Ungültiger Wert in {col}: {score}")

    print(f"📊 Score-Verteilung für {task_prefix}.x:", score_distribution)

    score_counts_0 = [score_distribution[col][0] for col in task_columns]
    score_counts_1 = [score_distribution[col][1] for col in task_columns]
    score_counts_2 = [score_distribution[col][2] for col in task_columns]
    score_counts_3 = [score_distribution[col][3] for col in task_columns]

    fig, ax = plt.subplots(figsize=(8, 6))

    bar_width = 0.3
    ax.bar(["Aufgabe " + task_prefix + ".x"], sum(score_counts_0), label="Score 0", color="lightgray", width=bar_width)
    ax.bar(["Aufgabe " + task_prefix + ".x"], sum(score_counts_1), bottom=sum(score_counts_0), label="Score 1", color="blue", width=bar_width)
    ax.bar(["Aufgabe " + task_prefix + ".x"], sum(score_counts_2), bottom=sum(score_counts_0) + sum(score_counts_1), label="Score 2", color="orange", width=bar_width)
    ax.bar(["Aufgabe " + task_prefix + ".x"], sum(score_counts_3), bottom=sum(score_counts_0) + sum(score_counts_1) + sum(score_counts_2), label="Score 3", color="red", width=bar_width)

    plt.ylabel("Anzahl der Scores")
    #plt.xlabel(f"Aufgabe {task_prefix}.x")
    plt.title(f"Gesamtverteilung der Scores (0-3) {task_prefix}.x {title_suffix}")
    plt.legend()

    ax.yaxis.grid(True, linestyle="--", alpha=0.7)

    save_path = os.path.join(output_folder, filename)
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ Gespeichert: {save_path}")

    return save_path

# **Funktion für M2 von A & M1 von B**
def save_stacked_bar_for_tasks_switched(task_prefix, title_suffix, filename):
    task_columns = [col for col in df_filtered.columns if f"_{task_prefix}." in col]

    if not task_columns:
        print(f"⚠️ Keine passenden Spalten für Aufgabe {task_prefix}.x gefunden.")
        return None

    print(f"📝 Gefundene Spalten für Aufgabe {task_prefix}.x: {task_columns}")

    score_distribution = {col: {0: 0, 1: 0, 2: 0, 3: 0} for col in task_columns}

    for col in task_columns:
        for _, row in df_filtered.iterrows():
            score = None
            if row["Group"] == "A" and col.startswith("M2_"):  # M2 für A
                score = row[col]
            elif row["Group"] == "B" and col.startswith("M1_"):  # M1 für B
                score = row[col]

            if pd.notna(score):
                try:
                    score = int(float(score))
                    if score in score_distribution[col]:
                        score_distribution[col][score] += 1
                except ValueError:
                    print(f"⚠️ Ungültiger Wert in {col}: {score}")

    score_counts_0 = [score_distribution[col][0] for col in task_columns]
    score_counts_1 = [score_distribution[col][1] for col in task_columns]
    score_counts_2 = [score_distribution[col][2] for col in task_columns]
    score_counts_3 = [score_distribution[col][3] for col in task_columns]

    fig, ax = plt.subplots(figsize=(8, 6))

    bar_width = 0.3
    ax.bar(["Aufgabe " + task_prefix + ".x"], sum(score_counts_0), label="Score 0", color="lightgray", width=bar_width)
    ax.bar(["Aufgabe " + task_prefix + ".x"], sum(score_counts_1), bottom=sum(score_counts_0), label="Score 1", color="blue", width=bar_width)
    ax.bar(["Aufgabe " + task_prefix + ".x"], sum(score_counts_2), bottom=sum(score_counts_0) + sum(score_counts_1), label="Score 2", color="orange", width=bar_width)
    ax.bar(["Aufgabe " + task_prefix + ".x"], sum(score_counts_3), bottom=sum(score_counts_0) + sum(score_counts_1) + sum(score_counts_2), label="Score 3", color="red", width=bar_width)


    plt.ylabel("Anzahl der Scores")
    #plt.xlabel(f"Aufgabe {task_prefix}.x")
    plt.title(f"Gesamtverteilung der Scores (0-3) {task_prefix}.x {title_suffix}")
    plt.legend()

    ax.yaxis.grid(True, linestyle="--", alpha=0.7)

    save_path = os.path.join(output_folder, filename)
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ Gespeichert: {save_path}")

    return save_path

# **Jetzt beide Versionen speichern**
for task in ["1", "2", "3", "4", "5", "6"]:
    save_stacked_bar_for_tasks(task, "BRO", f"aufgabe_{task}_original.png")
    save_stacked_bar_for_tasks_switched(task, "Permobil", f"aufgabe_{task}_switched.png")

def save_histplot(column_suffix, title_suffix):
    # Spaltennamen für M1 und M2
    column_m1 = f"M1_{column_suffix}"
    column_m2 = f"M2_{column_suffix}"

    # Prüfen, ob die Spalten existieren
    if column_m1 not in df_filtered.columns or column_m2 not in df_filtered.columns:
        print(f"⚠️ Spalten {column_m1} oder {column_m2} existieren nicht in den Daten.")
        return None

    # Daten für die Kombinationen vorbereiten
    data_a_m1 = df_filtered[df_filtered["Group"] == "A"][column_m1].dropna()
    data_b_m2 = df_filtered[df_filtered["Group"] == "B"][column_m2].dropna()
    data_a_m2 = df_filtered[df_filtered["Group"] == "A"][column_m2].dropna()
    data_b_m1 = df_filtered[df_filtered["Group"] == "B"][column_m1].dropna()

    # Sicherstellen, dass es überhaupt Daten gibt
    if data_a_m1.empty and data_b_m2.empty and data_a_m2.empty and data_b_m1.empty:
        print(f"⚠️ Keine gültigen Werte für {column_suffix}.")
        return None

    # Histogramm-Einstellungen
    bin_edges = np.arange(0, 9) - 0.5  # Ganze Zahlen von 0 bis 7, mittig ausgerichtet
    bar_width = 0.8  # Abstand zwischen Balken

    # **1️⃣ M1 (A) & M2 (B) Histogramm**
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.histplot(data_a_m1, bins=bin_edges, color="blue", label="M1 (Group A)", ax=ax, multiple="dodge", shrink=0.8)
    sns.histplot(data_b_m2, bins=bin_edges, color="red", label="M2 (Group B)", ax=ax, multiple="dodge", shrink=0.8)
    
    plt.xlabel(column_suffix)
    plt.ylabel("Häufigkeit")
    plt.title(f"Histogramm für {column_suffix} (M1 von A & M2 von B) {title_suffix}")
    plt.xticks(range(0, 8))
    max_count = max(np.histogram(data_a_m1, bins=range(0, 9))[0].max(), np.histogram(data_b_m2, bins=range(0, 9))[0].max(), 1)
    plt.yticks(range(0, max_count + 1))
    ax.yaxis.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    plt.savefig(os.path.join(output_folder, f"hist_{column_suffix}_M1A_M2B.png"), dpi=300, bbox_inches="tight")
    plt.close()

    # **2️⃣ M2 (A) & M1 (B) Histogramm**
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.histplot(data_a_m2, bins=bin_edges, color="green", label="M2 (Group A)", ax=ax, multiple="dodge", shrink=0.8)
    sns.histplot(data_b_m1, bins=bin_edges, color="purple", label="M1 (Group B)", ax=ax, multiple="dodge", shrink=0.8)

    plt.xlabel(column_suffix)
    plt.ylabel("Häufigkeit")
    plt.title(f"Histogramm für {column_suffix} (M2 von A & M1 von B) {title_suffix}")
    plt.xticks(range(0, 8))
    max_count = max(np.histogram(data_a_m2, bins=range(0, 9))[0].max(), np.histogram(data_b_m1, bins=range(0, 9))[0].max(), 1)
    plt.yticks(range(0, max_count + 1))
    ax.yaxis.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    plt.savefig(os.path.join(output_folder, f"hist_{column_suffix}_M2A_M1B.png"), dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Histogramme für {column_suffix} gespeichert!")

# **Erstelle Histogramme für SSI_3, SSI_9, SSI_10**
hist_columns = ["SSI_3", "SSI_9", "SSI_10"]
for col in hist_columns:
    save_histplot(col, "Histogramm")