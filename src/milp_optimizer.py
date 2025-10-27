import pulp
import random
import time
import pandas as pd

devices = {
    "Device_1": {"Energy": 30, "Available": True},
    "Device_2": {"Energy": 40, "Available": True},
    "Device_3": {"Energy": 35, "Available": True},
    "Device_4": {"Energy": 50, "Available": True},
    "Device_5": {"Energy": 25, "Available": True},
}


tasks = ["SensorRead", "ControlSignal", "Maintenance"]

def optimize_task_allocation(devices_dict, tasks_list):
    """Run MILP optimization to assign tasks to devices minimizing total energy."""
    prob = pulp.LpProblem("IIoT_Task_Assignment", pulp.LpMinimize)

    # this is binary decision variable x[d][t] = 1 if device d executes task t
    x = pulp.LpVariable.dicts("assign",
                              ((d, t) for d in devices_dict for t in tasks_list),
                              cat="Binary")

    # this will  minimize total energy use
    prob += pulp.lpSum(devices_dict[d]["Energy"] * x[(d, t)]
                       for d in devices_dict for t in tasks_list)

    # this is for  each task must be assigned to exactly one available device
    for t in tasks_list:
        prob += pulp.lpSum(x[(d, t)] for d in devices_dict if devices_dict[d]["Available"]) == 1

    # this is for  a device can handle at most one task
    for d in devices_dict:
        prob += pulp.lpSum(x[(d, t)] for t in tasks_list) <= 1

    
    prob.solve(pulp.PULP_CBC_CMD(msg=False))


    assignments = []
    for d in devices_dict:
        for t in tasks_list:
            if x[(d, t)].value() == 1:
                assignments.append({"Device": d, "Task": t, "Energy": devices_dict[d]["Energy"]})
    df = pd.DataFrame(assignments)
    print("\n--- Optimized Task Allocation ---")
    print(df)
    return df


def dynamic_reallocation():
    """Simulate dynamic reallocation every few seconds (for demo)."""
    while True:
        
        failed_device = random.choice(list(devices.keys()))
        devices[failed_device]["Available"] = False
        print(f"\nDevice {failed_device} reported anomaly → temporarily unavailable.")

        
        optimize_task_allocation(devices, tasks)

    
        time.sleep(5)
        devices[failed_device]["Available"] = True


if __name__ == "__main__":
    print("Initial optimization:")
    optimize_task_allocation(devices, tasks)

    print("\nStarting dynamic reallocation loop (Ctrl+C to stop):")
    try:
        dynamic_reallocation()
    except KeyboardInterrupt:
        print("\nStopped by user.")
