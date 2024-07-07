import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

#2->17, once its armed, take off keep the same
#17(auto takeoff)->14 (offboard), once it starts rl
#nav_State 14->2, maybe takes-over control, intention still 14
file_path = "/home/kangle/Documents/FYP/play/Tensile_Perching_Flight_Data/2024_06_14_state/rosbag2_2024_06_14-11_09_26_traj_1_full_success_state.csv"
data = pd.read_csv(file_path)

# Normalize timestamps
data['Normalized Timestamp'] = (data['Timestamp'] - data['Timestamp'].min()) / 1e9  # Convert to seconds

# Find the first timestamp when armed_time > 0 and takeoff_time > 0
first_armed_time = data[data['armed_time'] > 0]['Normalized Timestamp'].min()
first_takeoff_time = data[data['takeoff_time'] > 0]['Normalized Timestamp'].min()

print(f"File: {os.path.basename(file_path)}")
if pd.notna(first_armed_time):
    print(f"First timestamp (s) when armed_time > 0: {first_armed_time}")
else:
    print("No armed_time > 0 found.")

if pd.notna(first_takeoff_time):
    print(f"First timestamp (s) when takeoff_time > 0: {first_takeoff_time}")
else:
    print("No takeoff_time > 0 found.")

# Check for changes in nav_state and nav_state_user_intention and print the timestamps along with old and new values
previous_nav_state = None
previous_nav_state_user_intention = None

for index, row in data.iterrows():
    current_nav_state = row['nav_state']
    current_nav_state_user_intention = row['nav_state_user_intention']
    timestamp = row['Normalized Timestamp']
    
    if previous_nav_state is not None and current_nav_state != previous_nav_state:
        print(f"Timestamp (s): {timestamp}, nav_state changed from {previous_nav_state} to {current_nav_state}")
    
    if previous_nav_state_user_intention is not None and current_nav_state_user_intention != previous_nav_state_user_intention:
        print(f"Timestamp (s): {timestamp}, nav_state_user_intention changed from {previous_nav_state_user_intention} to {current_nav_state_user_intention}")
    
    previous_nav_state = current_nav_state
    previous_nav_state_user_intention = current_nav_state_user_intention
