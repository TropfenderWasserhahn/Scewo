import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import re

# === Constants ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COLOR_MAP = {'BRO': (0/255, 165/255, 249/255), 'Permobil M3': (169/255, 169/255, 169/255)}
SCORE_RANGE = range(1, 8)
BAR_WIDTH = 0.4

# === Helper Functions ===
def load_csv(filename):
    return pd.read_csv(os.path.join(BASE_DIR, "../Data", filename))

def calculate_mean(value_counts):
    """Calculate the mean score from value counts."""
    scores = np.array(value_counts.index)
    freq = value_counts.values
    return (scores * freq).sum() / freq.sum() if freq.sum() > 0 else 0

def extract_metric_values(df, metric_suffix, task_labels):
    """Extract EOU or effort values with correct M1/M2 mapping based on group."""
    records = []
    for _, row in df.iterrows():
        for task in task_labels:
            for version in ['BRO', 'Permobil M3']:
                prefix = "M1_" if (row['Group'] == 'A' and version == 'BRO') or (row['Group'] == 'B' and version == 'Permobil M3') else "M2_"
                col_name = f"{prefix}{task}_{metric_suffix}"
                if col_name in df.columns and pd.notna(row[col_name]):
                    records.append({
                        'Task': task,
                        'Score': int(row[col_name]),
                        'Version': version
                    })
    return pd.DataFrame(records)

def plot_eou_effort_paired(data_eou, data_effort, task_labels, output_file):
    paired_tasks = [task_labels[i:i+2] for i in range(0, len(task_labels), 2)]
    num_pairs = len(paired_tasks)
    fig, axs = plt.subplots(num_pairs, 2, figsize=(14, 3 * num_pairs))
    axs = axs.reshape(-1, 2)

    for row_idx, task_pair in enumerate(paired_tasks):
        for i, task in enumerate(task_pair):
            for col_idx, (metric_data, metric_label) in enumerate(zip([data_eou, data_effort], ['Benutzerfreundlichkeit', 'Anstrengung'])):
                ax = axs[row_idx][col_idx]
                subset = metric_data[metric_data['Task'] == task]
                if subset.empty:
                    continue

                mean_vals = {}
                for j, version in enumerate(['BRO', 'Permobil M3']):
                    values = subset[subset['Version'] == version]['Score']
                    counts = values.value_counts().reindex(SCORE_RANGE, fill_value=0).sort_index()
                    scores = np.array(counts.index)
                    freq = counts.values
                    mean_vals[version] = (scores * freq).sum() / freq.sum() if freq.sum() > 0 else 0
                    x = [s + (j - 0.5) * BAR_WIDTH for s in SCORE_RANGE]
                    ax.bar(x, freq, width=BAR_WIDTH, label=f"{version} (Ø={mean_vals[version]:.2f})", color=COLOR_MAP[version])

                ax.set_title(f"{metric_label} – Aufgabe {task}")
                ax.set_xlim(0.5, 7.5)
                ax.set_ylim(0, max(freq.max(), 1) + 1)
                ax.set_xticks(SCORE_RANGE)
                ax.set_xlabel('Score')
                ax.set_ylabel('Anzahl')
                ax.grid(True, axis='y', linestyle='--', linewidth=0.5)
                ax.legend(loc='upper left', fontsize=9)

        if len(task_pair) == 1:
            axs[row_idx][1].axis('off')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

# === Main Logic ===
df = load_csv("merged_data.csv")

# Tasks extrahieren
eou_columns = [col for col in df.columns if col.endswith('_EOU')]
effort_columns = [col for col in df.columns if col.endswith('_effort')]
task_pattern = re.compile(r'^[Mm][12]_(\d+\.\d+)_')

task_labels = sorted({
    match.group(1)
    for col in eou_columns + effort_columns
    if (match := task_pattern.match(col))
}, key=lambda x: list(map(int, x.split('.'))))

# EOU und Effort extrahieren
eou_df = extract_metric_values(df, 'EOU', task_labels)
effort_df = extract_metric_values(df, 'effort', task_labels)

# Plot erstellen
output_path = os.path.join(BASE_DIR, "../Output", "eou_effort_grouped_barplots_combined.png")
plot_eou_effort_paired(eou_df, effort_df, task_labels, output_path)

print(f"EOU + Effort Diagramm gespeichert unter: {output_path}")
