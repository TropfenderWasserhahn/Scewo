import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# === Constants ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COLOR_MAP = {'BRO': (0/255, 165/255, 249/255), 'Permobil M3': (169/255, 169/255, 169/255)}
SSI_ITEMS = ['SSI_1', 'SSI_3', 'SSI_9', 'SSI_10']
SSI_TITLES = {
    'SSI_1': 'Komfort',
    'SSI_3': 'Zufriedenheit',
    'SSI_9': 'Anstrengung',
    'SSI_10': 'Sicherheit'
}
SCORE_RANGE = range(1, 8)
BAR_WIDTH = 0.4

# === Helper Functions ===
def load_csv(filename):
    """Load a CSV file into a DataFrame."""
    return pd.read_csv(os.path.join(BASE_DIR, "../Data", filename))

def extract_ssi(df, group_col, version_label, prefix1, prefix2):
    """Extract SSI values based on group and version."""
    return df.apply(lambda row: pd.Series({
        'SSI_1': row.get(f"{prefix1}_SSI_1") if row[group_col] == 'A' else row.get(f"{prefix2}_SSI_1"),
        'SSI_3': row.get(f"{prefix1}_SSI_3") if row[group_col] == 'A' else row.get(f"{prefix2}_SSI_3"),
        'SSI_9': row.get(f"{prefix1}_SSI_9") if row[group_col] == 'A' else row.get(f"{prefix2}_SSI_9"),
        'SSI_10': row.get(f"{prefix1}_SSI_10") if row[group_col] == 'A' else row.get(f"{prefix2}_SSI_10"),
        'Version': version_label
    }), axis=1)

def calculate_mean(value_counts):
    """Calculate the mean score from value counts."""
    total = (np.array(value_counts.index) * value_counts.values).sum()
    count = value_counts.sum()
    return total / count if count > 0 else 0

def plot_ssi_bars(ax, data, item, color_map, score_range, bar_width):
    """Plot bar chart for a single SSI item."""
    mean_values = {}
    for i, version in enumerate(['BRO', 'Permobil M3']):
        version_data = data[data['Version'] == version][item]
        value_counts = version_data.value_counts().reindex(score_range, fill_value=0).sort_index()

        # Calculate mean
        mean_values[version] = calculate_mean(value_counts)

        # Plot bars
        x = [s + (i - 0.5) * bar_width for s in score_range]
        ax.bar(x, value_counts.values, width=bar_width, label=f"{version} (Ø={mean_values[version]:.2f})", color=color_map[version])

    return mean_values

# === Main Logic ===
df = load_csv("merged_data.csv")

# Extract SSI values for both sets
ssi_set1 = extract_ssi(df, 'Group', 'BRO', 'M1', 'M2')
ssi_set2 = extract_ssi(df, 'Group', 'Permobil M3', 'M2', 'M1')

# Combine and clean data
ssi_combined = pd.concat([ssi_set1, ssi_set2], ignore_index=True)
ssi_combined_clean = ssi_combined.dropna()

# Determine y-axis max value dynamically for each SSI item
y_max_values = {}
for item in SSI_ITEMS:
    max_count = 0
    for version in ['BRO', 'Permobil M3']:
        version_data = ssi_combined_clean[ssi_combined_clean['Version'] == version][item]
        counts = version_data.value_counts()
        if not counts.empty:
            max_count = max(max_count, counts.max())
    y_max_values[item] = int(np.ceil(max_count + 1))

# Plot grouped bar charts
fig, axs = plt.subplots(1, len(SSI_ITEMS), figsize=(20, 5))
for ax, item in zip(axs, SSI_ITEMS):
    plot_ssi_bars(ax, ssi_combined_clean, item, COLOR_MAP, SCORE_RANGE, BAR_WIDTH)

    # Format plot
    n = int(ssi_combined_clean[item].count() / 2)  # n per version
    ax.set_title(f"{SSI_TITLES[item]} (n={n})")
    ax.set_xlim(0.5, 7.5)
    ax.set_ylim(0, y_max_values[item])  # Use dynamic y_max for each item
    ax.set_xticks(SCORE_RANGE)
    ax.set_xlabel('Score')
    ax.set_ylabel('Anzahl')
    ax.grid(True, axis='y', linestyle='--', linewidth=0.5)
    ax.legend(loc='upper left', fontsize=9)

plt.tight_layout()

# Save plot
output_path = os.path.join(BASE_DIR, "../Output", "ssi_grouped_barplots_combined.png")
plt.savefig(output_path, dpi=300)
plt.close()
print(f"Gruppierte SSI-Barplots mit Mittelwerten gespeichert unter: {output_path}")