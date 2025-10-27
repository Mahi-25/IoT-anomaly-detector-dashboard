import threading
import time
import random
import pandas as pd
import joblib
from datetime import datetime
from queue import Queue

# this is to load trained model and scaler
model = joblib.load("models/knn_model.pkl")
scaler = joblib.load("models/scaler.pkl")


data_queue = Queue()


devices = [f"Device_{i}" for i in range(1, 6)]

# this is to define task types and their nominal deadlines
task_types = {
    "SensorRead": 150,
    "ControlSignal": 100,
    "Maintenance": 200
}

# this is function to simulate a device generating data
def simulate_device(device_id):
    while True:
        task = random.choice(list(task_types.keys()))
        cpu = random.uniform(20, 100)
        energy = random.uniform(10, 90)
        response = random.uniform(50, 250)
        deadline = task_types[task]

        data_point = {
            "DeviceID": device_id,
            "Task": task,
            "CPU_Usage": cpu,
            "Energy_Use": energy,
            "ResponseTime": response,
            "Deadline": deadline
        }
        data_queue.put(data_point)
        time.sleep(random.uniform(0.5, 2.0))  



def scheduler():
    print("\n--- Real-Time IIoT Scheduler Started ---\n")
    log = []

    while True:
        if not data_queue.empty():
            record = data_queue.get()

            # this is to prepare data for prediction
            X = pd.DataFrame([[record["CPU_Usage"], record["Energy_Use"],
                               record["ResponseTime"], record["Deadline"]]],
                             columns=["CPU_Usage", "Energy_Use", "ResponseTime", "Deadline"])
            X_scaled = scaler.transform(X)
            pred = model.predict(X_scaled)[0]
            label = "anomaly" if pred == 1 else "normal"

            timestamp = datetime.now().strftime("%H:%M:%S")

            print(f"[{timestamp}] {record['DeviceID']} | "
                  f"Task={record['Task']} | CPU={record['CPU_Usage']:.1f}% | "
                  f"Energy={record['Energy_Use']:.1f}W | "
                  f"Resp={record['ResponseTime']:.1f}ms | "
                  f"→ {label.upper()}")

            log.append({
                "time": timestamp,
                "device": record["DeviceID"],
                "task": record["Task"],
                "cpu": record["CPU_Usage"],
                "energy": record["Energy_Use"],
                "response": record["ResponseTime"],
                "deadline": record["Deadline"],
                "label": label
            })

        
            if len(log) % 50 == 0:
                pd.DataFrame(log).to_csv("data/realtime_log.csv", index=False)

        else:
            time.sleep(0.1)


# this will launch simulation threads for each device
if __name__ == "__main__":
    for dev in devices:
        threading.Thread(target=simulate_device, args=(dev,), daemon=True).start()

    scheduler()
