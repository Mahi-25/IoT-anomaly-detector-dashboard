import pandas as pd
import numpy as np
import random

# this is to to set a random seed for reproducibility
np.random.seed(42)

# Number of simulated records
N = 1000

devices = [f"Device_{i}" for i in range(1, 11)]
tasks = ["SensorRead", "ControlSignal", "Maintenance"]

data = []

for _ in range(N):
    device = random.choice(devices)
    task = random.choice(tasks)
    cpu = np.clip(np.random.normal(60, 20), 10, 100)           # percent
    energy = np.clip(np.random.normal(40, 15), 5, 100)         # watts
    response = np.clip(np.random.normal(120, 50), 20, 300)     # ms
    deadline = random.choice([100, 150, 200, 250])
    
    # this will label as anomaly if device overloaded or slow
    if cpu > 85 or response > deadline or energy > 70:
        label = "anomaly"
    else:
        label = "normal"
    
    data.append([device, task, cpu, energy, response, deadline, label])

df = pd.DataFrame(data, columns=[
    "DeviceID", "Task", "CPU_Usage", "Energy_Use", 
    "ResponseTime", "Deadline", "Label"
])

df.to_csv("iiot_dataset.csv", index=False)
print("Synthetic IIoT dataset generated: iiot_dataset.csv")
print(df.head(10))
