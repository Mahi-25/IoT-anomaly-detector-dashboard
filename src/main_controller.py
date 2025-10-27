import threading
import time
import random
import pandas as pd
import joblib
from datetime import datetime
from queue import Queue
import pulp

#  this is to load AI Model & Scaler
model = joblib.load("models/knn_model.pkl")
scaler = joblib.load("models/scaler.pkl")

data_queue = Queue()

devices = {
    f"Device_{i}": {"Energy": random.randint(25, 50), "Available": True}
    for i in range(1, 6)
}
tasks = ["SensorRead", "ControlSignal", "Maintenance"]

task_deadlines = {"SensorRead": 150, "ControlSignal": 100, "Maintenance": 200}

#  this is for Real-Time Data Simulation for IoT Device Threads

def simulate_device(device_id):
    while True:
        task = random.choice(tasks)
        cpu = random.uniform(20, 100)
        energy = random.uniform(10, 90)
        response = random.uniform(50, 250)
        deadline = task_deadlines[task]

        record = {
            "DeviceID": device_id,
            "Task": task,
            "CPU_Usage": cpu,
            "Energy_Use": energy,
            "ResponseTime": response,
            "Deadline": deadline,
        }
        data_queue.put(record)
        time.sleep(random.uniform(0.5, 1.5))

#  this part is MILP Optimization Engine
def optimize_task_allocation(devices_dict, tasks_list):
    """Run MILP optimization to minimize total energy."""
    prob = pulp.LpProblem("IIoT_Task_Assignment", pulp.LpMinimize)
    x = pulp.LpVariable.dicts(
        "assign",
        ((d, t) for d in devices_dict for t in tasks_list),
        cat="Binary",
    )

    prob += pulp.lpSum(
        devices_dict[d]["Energy"] * x[(d, t)]
        for d in devices_dict
        for t in tasks_list
        if devices_dict[d]["Available"]
    )

    for t in tasks_list:
        prob += (
            pulp.lpSum(
                x[(d, t)] for d in devices_dict if devices_dict[d]["Available"]
            )
            == 1
        )

    for d in devices_dict:
        prob += pulp.lpSum(x[(d, t)] for t in tasks_list) <= 1

    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    results = []
    for d in devices_dict:
        for t in tasks_list:
            if x[(d, t)].value() == 1:
                results.append({"Device": d, "Task": t})
    return results

#  this part is Scheduler + Anomaly Detection Controller
def controller():
    print("\n=== IIoT Controller Started (AI + MILP) ===\n")
    log = []

    while True:
        if not data_queue.empty():
            rec = data_queue.get()

            # this is for AI Prediction
            X = pd.DataFrame(
                [[rec["CPU_Usage"], rec["Energy_Use"], rec["ResponseTime"], rec["Deadline"]]],
                columns=["CPU_Usage", "Energy_Use", "ResponseTime", "Deadline"],
            )
            X_scaled = scaler.transform(X)
            pred = model.predict(X_scaled)[0]
            label = "anomaly" if pred == 1 else "normal"

            timestamp = datetime.now().strftime("%H:%M:%S")

            print(
                f"[{timestamp}] {rec['DeviceID']} | Task={rec['Task']} | "
                f"CPU={rec['CPU_Usage']:.1f}% | Energy={rec['Energy_Use']:.1f}W | "
                f"Resp={rec['ResponseTime']:.1f}ms | → {label.upper()}"
            )

            # this will update availability based on anomaly detection
            if label == "anomaly":
                devices[rec["DeviceID"]]["Available"] = False
            else:
                devices[rec["DeviceID"]]["Available"] = True

        
            if len(log) % 30 == 0:
                assignments = optimize_task_allocation(devices, tasks)
                print("\n--- Optimized Allocation ---")
                for a in assignments:
                    print(f"{a['Device']} → {a['Task']}")
                print("------------------------------\n")

            log.append(
                {
                    "time": timestamp,
                    "device": rec["DeviceID"],
                    "task": rec["Task"],
                    "cpu": rec["CPU_Usage"],
                    "energy": rec["Energy_Use"],
                    "response": rec["ResponseTime"],
                    "deadline": rec["Deadline"],
                    "label": label,
                }
            )

            if len(log) % 100 == 0:
                pd.DataFrame(log).to_csv("data/system_log.csv", index=False)
        else:
            time.sleep(0.2)


if __name__ == "__main__":
    # this is to start all device threads
    for dev in devices:
        threading.Thread(target=simulate_device, args=(dev,), daemon=True).start()

    # this is to start central controller
    try:
        controller()
    except KeyboardInterrupt:
        print("\nSystem stopped by user.")
