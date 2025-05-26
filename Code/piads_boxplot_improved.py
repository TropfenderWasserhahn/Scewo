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
    """Create and save boxplots for the given scores."""
    plt.figure(figsize=(16, 12))
    for i, col in enumerate(score_names, 1):
        plt.subplot(2, 2, i)
        ax = sns.boxplot(data=data, x='Version', y=col, hue='Version', palette=color_map, dodge=False)

        # Add title with sample sizes
        n_bro = data[data['Version'] == 'BRO'][col].notna().sum()
        n_perm = data[data['Version'] == 'Permobil M3'][col].notna().sum()
        plt.title(f'PIADS {col} (n={n_bro} | n={n_perm})')
        plt.xlabel('')
        plt.ylabel('Score')

        # Set y-axis limits and ticks
        ax.set_ylim(y_lim)
        ax.set_yticks(y_ticks)

        # Add gridlines
        ax.yaxis.grid(True, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)

        # Mittelwerte als schwarze Rauten
        for version in data['Version'].unique():
            mean_val = data[data['Version'] == version][col].mean()
            xpos = 0 if version == 'BRO' else 1
            ax.plot(xpos, mean_val, marker='D', color='black', markersize=6, label='Mittelwert' if i == 1 and version == 'BRO' else "")

        if i == 1:
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