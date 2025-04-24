import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import re

# === Daten laden ===
base_dir = os.path.dirname(os.path.abspath(__file__))

def load_csv(filename):
    file_path = os.path.join(base_dir, "../Data", filename)
    return pd.read_csv(file_path)

df = load_csv("merged_data.csv")

color_map = {'BRO': (0/255, 165/255, 249/255), 'Permobil M3': (169/255, 169/255, 169/255)}

# === Gruppierte Barplots für Aufgaben 1–6 mit korrekt zugewiesenen Scores ===

fig, axs = plt.subplots(3, 2, figsize=(12, 10))  # 3 Zeilen, 2 Spalten
axs = axs.flatten()

# Funktion zur Extraktion gemäß korrekter Logik
def extract_scores_correct_by_group(row, task_num, version_label):
    if version_label == 'BRO':
        if row['Group'] == 'A':
            return [row[col] for col in df.columns if col.startswith(f"M1_{task_num}.") and col.endswith("_score")]
        elif row['Group'] == 'B':
            return [row[col] for col in df.columns if col.startswith(f"M2_{task_num}.") and col.endswith("_score")]
    elif version_label == 'Permobil M3':
        if row['Group'] == 'A':
            return [row[col] for col in df.columns if col.startswith(f"M2_{task_num}.") and col.endswith("_score")]
        elif row['Group'] == 'B':
            return [row[col] for col in df.columns if col.startswith(f"M1_{task_num}.") and col.endswith("_score")]
    return []

# Schritt 1: Daten sammeln & globales y-Maximum berechnen
score_data_per_task = []
global_max = 0

for task_num in range(1, 7):
    bro_rows = []
    m3_rows = []

    for _, row in df.iterrows():
        bro_rows.extend([{'Score': s, 'Version': 'BRO'} for s in extract_scores_correct_by_group(row, task_num, 'BRO') if pd.notna(s)])
        m3_rows.extend([{'Score': s, 'Version': 'Permobil M3'} for s in extract_scores_correct_by_group(row, task_num, 'Permobil M3') if pd.notna(s)])

    all_scores = pd.DataFrame(bro_rows + m3_rows)
    all_scores['Score'] = all_scores['Score'].astype(int)

    score_counts = all_scores.groupby(['Score', 'Version']).size().unstack(fill_value=0)
    for version in ['BRO', 'Permobil M3']:
        if version not in score_counts.columns:
            score_counts[version] = 0
    score_counts = score_counts.reindex([1, 2, 3], fill_value=0)

    global_max = max(global_max, score_counts.values.max())
    score_data_per_task.append((task_num, score_counts))

# Neue Titel definieren
combined_task_titles = [
    "Einstellungen",
    "Manövrierfähigkeit / Beweglichkeit",
    "Alltagssituationen in der Küche",
    "Steigung",
    "Bordsteinkanten",
    "Treppe"
]

# Schritt 2: Plots erstellen mit einheitlicher y-Achse
for i, (task_num, score_counts) in enumerate(score_data_per_task):
    ax = axs[i]
    width = 0.35
    x = np.arange(len(score_counts.index))

    # Balken zeichnen
    bars_bro = ax.bar(x - width/2, score_counts['BRO'], width, label='BRO', color=color_map['BRO'])
    bars_m3 = ax.bar(x + width/2, score_counts['Permobil M3'], width, label='Permobil M3', color=color_map['Permobil M3'])

    # Mittelwertberechnung
    bro_total = sum(score * count for score, count in zip(score_counts.index, score_counts['BRO']))
    bro_n = score_counts['BRO'].sum()
    mean_bro = bro_total / bro_n if bro_n > 0 else 0

    m3_total = sum(score * count for score, count in zip(score_counts.index, score_counts['Permobil M3']))
    m3_n = score_counts['Permobil M3'].sum()
    mean_m3 = m3_total / m3_n if m3_n > 0 else 0

    # Angepasster Titel
    ax.set_title(combined_task_titles[i], fontsize=11)

    # Achsen
    ax.set_xticks(x)
    ax.set_xticklabels(['Fail (1)', 'Partial Pass (2)', 'Pass (3)'], fontsize=10)
    ax.set_ylim(0, global_max + 3)
    ax.set_yticks(list(range(0, global_max + 5, 5)))
    ax.set_ylabel('Anzahl', fontsize=10)
    ax.grid(True, axis='y', linestyle='--', linewidth=0.5)

    # Balkenbeschriftung
    for bar in bars_bro + bars_m3:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, height + 0.3, f"{int(height)}", ha='center', va='bottom', fontsize=9)

    # Legende mit Mittelwerten
    ax.legend(
        [f'BRO (Ø={mean_bro:.2f})', f'Permobil M3 (Ø={mean_m3:.2f})'],
        loc='upper left',
        fontsize=9
    )

