'''
Description: This script reads a rosbag file and extracts the positions of the drone, payload, and round bar from the Vicon system.
The extracted data is then interpolated to fill in missing values and saved to a CSV file.

Install by running: 'pip3 install rosbags'
Usage: python3 rosbag_reader_combined.py --path ~/Documents/rosbag-tensile-perching/success/rosbag2_2024_05_22-17_26_15

All ros topics related to the positions of the drone, payload, and round bar are as follows:

Drone ROS2 Topics: /fmu/out/vehicle_status
'''
import csv
import os
import argparse
from collections import defaultdict
from rosbags.rosbag2 import Reader
from rosbags.typesys import Stores, get_types_from_msg, get_typestore
import pandas as pd
import numpy as np

# Topics to read from
TOPICS = {
    'drone': '/fmu/out/vehicle_status'
}

# Correct message definition for px4_msgs/msg/VehicleStatus
STRIDX_MSG = """
uint64 timestamp
uint64 armed_time
uint64 takeoff_time
uint8 arming_state
uint8 latest_arming_reason
uint8 latest_disarming_reason
uint64 nav_state_timestamp
uint8 nav_state_user_intention
uint8 nav_state
uint8 executor_in_charge
uint32 valid_nav_states_mask
uint32 can_set_nav_states_mask
uint16 failure_detector_status
uint8 hil_state
uint8 vehicle_type
bool failsafe
bool failsafe_and_user_took_over
uint8 failsafe_defer_state
bool gcs_connection_lost
uint8 gcs_connection_lost_counter
bool high_latency_data_link_lost
bool is_vtol
bool is_vtol_tailsitter
bool in_transition_mode
bool in_transition_to_fw
uint8 system_type
uint8 system_id
uint8 component_id
bool safety_button_available
bool safety_off
bool power_input_valid
bool usb_connected
bool open_drone_id_system_present
bool open_drone_id_system_healthy
bool parachute_system_present
bool parachute_system_healthy
bool avoidance_system_required
bool avoidance_system_valid
bool rc_calibration_in_progress
bool calibration_enabled
bool pre_flight_checks_pass
"""

# Initialize the typestore and register the custom message type
typestore = get_typestore(Stores.ROS2_HUMBLE)
typestore.register(get_types_from_msg(STRIDX_MSG, 'px4_msgs/msg/VehicleStatus'))

StrIdx = typestore.types['px4_msgs/msg/VehicleStatus']

def print_connections(reader):
    """Prints all topic and msgtype information available in the rosbag."""
    for connection in reader.connections:
        print(connection.topic, connection.msgtype)

def collect_messages(reader, topics):
    """Collects messages from specified topics in the rosbag and returns a dictionary of timestamped data."""
    data = defaultdict(lambda: {
        #'timestamp':None,
        'armed_time': None, 'takeoff_time': None,
        'nav_state_user_intention':None, 'nav_state': None
    })

    for name, topic in topics.items():
        connections = [x for x in reader.connections if x.topic == topic]
        for connection, timestamp, rawdata in reader.messages(connections=connections):
            msg = typestore.deserialize_cdr(rawdata, connection.msgtype)
            #data[timestamp]['timestamp']=msg.timestamp
            data[timestamp]['armed_time'] = msg.armed_time
            data[timestamp]['takeoff_time'] = msg.takeoff_time
            data[timestamp]['nav_state_user_intention'] = msg.nav_state_user_intention
            data[timestamp]['nav_state'] = msg.nav_state


    return data

def interpolate_data(data):
    """Interpolates missing values in the collected data."""
    df = pd.DataFrame.from_dict(data, orient='index')
    df.sort_index(inplace=True)
    df.interpolate(method='linear', inplace=True)
    df.ffill(inplace=True)
    df.bfill(inplace=True)
    return df

def save_messages_to_csv(data, csv_filename):
    """Saves the collected data to a CSV file."""
    # Ensure the data is in the correct format
    formatted_data = {k: {kk: (vv if not isinstance(vv, np.ndarray) else vv.tolist()) for kk, vv in v.items()} for k, v in data.items()}
    
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame.from_dict(formatted_data, orient='index')
    
    # Save the DataFrame to a CSV file
    df.to_csv(csv_filename, index_label='Timestamp')
    print(f"Data saved to {csv_filename}")


def main():
    """Main function to read the rosbag, process messages, and save them to a CSV file."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Process a rosbag file and save extracted data to a CSV file.')
    parser.add_argument('--path', required=True, help='Path to the rosbag file')
    args = parser.parse_args()
    bag_path = args.path

    with Reader(bag_path) as reader:
        print("Connections:")
        print_connections(reader)
        
        print("\nCollecting Positions:")
        data = collect_messages(reader, TOPICS)

        print("\n Interpolating Data:")
        df = interpolate_data(data)
        
        # Extract folder name from the bag path and create the CSV filename
        folder_name = os.path.basename(bag_path)
        csv_filename = f'{folder_name}_state.csv'
        save_messages_to_csv(df, csv_filename)

if __name__ == "__main__":
    main()
