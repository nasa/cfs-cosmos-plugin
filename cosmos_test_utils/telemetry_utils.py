"""Utilities for tracking and reporting telemetry changes in COSMOS tests."""

import copy
from typing import Dict, List, Any, Optional
from .system_config import (
    COMMON_PACKET_TIME_SECONDS_FIELD,
    COMMON_PACKET_TIME_SUBSECS_FIELD,
    COMMON_PACKET_SEQUENCE_COUNT_FIELD,
    COMMON_PACKET_TIME_SECONDS_DESC,
    COMMON_PACKET_TIME_SUBSECS_DESC,
    COMMON_PACKET_SEQUENCE_DESC
)

# Global storage for telemetry tracking
prev_vals: Dict[str, Dict[str, Dict[str, Any]]] = {}
current_vals: Dict[str, Dict[str, Dict[str, Any]]] = {}

def _update_telemetry_values(
    target_name: str,
    packet_name: str
) -> None:
    """Save current telemetry values into prev_vals, then get new telemetry into current_vals.
    
    This is an internal function not meant to be called directly by users.

    Args:
        target_name: COSMOS Target name
        packet_name: COSMOS Telemetry packet name
    """
    global current_vals
    global prev_vals
    
    # Import and use the COSMOS get_tlm_packet function
    from openc3.script import get_tlm_packet
    
    # Initialize the nested dictionaries if they don't exist
    if target_name not in current_vals:
        current_vals[target_name] = {}
    if packet_name not in current_vals[target_name]:
        current_vals[target_name][packet_name] = {}
        current_vals[target_name][packet_name]["Num_Updates_Run"] = 0
    
    # Copy current values to previous values, this initializes prev_vals if this is the first time seeing this packet
    prev_vals = copy.deepcopy(current_vals)
    
    # Update the run counter
    current_vals[target_name][packet_name]["Num_Updates_Run"] += 1
    
    # Get all telemetry points for this packet
    all_tlm_points = get_tlm_packet(f"{target_name} {packet_name}", type='FORMATTED')
    
    # Store each telemetry point in the current_vals dictionary
    for tlm_point in all_tlm_points:
        current_vals[target_name][packet_name][tlm_point[0]] = tlm_point[1]


