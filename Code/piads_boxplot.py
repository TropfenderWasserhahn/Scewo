import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# === Daten laden ===
base_dir = os.path.dirname(os.path.abspath(__file__))

def load_csv(filename):
    file_path = os.path.join(base_dir, "../Data", filename)
    return pd.read_csv(file_path)

df = load_csv("merged_data.csv")

color_map = {'BRO': (0/255, 165/255, 249/255), 'Permobil M3': (169/255, 169/255, 169/255)}

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

    ax = sns.boxplot(data=combined_scores_clean, x='Version', y=col, hue='Version', palette=color_map, legend=False)

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