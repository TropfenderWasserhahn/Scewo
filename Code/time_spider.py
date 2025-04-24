import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import re

# === Constants ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COLOR_MAP = {'BRO': (0/255, 165/255, 249/255), 'Permobil M3': (169/255, 169/255, 169/255)}
DETAILED_TITLES = [
    "Transfer", "Sitzeinstellungen", "Zum Start", "Korridor", "Slalom", "180° Drehung",
    "Rückwärtsfahren", "Tür öffnen", "Hände waschen", "Objekt erreichen", "An den Tisch setzen", "Tür schliessen",
    "5° Steigung hoch", "5° Steigung runter", "15° Steigung hoch", "15° Steigung runter",
    "Bordsteinkante hoch", "Bordsteinkante runter", "Treppe hoch", "Treppe runter"
]

# === Helper Functions ===
def load_csv(filename):
    return pd.read_csv(os.path.join(BASE_DIR, "../Data", filename))

def extract_time(row, task_num, version_label):
    prefix = "M1_" if (row['Group'] == 'A' and version_label == 'BRO') or (row['Group'] == 'B' and version_label == 'Permobil M3') else "M2_"
    return [row[col] for col in df.columns if col.startswith(f"{prefix}{task_num}.") and col.endswith("_time") and pd.notna(row[col])]

def calculate_mean(score_counts, version):
    total = (score_counts[version] * score_counts.index).sum()
    count = score_counts[version].sum()
    return total / count if count > 0 else 0

def spider_chart(df, detailed_titles, color_map, save_path=None):
    # === Subtasks extrahieren ===
    time_columns = [col for col in df.columns if col.endswith('_time') and (col.startswith('M1_') or col.startswith('M2_'))]
    subtask_pattern = re.compile(r'^\d+\.\d+$')
    subtasks = sorted(
        {col.split('_')[1].replace('_time', '') for col in time_columns if subtask_pattern.match(col.split('_')[1])},
        key=lambda x: list(map(int, x.split('.')))
    )

    assert len(subtasks) == len(detailed_titles), "Mismatch: Anzahl der Subtasks entspricht nicht den Titeln."

    mean_times_bro = []
    mean_times_m3 = []

    for subtask in subtasks:
        bro_values, m3_values = [], []

        for _, row in df.iterrows():
            bro_col = f"M1_{subtask}_time" if row['Group'] == 'A' else f"M2_{subtask}_time"
            m3_col = f"M2_{subtask}_time" if row['Group'] == 'A' else f"M1_{subtask}_time"

            if bro_col in row and pd.notna(row[bro_col]):
                bro_values.append(float(row[bro_col]))
            if m3_col in row and pd.notna(row[m3_col]):
                m3_values.append(float(row[m3_col]))

        mean_times_bro.append(np.mean(bro_values) if bro_values else 0)
        mean_times_m3.append(np.mean(m3_values) if m3_values else 0)

    # === Spider Chart erstellen ===
    num_vars = len(detailed_titles)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # Schleife schließen
    mean_times_bro += [mean_times_bro[0]]
    mean_times_m3 += [mean_times_m3[0]]
    angles += [angles[0]]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    ax.plot(angles, mean_times_bro, linewidth=2, label='BRO', color=color_map['BRO'])
    ax.fill(angles, mean_times_bro, alpha=0.25, color=color_map['BRO'])

    ax.plot(angles, mean_times_m3, linewidth=2, label='Permobil M3', color=color_map['Permobil M3'])
    ax.fill(angles, mean_times_m3, alpha=0.25, color=color_map['Permobil M3'])

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), detailed_titles)
    ax.set_title("Ø Zeit pro Aufgabe – BRO vs. Permobil M3", size=14, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300)
        plt.close()
    else:
        plt.show()


# === Main Logic ===
df = load_csv("merged_data.csv")
save_path=os.path.join(BASE_DIR, "../Output", "spider_time_chart.png")
spider_chart(df, DETAILED_TITLES, COLOR_MAP, save_path)