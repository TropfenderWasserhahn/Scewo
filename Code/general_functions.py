COLOR_MAP = {'BRO': (0/255, 165/255, 249/255), 'Permobil M3': (169/255, 169/255, 169/255)}

# Einheitliche Schriftgröße und Stil für alle Plots
plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 10,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "legend.fontsize": 10,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
})

def add_mean_legend(ax, data_dict):
    """
    Fügt eine Legende mit Mittelwerten für Balken-/Boxplots hinzu.

    Parameter:
    - ax: Matplotlib-Achse (z. B. aus fig, ax = plt.subplots())
    - data_dict: Dictionary mit Labels als Keys (z. B. "BRO", "M3")
                 und Pandas Series oder Listen mit Werten als Values.

    Beispiel:
    add_mean_legend(ax, {
        "BRO": bro_data["BRO_total"].dropna(),
        "M3": m3_data["M3_total"].dropna()
    })
    """
    handles = []
    for label, values in data_dict.items():
        mean_val = round(values.mean(), 2)
        color = COLOR_MAP.get(label, "gray")  # Standardfarbe, falls Label nicht im Farbschema
        line = plt.Line2D([0], [0], color=color, lw=4, label=f"{label} (Ø = {mean_val})")
        handles.append(line)
    ax.legend(handles=handles)
