import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
import numpy as np
import re
from math import ceil

# === Constants ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COLOR_MAP = {'BRO': (0/255, 165/255, 249/255), 'Permobil M3': (169/255, 169/255, 169/255)}
COMBINED_TITLES = [
    "Einstellungen", "Manövrierfähigkeit / Beweglichkeit", "Alltagssituationen in der Küche",
    "Steigung", "Bordsteinkanten", "Treppe"
]
DETAILED_TITLES = [
    "Transfer", "Sitzeinstellungen", "Zum Start", "Korridor", "Slalom", "180° Drehung",
    "Rückwärtsfahren", "Tür öffnen", "Hände waschen", "Objekt erreichen", "An den Tisch setzen", "Tür schliessen",
    "5° Steigung hoch", "5° Steigung runter", "15° Steigung hoch", "15° Steigung runter",
    "Bordsteinkante hoch", "Bordsteinkante runter", "Treppe hoch", "Treppe runter"
]

# === Helper Functions ===
def load_csv(filename):
    return pd.read_csv(os.path.join(BASE_DIR, "../Data", filename))

def extract_scores(row, task_num, version_label):
    prefix = "M1_" if (row['Group'] == 'A' and version_label == 'BRO') or (row['Group'] == 'B' and version_label == 'Permobil M3') else "M2_"
    return [row[col] for col in df.columns if col.startswith(f"{prefix}{task_num}.") and col.endswith("_score") and pd.notna(row[col])]

def calculate_mean(score_counts, version):
    total = (score_counts[version] * score_counts.index).sum()
    count = score_counts[version].sum()
    return total / count if count > 0 else 0