# Beschriftung unten rechts
axs[-1].set_xlabel('Score', fontsize=10)
plt.tight_layout()
output_path = os.path.join(base_dir, "../Output", "task1to6_score_grouped_barplot_corrected.png")
plt.savefig(output_path, dpi=300)
plt.close()

print(f"KORREKTER Score-Barplot (BRO vs. Permobil M3) mit Mittelwerten gespeichert unter: {output_path}")

# ---------------------------------------------------------------------------------------------------------------------------

# Alle Aufgaben einzeln darstellen
titles_ordered = [
    "Transfer", "Sitzeinstellungen", "Zum Start", "Korridor", "Slalom", "180° Drehung",
    "Rückwärtsfahren", "Tür öffnen", "Hände waschen", "Objekt erreichen", "An den Tisch setzen", "Tür schliessen",
    "5° Steigung hoch", "5° Steigung runter", "15° Steigung hoch", "15° Steigung runter",
    "Bordsteinkante hoch", "Bordsteinkante runter", "Treppe hoch", "Treppe runter"
]

# === Subtasks extrahieren und filtern ===
score_columns = [col for col in df.columns if col.endswith('_score') and (col.startswith('M1_') or col.startswith('M2_'))]
subtask_pattern = re.compile(r'^\d+\.\d+$')
valid_subtasks = set()

for col in score_columns:
    part = col.split('_')[1].replace('_score', '')
    if subtask_pattern.match(part):
        valid_subtasks.add(part)

subtasks = sorted(valid_subtasks, key=lambda x: list(map(int, x.split('.'))))
assert len(subtasks) == len(titles_ordered), "Anzahl der Titel stimmt nicht mit den Subtasks überein!"

# === Plot-Layout definieren ===
n_subtasks = len(subtasks)
n_cols = 3
n_rows = (n_subtasks + n_cols - 1) // n_cols

fig, axs = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
axs = axs.flatten()

global_max = 0
score_data_per_subtask = []

# === Scores extrahieren und berechnen ===
for subtask in subtasks:
    bro_scores, m3_scores = [], []

    for _, row in df.iterrows():
        bro_col = f"M1_{subtask}_score" if row['Group'] == 'A' else f"M2_{subtask}_score"
        if bro_col in row and pd.notna(row[bro_col]):
            bro_scores.append({'Score': int(row[bro_col]), 'Version': 'BRO'})

        m3_col = f"M2_{subtask}_score" if row['Group'] == 'A' else f"M1_{subtask}_score"
        if m3_col in row and pd.notna(row[m3_col]):
            m3_scores.append({'Score': int(row[m3_col]), 'Version': 'Permobil M3'})

    all_scores = pd.DataFrame(bro_scores + m3_scores)
    score_counts = all_scores.groupby(['Score', 'Version']).size().unstack(fill_value=0)
    for version in ['BRO', 'Permobil M3']:
        if version not in score_counts.columns:
            score_counts[version] = 0
    score_counts = score_counts.reindex([1, 2, 3], fill_value=0)
    score_data_per_subtask.append(score_counts)
    global_max = max(global_max, score_counts.values.max())

# === Plotten ===
for ax, subtask, score_counts, title in zip(axs, subtasks, score_data_per_subtask, titles_ordered):
    x = np.arange(len(score_counts.index))
    width = 0.35

    bars_bro = ax.bar(x - width/2, score_counts['BRO'], width, label='BRO', color=color_map['BRO'])
    bars_m3 = ax.bar(x + width/2, score_counts['Permobil M3'], width, label='Permobil M3', color=color_map['Permobil M3'])

    mean_bro = (score_counts['BRO'] * score_counts.index).sum() / score_counts['BRO'].sum() if score_counts['BRO'].sum() > 0 else 0
    mean_m3 = (score_counts['Permobil M3'] * score_counts.index).sum() / score_counts['Permobil M3'].sum() if score_counts['Permobil M3'].sum() > 0 else 0

    ax.set_title(f"{title} – BRO (Ø={mean_bro:.2f}), M3 (Ø={mean_m3:.2f})", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(['Fail (1)', 'Partial Pass (2)', 'Pass (3)'])
    ax.set_ylim(0, global_max + 3)
    ax.grid(True, axis='y', linestyle='--', linewidth=0.5)

    for bar in bars_bro + bars_m3:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, height + 0.3, f"{int(height)}", ha='center', va='bottom', fontsize=8)

# Leere Achsen ausblenden
for ax in axs[len(score_data_per_subtask):]:
    ax.axis('off')

# === Speichern ===
plt.tight_layout()
output_path = os.path.join(base_dir, "../Output", "subtask_detailed_grouped_barplots_named.png")
plt.savefig(output_path, dpi=300)
plt.close()