def report_telemetry(
    target_name: str,
    packet_name: str,
    level_of_detail: int = 0
) -> None:
    """Report changes in telemetry between current and previous values.
    
    Args:
        target_name: COSMOS Target name
        packet_name: COSMOS Telemetry packet name
        level_of_detail: Detail level for reporting (0=changes only, other=all values)
    
    This displays a formatted report showing:
    - Header and timing information
    - Changed telemetry values (or all values if level_of_detail > 0)
    - Change indicators for values that have changed
    """
    global current_vals
    global prev_vals
    
    # Update telemetry values first
    _update_telemetry_values(target_name, packet_name)
    
    current_packet = current_vals[target_name][packet_name]
    previous_packet = prev_vals[target_name][packet_name]
    
    
    # Calculate deltas for timing fields if this isn't the first run
    if current_packet.get('Num_Updates_Run') != 1:
        secs_delta = current_packet.get(COMMON_PACKET_TIME_SECONDS_FIELD, 0) - previous_packet.get(COMMON_PACKET_TIME_SECONDS_FIELD, 0)
        subsecs_delta = current_packet.get(COMMON_PACKET_TIME_SUBSECS_FIELD, 0) - previous_packet.get(COMMON_PACKET_TIME_SUBSECS_FIELD, 0)
        seq_delta = current_packet.get(COMMON_PACKET_SEQUENCE_COUNT_FIELD, 0) - previous_packet.get(COMMON_PACKET_SEQUENCE_COUNT_FIELD, 0)
    
        # Handle potential missing fields without crashing
        if all(field in current_packet and field in previous_packet for field in ['PACKET_TIMESECONDS', 'RECEIVED_TIMESECONDS', 'RECEIVED_COUNT']):
            pkt_time_sec_delta = float(current_packet.get('PACKET_TIMESECONDS', '0')) - float(previous_packet.get('PACKET_TIMESECONDS', '0'))
            rec_time_sec_delta = float(current_packet.get('RECEIVED_TIMESECONDS', '0')) - float(previous_packet.get('RECEIVED_TIMESECONDS', '0'))
            cosmos_rec_cnt_delta = current_packet.get('RECEIVED_COUNT', 0) - previous_packet.get('RECEIVED_COUNT', 0)
        else:
            pkt_time_sec_delta = 0
            rec_time_sec_delta = 0
            cosmos_rec_cnt_delta = 0
    else:
        # First run - initialize all delta variables to 0
        secs_delta = 0
        subsecs_delta = 0
        seq_delta = 0
        pkt_time_sec_delta = 0
        rec_time_sec_delta = 0
        cosmos_rec_cnt_delta = 0
        
    # Lists of telemetry items to exclude from detailed reports
    tlm_to_exclude = ['Num_Updates_Run', COMMON_PACKET_TIME_SECONDS_FIELD, COMMON_PACKET_TIME_SUBSECS_FIELD, COMMON_PACKET_SEQUENCE_COUNT_FIELD, 
                      'PACKET_TIMEFORMATTED', 'RECEIVED_TIMEFORMATTED', 'RECEIVED_COUNT']
    tlm_to_exclude_in_lvl_0 = ['Num_Updates_Run', COMMON_PACKET_TIME_SECONDS_FIELD, COMMON_PACKET_TIME_SUBSECS_FIELD, COMMON_PACKET_SEQUENCE_COUNT_FIELD, 
                               'PACKET_TIMESECONDS', 'PACKET_TIMEFORMATTED', 'RECEIVED_TIMESECONDS', 
                               'RECEIVED_TIMEFORMATTED', 'RECEIVED_COUNT']
    
    # Start the report
    print(f"\n>>> {'*':*^130}")
    print(f">>> {'Initial' if(current_packet.get('Num_Updates_Run') == 1) else 'Changes since last'} "
          f"{target_name} {packet_name} Telemetry Report")
    print(f">>> {' CCSDS Header and COSMOS derived points ':-^130}")
    print(">>>")
    
    # Print header information differently for initial vs. update reports
    if current_packet.get('Num_Updates_Run') == 1:
        # Initial packet report
        for field in [COMMON_PACKET_TIME_SECONDS_FIELD, COMMON_PACKET_TIME_SUBSECS_FIELD, 'PACKET_TIMEFORMATTED', COMMON_PACKET_SEQUENCE_COUNT_FIELD,
                     'RECEIVED_TIMEFORMATTED', 'RECEIVED_COUNT']:
            if field in current_packet:
                print(f">>> {field.replace('_', ' '):<35} : {current_packet.get(field):>23}")
    else:
        # Update report with changes
        for field, label, delta_var in [
            (COMMON_PACKET_TIME_SECONDS_FIELD, COMMON_PACKET_TIME_SECONDS_DESC, secs_delta),
            (COMMON_PACKET_TIME_SUBSECS_FIELD, COMMON_PACKET_TIME_SUBSECS_DESC, subsecs_delta),
            ('PACKET_TIMEFORMATTED', 'DERIVED Packet Time Formatted', pkt_time_sec_delta),
            (COMMON_PACKET_SEQUENCE_COUNT_FIELD, COMMON_PACKET_SEQUENCE_DESC, seq_delta),
            ('RECEIVED_TIMEFORMATTED', 'COSMOS Received Time', rec_time_sec_delta),
            ('RECEIVED_COUNT', 'COSMOS Received Count', cosmos_rec_cnt_delta)
        ]:
            if field in previous_packet and field in current_packet:
                print(f">>> {label:<35} : {previous_packet.get(field):>23} --> "
                      f"{current_packet.get(field):>23} ==> Delta since last packet: {delta_var} ")
        
        # Print rate information if relevant
        if 'RECEIVED_COUNT' in current_packet and 'RECEIVED_COUNT' in previous_packet:
            if cosmos_rec_cnt_delta > 0:
                rate = float(rec_time_sec_delta) / cosmos_rec_cnt_delta
                print(f">>>  Calculated Rate based on COSMOS derived data = {rate} pkts/sec. "
                      f"(rounded to 4 significant digits: {rate:.4f} pkts/sec)")
            else:
                print(">>>  <!> No new Packet was received ")
            
            if seq_delta > 0:
                rate = float(pkt_time_sec_delta) / seq_delta
                print(f">>>  Calculated Rate based on CCSDS header data = {rate} pkts/sec. "
                      f"(rounded to 4 significant digits: {rate:.4f} pkts/sec)")
                if all(field in current_packet for field in ['RECEIVED_TIMEFORMATTED', 'PACKET_TIMEFORMATTED']):
                    if str(current_packet.get('RECEIVED_TIMEFORMATTED')) == str(current_packet.get('PACKET_TIMEFORMATTED')):
                        print(">>>  <!> PACKET_TIMESECONDS and PACKET_TIMEFORMATTED need to be fixed to be calculated from the CCSDS header,")
                        print(">>>      not mirror COSMOS received time data")
    
    # Print the telemetry values section
    print(">>>")
    printstr = f" {target_name} {packet_name} Telemetry "
    print(f">>> {printstr:-^130}")
    print(">>>")
    
    # Get all keys from the current packet
    packet_keys = current_packet.keys()
    
    if current_packet.get('Num_Updates_Run') == 1:
        # Initial packet - just print values
        for tlm_point in packet_keys:
            if (level_of_detail == 0 and tlm_point not in tlm_to_exclude_in_lvl_0) or \
               (level_of_detail != 0 and tlm_point not in tlm_to_exclude):
                print(f">>> {tlm_point:<35} : {str(current_packet.get(tlm_point)):>16}")
    else:
        # Update packet - print changes
        for tlm_point in packet_keys:
            if level_of_detail == 0 and tlm_point not in tlm_to_exclude_in_lvl_0:
                if tlm_point in previous_packet:
                    delta_txt = "<---" if (previous_packet.get(tlm_point) != current_packet.get(tlm_point)) else ""
                    if delta_txt == "<---":
                        print(f">>> {tlm_point:<35} : {str(previous_packet.get(tlm_point)):>16} --> "
                              f"{str(current_packet.get(tlm_point)):>16} {delta_txt}")
            elif level_of_detail != 0 and tlm_point not in tlm_to_exclude:
                if tlm_point in previous_packet:
                    delta_txt = "<---" if (previous_packet.get(tlm_point) != current_packet.get(tlm_point)) else ""
                    print(f">>> {tlm_point:<35} : {str(previous_packet.get(tlm_point)):>16} --> "
                          f"{str(current_packet.get(tlm_point)):>16} {delta_txt}")
    
    # End the report
    print(">>>")
    print(f">>> {'-':-^130}")