def plot_bar_chart(ax, score_counts, title, global_max):
    x = np.arange(len(score_counts.index))
    width = 0.35

    mean_bro = calculate_mean(score_counts, 'BRO')
    mean_m3 = calculate_mean(score_counts, 'Permobil M3')

    bars_bro = ax.bar(x - width/2, score_counts['BRO'], width,
                      label=f'BRO (Ø={mean_bro:.2f})', color=COLOR_MAP['BRO'])
    bars_m3 = ax.bar(x + width/2, score_counts['Permobil M3'], width,
                     label=f'Permobil M3 (Ø={mean_m3:.2f})', color=COLOR_MAP['Permobil M3'])

    ax.set_title(title, fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(['No Part (0)', 'Fail (1)', 'Partial Pass (2)', 'Pass (3)'])

    # === Y-Achse: mindestens +4 und auf Tick enden ===
    minimum_ymax = global_max + 4
    locator = ticker.MaxNLocator(integer=True)
    tick_values = locator.tick_values(0, minimum_ymax)

    final_ymax = tick_values[tick_values >= minimum_ymax].min()  # nächster gültiger Tick ≥ minimum
    ax.set_ylim(0, final_ymax)
    ax.yaxis.set_major_locator(locator)

    ax.grid(True, axis='y', linestyle='--', linewidth=0.5)
    ax.legend(loc='upper left', fontsize=10)


# === Main Logic ===
df = load_csv("merged_data.csv")

# === Combined Barplots (Tasks 1–6) ===
fig, axs = plt.subplots(3, 2, figsize=(12, 10))
axs = axs.flatten()

for i, task_num in enumerate(range(1, 7)):
    bro_rows, m3_rows = [], []
    global_max = 0

    for _, row in df.iterrows():
        bro_rows.extend([{'Score': s, 'Version': 'BRO'} for s in extract_scores(row, task_num, 'BRO')])
        m3_rows.extend([{'Score': s, 'Version': 'Permobil M3'} for s in extract_scores(row, task_num, 'Permobil M3')])

    all_scores = pd.DataFrame(bro_rows + m3_rows)
    all_scores['Score'] = all_scores['Score'].astype(int)
    score_counts = all_scores.groupby(['Score', 'Version']).size().unstack(fill_value=0).reindex([0, 1, 2, 3], fill_value=0)
    global_max = max(global_max, score_counts.values.max())

    plot_bar_chart(axs[i], score_counts, COMBINED_TITLES[i], global_max)

plt.tight_layout()
output_path = os.path.join(BASE_DIR, "../Output", "task1to6_score_grouped_barplot.png")
plt.savefig(output_path, dpi=300)
plt.close()

# === Detailed Barplots (All Subtasks) ===
score_columns = [col for col in df.columns if col.endswith('_score') and (col.startswith('M1_') or col.startswith('M2_'))]
subtask_pattern = re.compile(r'^\d+\.\d+$')
subtasks = sorted({col.split('_')[1].replace('_score', '') for col in score_columns if subtask_pattern.match(col.split('_')[1])}, key=lambda x: list(map(int, x.split('.'))))

assert len(subtasks) == len(DETAILED_TITLES), "Anzahl der Titel stimmt nicht mit den Subtasks überein!"

fig, axs = plt.subplots((len(subtasks) + 2) // 3, 3, figsize=(15, 20))
axs = axs.flatten()
global_max = 0

for subtask, title, ax in zip(subtasks, DETAILED_TITLES, axs):
    bro_scores, m3_scores = [], []

    for _, row in df.iterrows():
        bro_col = f"M1_{subtask}_score" if row['Group'] == 'A' else f"M2_{subtask}_score"
        m3_col = f"M2_{subtask}_score" if row['Group'] == 'A' else f"M1_{subtask}_score"

        if bro_col in row and pd.notna(row[bro_col]):
            bro_scores.append({'Score': int(row[bro_col]), 'Version': 'BRO'})
        if m3_col in row and pd.notna(row[m3_col]):
            m3_scores.append({'Score': int(row[m3_col]), 'Version': 'Permobil M3'})

    all_scores = pd.DataFrame(bro_scores + m3_scores)
    score_counts = (
        all_scores.groupby(['Score', 'Version'])
        .size()
        .unstack(fill_value=0)
        .reindex(index=pd.Index([0, 1, 2, 3], name='Score'), fill_value=0)
)

    global_max = max(global_max, score_counts.values.max())

    plot_bar_chart(ax, score_counts, title, global_max)

for ax in axs[len(subtasks):]:
    ax.axis('off')

plt.tight_layout()
output_path = os.path.join(BASE_DIR, "../Output", "task1to6_score_ detailed_grouped_barplot.png")
plt.savefig(output_path, dpi=300)
plt.close()

# === Combined Boxplots (Tasks 1–6) ===
fig, axs = plt.subplots(3, 2, figsize=(12, 10))
axs = axs.flatten()

for i, task_num in enumerate(range(1, 7)):
    bro_scores, m3_scores = [], []

    for _, row in df.iterrows():
        bro_scores.extend(extract_scores(row, task_num, 'BRO'))
        m3_scores.extend(extract_scores(row, task_num, 'Permobil M3'))

    # Nur gültige Werte behalten
    bro_scores = [s for s in bro_scores if pd.notna(s)]
    m3_scores = [s for s in m3_scores if pd.notna(s)]

    ax = axs[i]
    box = ax.boxplot([bro_scores, m3_scores], labels=['BRO', 'Permobil M3'],
                     patch_artist=True,
                     medianprops=dict(color='black'),
                     whiskerprops=dict(color='black'),
                     capprops=dict(color='black'),
                     flierprops=dict(markerfacecolor='red', marker='o', markersize=5, linestyle='none'))

    # Farbe manuell zuweisen
    colors = [COLOR_MAP['BRO'], COLOR_MAP['Permobil M3']]
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)

    ax.set_title(COMBINED_TITLES[i], fontsize=10)
    ax.set_ylabel('Score')
    ax.set_ylim(-0.5, 3.5)
    ax.grid(True, axis='y', linestyle='--', linewidth=0.5)

plt.tight_layout()
output_path = os.path.join(BASE_DIR, "../Output", "task1to6_score_boxplots.png")
plt.savefig(output_path, dpi=300)
plt.close()