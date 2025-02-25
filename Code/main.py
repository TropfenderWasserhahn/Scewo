# This is the main file for data analysis

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
print("Module erfolgreich geladen!")

# Load data
measurement_data = pd.read_csv("Data/Measurement.csv")
screening_data = pd.read_csv("Data/Screening.csv")
piads_data = pd.read_csv("Data/PIADS.csv")
interview_data = pd.read_csv("Data/Interview.csv")

# Data exploration
def data_exploration(data):
    print(data.head(10))
    print(data.shape)
    print(data.columns)
    print(data.info())
    print(data.describe())
    print(data.isna().sum())
    print('############################################################')

data_exploration(measurement_data)
data_exploration(screening_data)
data_exploration(piads_data)
data_exploration(interview_data)