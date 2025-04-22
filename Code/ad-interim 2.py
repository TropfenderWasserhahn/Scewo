import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# === Daten laden ===
base_dir = os.path.dirname(os.path.abspath(__file__))

def load_csv(filename):
    file_path = os.path.join(base_dir, "../Output", filename)
    return pd.read_csv(file_path)

df = load_csv("merged_data.csv")

# === Set 1: A → M1, B → M2 | Set 2: A → M2, B → M1 ===
scores_set1 = df.apply(lambda row: pd.Series({
    'total_score': row.get('M1_total_score') if row['Group'] == 'A' else row.get('M2_total_score'),
    'competence_score': row.get('M1_competence_score') if row['Group'] == 'A' else row.get('M2_competence_score'),
    'adaptability_score': row.get('M1_adaptability_score') if row['Group'] == 'A' else row.get('M2_adaptability_score'),
    'self_esteem_score': row.get('M1_self_esteem_score') if row['Group'] == 'A' else row.get('M2_self_esteem_score')
}), axis=1)
scores_set1['Version'] = 'BRO'  # Neue Bezeichnung

scores_set2 = df.apply(lambda row: pd.Series({
    'total_score': row.get('M2_total_score') if row['Group'] == 'A' else row.get('M1_total_score'),
    'competence_score': row.get('M2_competence_score') if row['Group'] == 'A' else row.get('M1_competence_score'),
    'adaptability_score': row.get('M2_adaptability_score') if row['Group'] == 'A' else row.get('M1_adaptability_score'),
    'self_esteem_score': row.get('M2_self_esteem_score') if row['Group'] == 'A' else row.get('M1_self_esteem_score')
}), axis=1)
scores_set2['Version'] = 'Permobil M3'

# === Daten kombinieren und bereinigen ===
combined_scores = pd.concat([scores_set1, scores_set2], ignore_index=True)
combined_scores_clean = combined_scores.dropna()

# === Plot-Einstellungen ===
color_map = {'BRO': (0/255, 165/255, 249/255), 'Permobil M3': (0/255, 155/255, 0/255)}
score_names = ['total_score', 'competence_score', 'adaptability_score', 'self_esteem_score']

# Einheitlicher Y-Achsenbereich
y_min = combined_scores_clean[score_names].min().min()
y_max = combined_scores_clean[score_names].max().max()

# === Boxplots erstellen ===

plt.figure(figsize=(16, 12))  # größerer Plot

for i, col in enumerate(score_names, 1):
    plt.subplot(2, 2, i)

    # Gruppengrößen zählen
    n_bro = combined_scores_clean[combined_scores_clean['Version'] == 'BRO'][col].notna().sum()
    n_perm = combined_scores_clean[combined_scores_clean['Version'] == 'Permobil M3'][col].notna().sum()

    ax = sns.boxplot(
        data=combined_scores_clean,
        x='Version',
        y=col,
        palette=color_map
    )

    # Titel mit Score-Namen und n
    plt.title(f'PIADS {col} (n={n_bro} | n={n_perm})')
    plt.xlabel('')
    plt.ylabel('Score')

    # Y-Achse fix von -3.25 bis 3.25 und Ticks im 0.5er-Schritt
    ax.set_ylim(-3.25, 3.25)
    ax.set_yticks(np.arange(-3.0, 3.01, 0.5))

    # Rasterlinien
    ax.yaxis.grid(True, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)




# === Speichern ===
plt.tight_layout()
# === Boxplots speichern im Output-Ordner ===
output_path = os.path.join(base_dir, "../Output", "piads_score_boxplots_colored.png")
plt.savefig(output_path, dpi=300)
plt.close()
print(f"PIADS-Boxplots gespeichert unter: {output_path}")


# Funktion zum Extrahieren der SSI-Werte
def extract_ssi(row, version):
    if version == 'Set 1':
        return {
            'SSI_1': row.get('M1_SSI_1') if row['Group'] == 'A' else row.get('M2_SSI_1'),
            'SSI_3': row.get('M1_SSI_3') if row['Group'] == 'A' else row.get('M2_SSI_3'),
            'SSI_9': row.get('M1_SSI_9') if row['Group'] == 'A' else row.get('M2_SSI_9'),
            'SSI_10': row.get('M1_SSI_10') if row['Group'] == 'A' else row.get('M2_SSI_10'),
            'Version': 'BRO'
        }
    else:
        return {
            'SSI_1': row.get('M2_SSI_1') if row['Group'] == 'A' else row.get('M1_SSI_1'),
            'SSI_3': row.get('M2_SSI_3') if row['Group'] == 'A' else row.get('M1_SSI_3'),
            'SSI_9': row.get('M2_SSI_9') if row['Group'] == 'A' else row.get('M1_SSI_9'),
            'SSI_10': row.get('M2_SSI_10') if row['Group'] == 'A' else row.get('M1_SSI_10'),
            'Version': 'Permobil M3'
        }

