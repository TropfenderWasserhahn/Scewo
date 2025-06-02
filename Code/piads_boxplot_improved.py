import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# === Constants ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COLOR_MAP = {'BRO': (0/255, 165/255, 249/255), 'Permobil M3': (169/255, 169/255, 169/255)}
SCORE_NAMES = ['total_score', 'competence_score', 'adaptability_score', 'self_esteem_score']
Y_LIM = (-3.25, 3.25)
Y_TICKS = np.arange(-3.0, 3.01, 0.5)

# === Helper Functions ===
def load_csv(filename):
    """Load a CSV file into a DataFrame."""
    return pd.read_csv(os.path.join(BASE_DIR, "../Data", filename))

def extract_scores(df, group_col, version_label, prefix1, prefix2):
    """Extract scores based on group and version."""
    return df.apply(lambda row: pd.Series({
        'total_score': row.get(f"{prefix1}_total_score") if row[group_col] == 'A' else row.get(f"{prefix2}_total_score"),
        'competence_score': row.get(f"{prefix1}_competence_score") if row[group_col] == 'A' else row.get(f"{prefix2}_competence_score"),
        'adaptability_score': row.get(f"{prefix1}_adaptability_score") if row[group_col] == 'A' else row.get(f"{prefix2}_adaptability_score"),
        'self_esteem_score': row.get(f"{prefix1}_self_esteem_score") if row[group_col] == 'A' else row.get(f"{prefix2}_self_esteem_score"),
        'Version': version_label
    }), axis=1)

def plot_boxplots(data, score_names, y_lim, y_ticks, color_map, output_path):
    """Create and save boxplots using matplotlib (volle Kontrolle)."""
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))

    for i, (col, ax) in enumerate(zip(score_names, axes)):
        # Daten für beide Gruppen
        bro_vals = data[data['Version'] == 'BRO'][col].dropna()
        perm_vals = data[data['Version'] == 'Permobil M3'][col].dropna()
        grouped_data = [bro_vals, perm_vals]

        # Boxplot mit vollen Kontrollelementen
        box = ax.boxplot(
            grouped_data,
            widths=0.2,
            patch_artist=True,
            boxprops=dict(linewidth=1, edgecolor='black'),
            medianprops=dict(color='black'),
            whiskerprops=dict(color='black', linewidth=1),
            capprops=dict(color='black', linewidth=1),
            flierprops=dict(marker='o', color='black', markersize=3, alpha=0.6)
        )

        # Farben setzen
        colors = [color_map['BRO'], color_map['Permobil M3']]
        for patch, color in zip(box['boxes'], colors):
            patch.set_facecolor(color)

        # Achsen- und Titelbeschriftungen
        ax.set_xticks([1, 2])
        ax.set_xticklabels(['BRO', 'Permobil M3'])
        ax.set_title(f'PIADS {col} (n={len(bro_vals)} | n={len(perm_vals)})')
        ax.set_ylabel("Score" if i == 0 else "")
        ax.set_ylim(y_lim)
        ax.set_yticks(y_ticks)
        ax.yaxis.grid(True, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)

        # Mittelwerte als schwarze Rauten
        for j, values in enumerate(grouped_data, start=1):
            mean_val = values.mean()
            ax.plot(j, mean_val, marker='D', color='black', markersize=6,
                    label='Mittelwert' if i == 0 and j == 1 else "")

        if i == 0:
            ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"PIADS-Boxplots gespeichert unter: {output_path}")


# === Main Logic ===
df = load_csv("merged_data.csv")

# Extract scores for both versions
scores_set1 = extract_scores(df, 'Group', 'BRO', 'M1', 'M2')
scores_set2 = extract_scores(df, 'Group', 'Permobil M3', 'M2', 'M1')

# Combine and clean scores
combined_scores = pd.concat([scores_set1, scores_set2], ignore_index=True)
combined_scores_clean = combined_scores.dropna()

# Plot and save boxplots
output_path = os.path.join(BASE_DIR, "../Output", "piads_boxplots.png")
plot_boxplots(combined_scores_clean, SCORE_NAMES, Y_LIM, Y_TICKS, COLOR_MAP, output_path)