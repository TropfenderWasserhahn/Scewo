import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import re

# === Constants ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COLOR_MAP = {'BRO': (0/255, 165/255, 249/255), 'Permobil M3': (169/255, 169/255, 169/255)}

# === Helper Functions ===
def load_csv(filename):
    return pd.read_csv(os.path.join(BASE_DIR, "../Data", filename))

def extract_scores(row, task_num, version_label):
    prefix = "M1_" if (row['Group'] == 'A' and version_label == 'BRO') or (row['Group'] == 'B' and version_label == 'Permobil M3') else "M2_"
    return [row[col] for col in df.columns if col.startswith(f"{prefix}") and col.endswith(f"{task_num}") and pd.notna(row[col])]

def calculate_mean(score_counts, version):
    total = (score_counts[version] * score_counts.index).sum()
    count = score_counts[version].sum()
    return total / count if count > 0 else 0

