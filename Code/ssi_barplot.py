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
# --- Plots ---
fig, axs = plt.subplots(1, 4, figsize=(20, 5))  # Nur eine Zeile, vier Spalten für die SSI-Items

for col_idx, item in enumerate(ssi_items):
    ax = axs[col_idx]

    bar_width = 0.4
    score_range = range(1, 8)

    # Durchschnittswerte initialisieren
    mean_values = {}

    for i, version in enumerate(['BRO', 'Permobil M3']):
        version_data = ssi_combined_clean[ssi_combined_clean['Version'] == version][item]
        value_counts = version_data.value_counts().sort_index()

        # Fehlende Scores mit 0 auffüllen
        for score in score_range:
            if score not in value_counts.index:
                value_counts.loc[score] = 0
        value_counts = value_counts.sort_index()

        # Mittelwert berechnen
        total = sum(score * count for score, count in zip(value_counts.index, value_counts.values))
        n_version = value_counts.sum()
        mean = total / n_version if n_version > 0 else 0
        mean_values[version] = mean

        # X-Position leicht verschieben je nach Version
        x = [s + (i - 0.5) * bar_width for s in score_range]
        ax.bar(x, value_counts.values, width=bar_width, label=f"{version} (Ø={mean:.2f})", color=color_map[version])

    # Formatierung
    n = int(ssi_combined_clean[item].count() / 2)  # n pro Version
    ax.set_title(f"{ssi_titles[item]} (n={n})")
    ax.set_xlim(0.5, 7.5)
    ax.set_ylim(0, y_max)
    ax.set_xticks(score_range)
    ax.set_xlabel('Score')
    ax.set_ylabel('Anzahl')
    ax.grid(True, axis='y', linestyle='--', linewidth=0.5)

    # Legende mit Mittelwerten
    ax.legend(loc='upper left', fontsize=9)

plt.tight_layout()

# Speichern
combined_bar_path = os.path.join(base_dir, "../Output", "ssi_grouped_barplots_combined.png")
plt.savefig(combined_bar_path, dpi=300)
plt.close()
print(f"Gruppierte SSI-Barplots mit Mittelwerten gespeichert unter: {combined_bar_path}")