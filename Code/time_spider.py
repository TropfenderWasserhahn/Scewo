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