def report_all_telemetry(
    target_name: str,
    level_of_detail: int = 0,
    exclude_packets: Optional[List[str]] = None
) -> None:
    """Report changes for all telemetry packets from a specific target.
    
    This function:
    1. Gets a list of all telemetry packet names for the specified target
    2. Calls report_telemetry for each packet
    
    Args:
        target_name: COSMOS Target name
        level_of_detail: Detail level for reporting (0=changes only, other=all values)
        exclude_packets: List of packet names to exclude from reporting
    """
    # Import and use the COSMOS get_all_tlm_names function
    from openc3.script import get_all_tlm_names
    
    # Initialize exclude_packets to empty list if not provided
    if exclude_packets is None:
        exclude_packets = []
    
    # Get all telemetry packet names for this target
    packet_names = get_all_tlm_names(target_name)
    
    print(f"\n>>> {'*':*^130}")
    print(f">>> Reporting changes for all {target_name} telemetry packets")
    print(f">>> {'*':*^130}")
    
    # Process each packet
    for packet_name in packet_names:
        # Skip excluded packets
        if packet_name in exclude_packets:
            print(f"\n>>> Skipping excluded packet: {target_name} {packet_name}")
            continue
            
        try:
            # Report changes for this packet
            print(f"\n>>> Processing packet: {target_name} {packet_name}")
            report_telemetry(target_name, packet_name, level_of_detail)
        except Exception as e:
            print(f"\n>>> ERROR processing packet {target_name} {packet_name}: {str(e)}")
    
    print(f"\n>>> {'*':*^130}")
    print(f">>> Completed report of all {target_name} telemetry packets")
    print(f">>> {'*':*^130}")


def report_all_targets_telemetry(
    level_of_detail: int = 0,
    exclude_targets: Optional[List[str]] = None,
    exclude_packets: Optional[List[str]] = None
) -> None:
    """Report changes for all telemetry packets from all targets.
    
    This function:
    1. Gets a list of all target names defined in the system
    2. Calls report_all_telemetry for each target
    
    Args:
        level_of_detail: Detail level for reporting (0=changes only, other=all values)
        exclude_targets: List of target names to exclude from reporting
        exclude_packets: List of packet names to exclude from reporting
    """
    # Import and use the COSMOS get_target_list function
    from openc3.script import get_target_list
    
    # Initialize exclude lists if not provided
    if exclude_targets is None:
        exclude_targets = []
    if exclude_packets is None:
        exclude_packets = []
    
    # Get all target names
    targets = get_target_list()
    
    print(f"\n>>> {'*':*^130}")
    print(f">>> Reporting changes for all telemetry packets across all targets")
    print(f">>> {'*':*^130}")
    
    # Process each target
    for target_name in targets:
        # Skip excluded targets
        if target_name in exclude_targets:
            print(f"\n>>> Skipping excluded target: {target_name}")
            continue
            
        try:
            # Report changes for all packets in this target
            print(f"\n>>> Processing target: {target_name}")
            report_all_telemetry(
                target_name, 
                level_of_detail=level_of_detail,
                exclude_packets=exclude_packets
            )
        except Exception as e:
            print(f"\n>>> ERROR processing target {target_name}: {str(e)}")
    
    print(f"\n>>> {'*':*^130}")
    print(f">>> Completed report of all telemetry packets across all targets")
    print(f">>> {'*':*^130}")