# Daten erzeugen
ssi_set1 = df.apply(lambda row: extract_ssi(row, 'Set 1'), axis=1, result_type='expand')
ssi_set2 = df.apply(lambda row: extract_ssi(row, 'Set 2'), axis=1, result_type='expand')

# Kombinieren und bereinigen
ssi_combined = pd.concat([ssi_set1, ssi_set2], ignore_index=True)
ssi_combined_clean = ssi_combined.dropna()


# SSI-Items und Titelzuordnung
ssi_items = ['SSI_1', 'SSI_3', 'SSI_9', 'SSI_10']
ssi_titles = {
    'SSI_1': 'Komfort',
    'SSI_3': 'Zufriedenheit',
    'SSI_9': 'Anstrengung',
    'SSI_10': 'Sicherheit'
}

bar_colors = {'BRO': (0/255, 165/255, 249/255), 'Permobil M3': (0/255, 155/255, 0/255)}

# --- Maximalwert über alle Kombinationen finden ---
max_count = 0
for item in ssi_items:
    for version in ['BRO', 'Permobil M3']:
        version_data = ssi_combined_clean[ssi_combined_clean['Version'] == version][item]
        counts = version_data.value_counts()
        if not counts.empty:
            max_count = max(max_count, counts.max())

# Für Übersicht etwas Puffer geben (z. B. +1)
y_max = int(np.ceil(max_count + 1))

# --- Plots ---
fig, axs = plt.subplots(2, 4, figsize=(20, 10))

for col_idx, item in enumerate(ssi_items):
    for row_idx, version in enumerate(['BRO', 'Permobil M3']):
        ax = axs[row_idx, col_idx]
        version_data = ssi_combined_clean[ssi_combined_clean['Version'] == version][item]
        value_counts = version_data.value_counts().sort_index()

        for score in range(0, 8):
            if score not in value_counts.index:
                value_counts.loc[score] = 0
        value_counts = value_counts.sort_index()

        ax.bar(value_counts.index, value_counts.values, color=bar_colors[version])

        n = int(value_counts.sum())
        ax.set_title(f"{ssi_titles[item]} – {version} (n={n})")

        ax.set_xlim(-0.5, 7.5)
        ax.set_ylim(0, y_max)
        ax.set_xticks(range(0, 8))
        ax.set_yticks(range(0, y_max + 1))  # Nur ganze Zahlen
        ax.set_xlabel('Score')
        ax.set_ylabel('Anzahl')
        ax.grid(True, axis='y', linestyle='--', linewidth=0.5)

plt.tight_layout()

# Speichern
# === SSI-Balkenplots speichern im Output-Ordner ===
split_named_bar_path = os.path.join(base_dir, "../Output", "ssi_stacked_barplots_split_named.png")
plt.savefig(split_named_bar_path, dpi=300)
plt.close()
print(f"SSI-Barplots gespeichert unter: {split_named_bar_path}")

# === Gruppierte Barplots für Aufgaben 1–6 mit korrekt zugewiesenen Scores ===

color_map = {'BRO': (0/255, 165/255, 249/255), 'Permobil M3': (0/255, 155/255, 0/255)}

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

# Schritt 2: Plots erstellen mit einheitlicher y-Achse
for i, (task_num, score_counts) in enumerate(score_data_per_task):
    ax = axs[i]
    width = 0.35
    x = np.arange(len(score_counts.index))

    bars_bro = ax.bar(x - width/2, score_counts['BRO'], width, label='BRO', color=color_map['BRO'])
    bars_m3 = ax.bar(x + width/2, score_counts['Permobil M3'], width, label='Permobil M3', color=color_map['Permobil M3'])

    ax.set_title(f'Aufgabe {task_num}', fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(['1', '2', '3'], fontsize=10)
    ax.set_ylim(0, global_max + 1)
    ax.set_yticks(list(range(0, global_max + 5, 5)))
    ax.set_ylabel('Anzahl', fontsize=10)
    ax.grid(True, axis='y', linestyle='--', linewidth=0.5)

    # Balkenbeschriftung
    for bar in bars_bro + bars_m3:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, height + 0.3, f"{int(height)}", ha='center', va='bottom', fontsize=9)

axs[-1].set_xlabel('Score', fontsize=10)
axs[0].legend(loc='upper left', fontsize=9)

plt.tight_layout()
output_path = os.path.join(base_dir, "../Output", "task1to6_score_grouped_barplot_corrected.png")
plt.savefig(output_path, dpi=300)
plt.close()

print(f"KORREKTER Score-Barplot (BRO vs. Permobil M3) gespeichert unter: {output_path}")
