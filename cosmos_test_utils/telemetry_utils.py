# NASA Docket No. GSC-19606-1, and identified as Test Utilities Python
# package to facilitate testing software with the open source COSMOS
# ground system"
#
# Copyright (c) 2025 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utilities for tracking and reporting telemetry changes in COSMOS tests."""


import copy
from openc3.script import get_tlm_packet
from typing import Dict, List, Any, Optional
from .wait_utils import wait_for_sequence_count_change, wait_multiple_telemetry
from .system_config import (
    COMMON_PACKET_FIELDS,
    DERIVED_PACKET_FIELDS,
    RATE_CALC_CCSDS_SECONDS_FIELD,
    RATE_CALC_CCSDS_SUBSECS_FIELD,
    RATE_CALC_CCSDS_SEQUENCE_FIELD,
    RATE_CALC_COSMOS_TIMESECONDS_FIELD,
    RATE_CALC_COSMOS_COUNT_FIELD,
    DERIVED_PACKET_TIMEFORMATTED_FIELD,
    DERIVED_RECEIVED_TIMEFORMATTED_FIELD,
    HEADER_VALUE_COLUMN_WIDTH,
    DERIVED_VALUE_COLUMN_WIDTH,
    TELEMETRY_VALUE_COLUMN_WIDTH
)

# Global storage for telemetry tracking
prev_vals: Dict[str, Dict[str, Dict[str, Any]]] = {}
current_vals: Dict[str, Dict[str, Dict[str, Any]]] = {}

def get_tlm_point(target: str, packet: str, item: str, type: str = 'CONVERTED') -> Any:
    """
    Get a single telemetry point from COSMOS.
    Never waits for a new packet. Returns the value immediately

    This function is a wrapper for the COSMOS tlm function, allowing easy access
    to individual telemetry points with a simpler interface.

    Args:
        target (str): Name of the target of the telemetry item.
        packet (str): Name of the telemetry packet of the telemetry item.
        item (str): Name of the telemetry item.
        type (str, optional): Type of telemetry value to return. 
                              Options are 'RAW', 'CONVERTED', or 'FORMATTED'.
                              Defaults to 'CONVERTED'.

    Returns:
        Any: The value of the requested telemetry point. The type can vary
             depending on the nature of the telemetry item and the requested
             type (raw, converted, or formatted).

    Raises:
        ValueError: If an invalid type is specified.

    Example:
        value = get_tlm_point("INST", "HEALTH_STATUS", "COLLECTS")
        raw_value = get_tlm_point("INST", "HEALTH_STATUS", "COLLECTS", type='RAW')
        formatted_value = get_tlm_point("INST", "HEALTH_STATUS", "COLLECTS", type='FORMATTED')
    """
    # Import the COSMOS tlm function
    from openc3.script import tlm

    # Validate the type parameter
    valid_types = ['RAW', 'CONVERTED', 'FORMATTED']
    if type.upper() not in valid_types:
        raise ValueError(f"Invalid type '{type}'. Must be one of: {', '.join(valid_types)}")

    # Call the COSMOS tlm function and return the result
    return tlm(f"{target} {packet} {item}", type=type.upper())


def get_telemetry_values(
    target_name: str, 
    packet_name: str, 
    num_items: Optional[int] = None,
    wait_for_new_packet: bool = True,
    filter_tlm: bool = True
) -> Any:
    """
    Retrieve current telemetry item contents in the order they are defined for a specified packet.
    
    Args:
        target_name: Name of the target.
        packet_name: Name of the telemetry packet.
        num_items: Number of telemetry items to retrieve. If None, retrieves all items.
        wait_for_new_packet: Whether to wait for a new telemetry packet or not (default: True).
        filter_tlm: Whether to filter out the header and derived tlm items from the return(default: True)
    
    Returns:
        list: List of telemetry item contents in the order they are defined.
    
    Example:
        # Get all telemetry values
        all_values = get_telemetry_values("CFS-1", "CFE_ES_HK")
        # Get only the first 5 telemetry values
        first_five = get_telemetry_values("CFS-1", "CFE_ES_HK", num_items=5)
        # Get values without waiting for a new packet
        current_values = get_telemetry_values("CFS-1", "CFE_ES_HK", wait_for_new_packet=False)
    """
    if num_items is not None and num_items <= 0:
        raise ValueError("num_items must be a positive integer or None")
    
    if wait_for_new_packet:
        new_packet = wait_for_sequence_count_change(target_name, packet_name)
        if not new_packet:
            print(f" <!> Warning: Did not receive new {target_name} {packet_name} telemetry packet")
    
    try:
        # Get all telemetry points for this packet
        all_tlm_points = get_tlm_packet(f"{target_name} {packet_name}", type='RAW')
    except Exception as e:
        raise RuntimeError(f"Unable to retrieve telemetry packet: {str(e)}")
    
    # Filter out header and derived fields if requested
    if filter_tlm:
        # Get field names from tuples
        common_field_names = [field[0] for field in COMMON_PACKET_FIELDS]
        derived_field_names = [field[0] for field in DERIVED_PACKET_FIELDS]
        
        filtered_tlm_points = [
            point for point in all_tlm_points 
            if point[0] not in common_field_names and point[0] not in derived_field_names
        ]
    else:
        filtered_tlm_points = all_tlm_points
    
    # Extract only the values, not the names
    values = [point[1] for point in filtered_tlm_points]
    
    # If num_items is specified and less than total items, return only requested number
    if num_items is not None:
        result = values[:num_items]
        return result[0] if num_items == 1 else result
    else:
        return values


def validate_telemetry(
    expected_conditions: List[Any],
    timeout: Optional[float] = None
) -> bool:
    """
    Validate multiple telemetry conditions (or a single condition).
    
    Args:
        expected_conditions: Single condition or list of conditions to validate.
                             Single condition format: [target, packet, item, comparison (optional), expected_value]
                             Multiple conditions format: [[target, packet, item, comparison (optional), expected_value], ...]
                             See examples.
        timeout: Maximum wait time in seconds (default: None, uses system_config value)
    
    Valid comparison operators:
        "==", "!=", "<", "<=", ">", ">=", "contains", "does_not_contain"
    
    Returns:
        bool: True if all conditions are met, False otherwise
    
    Raises:
        ValueError: If any condition in expected_conditions is invalid
    
    Example:
        # Single condition (no outer list needed)
        success = validate_telemetry(
            ['TARGET', 'HK_TLM_PK', 'COMMAND_COUNTER', 5]
        )
        
        # Multiple conditions
        success = validate_telemetry([
            ['TARGET', 'HK_TLM_PK', 'MODE', 'SAFE'],
            ['TARGET', 'HK_TLM_PK', 'BATTERY', '>=', 75]
        ])
        
        # Single condition with comparison operator
        success = validate_telemetry(
            ['TARGET', 'HEALTH_TLM', 'TEMPERATURE', '<', 30]
        )
        
        # Building expected_conditions variable
        expected_conditions = [
            ['TARGET', 'HEALTH_TLM', 'TEMPERATURE', '<', 30],
            ['TARGET', 'HEALTH_TLM', 'POWER_STATUS', 'ON']
        ]
        validation_result = validate_telemetry(expected_conditions)
    
    Note: You do not need to match the Targets. 
        If you have multiple targets you can have the function validate items across all relevant targets
    """
    # Validate expected_conditions
    if not expected_conditions or not isinstance(expected_conditions, list):
        raise ValueError("expected_conditions must be a non-empty list")
    
    # Check if this is a single condition (first element is a string - the target name)
    # vs multiple conditions (first element is a list)
    if isinstance(expected_conditions[0], str):
        # Single condition - wrap it in a list
        conditions_to_check = [expected_conditions]
    else:
        # Multiple conditions - use as-is
        conditions_to_check = expected_conditions
    
    # Use wait_multiple_telemetry to check conditions
    success, _ = wait_multiple_telemetry(
        conditions_to_check,
        timeout=timeout
    )
    
    return success


def _format_value(value: Any, format_type: str, width: int) -> str:
    """Format a telemetry value according to its specified format type.
    
    Args:
        value: The value to format
        format_type: The format type ('hex', 'dec', 'float', 'time', 'string')
        width: The width to right-justify the formatted value
    
    Returns:
        The formatted and right-justified string
    """
    if value is None:
        return str(None).rjust(width)
    
    if format_type == 'hex':
        if isinstance(value, int):
            formatted = f"0x{value:04X}"
        else:
            formatted = str(value)
    elif format_type == 'dec':
        formatted = str(int(value))
    elif format_type == 'float':
        formatted = str(float(value))
    elif format_type in ['time', 'string']:
        formatted = str(value)
    else:
        # Default to hex if format type not recognized
        if isinstance(value, int):
            formatted = f"0x{value:04X}"
        else:
            formatted = str(value)
    
    # Right-justify to width
    return formatted.rjust(width)


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
        current_vals[target_name][packet_name]["Header_Field_Width"] = 0
        current_vals[target_name][packet_name]["Telemetry_Field_Width"] = 0
    
    # Copy current values to previous values, this initializes prev_vals if this is the first time seeing this packet
    prev_vals = copy.deepcopy(current_vals)
    
    # Update the run counter
    current_vals[target_name][packet_name]["Num_Updates_Run"] += 1
    
    # Get all telemetry points for this packet
    all_tlm_points = get_tlm_packet(f"{target_name} {packet_name}", type='RAW')
    
    # Calculate field widths on first run
    if current_vals[target_name][packet_name]["Num_Updates_Run"] == 1:
        # Get field names from configuration
        common_field_names = [field[0] for field in COMMON_PACKET_FIELDS]
        derived_field_names = [field[0] for field in DERIVED_PACKET_FIELDS]
        
        # Get telemetry field names (excluding common and derived)
        exclude_fields = common_field_names + derived_field_names + ["Num_Updates_Run", "Header_Field_Width", "Telemetry_Field_Width"]
        telemetry_field_names = [point[0] for point in all_tlm_points if point[0] not in exclude_fields]
        
        # Calculate max widths for header/derived and telemetry
        header_width = 0
        if common_field_names:
            header_width = max(header_width, max(len(name) for name in common_field_names))
        if derived_field_names:
            header_width = max(header_width, max(len(name) for name in derived_field_names))
        
        telemetry_width = 0
        if telemetry_field_names:
            telemetry_width = max(len(name) for name in telemetry_field_names)
        
        # Account for indentation differences to align colons
        # Header/derived have ">>>   " (6 chars) before field name
        # Telemetry has ">>> " (4 chars) before field name
        # This means header/derived fields effectively have length + 2
        # To align colons: telemetry_width = header_width + 2
        
        # The "effective length" concept:
        # - Header/derived effective length = actual_length + 2 (due to indent)
        # - Telemetry effective length = actual_length
        # We want the longest effective length to have exactly 1 space before colon
        
        # Compare effective lengths
        header_effective_length = header_width + 2
        telemetry_effective_length = telemetry_width
        
        if header_effective_length >= telemetry_effective_length:
            # Header/derived has longest effective length (or equal)
            # Give header exactly 1 space, telemetry will have more
            current_vals[target_name][packet_name]["Header_Field_Width"] = header_width
            current_vals[target_name][packet_name]["Telemetry_Field_Width"] = header_width + 2
        else:
            # Telemetry has longest effective length
            # Give telemetry exactly 1 space, header will have more
            current_vals[target_name][packet_name]["Telemetry_Field_Width"] = telemetry_width
            current_vals[target_name][packet_name]["Header_Field_Width"] = telemetry_width - 2
    
    # Store each telemetry point in the current_vals dictionary
    for tlm_point in all_tlm_points:
        current_vals[target_name][packet_name][tlm_point[0]] = tlm_point[1]


def report_telemetry(
    target_name: str,
    packet_name: str,
    level_of_detail: int = 0,
    display_as_initial: bool = False
) -> None:
    """Report changes in telemetry between current and previous values.
    
    Args:
        target_name: COSMOS Target name
        packet_name: COSMOS Telemetry packet name
        level_of_detail: Detail level for reporting (0=changes only, other=all values)
    
    This displays a formatted report showing:
    - Header fields with format specifications from COMMON_PACKET_FIELDS
    - Derived fields with format specifications from DERIVED_PACKET_FIELDS
    - Packet rate calculations (CCSDS and COSMOS)
    - Changed telemetry values (or all values if level_of_detail > 0)
    - Change indicators (<---) for values that have changed
    - Warnings when no new packet received or no changes detected
    """
    global current_vals
    global prev_vals
    
    # Update telemetry values first
    _update_telemetry_values(target_name, packet_name)
    
    current_packet = current_vals[target_name][packet_name]
    previous_packet = prev_vals[target_name][packet_name]
    
    # Reset to initial state if requested
    if display_as_initial:
        current_vals[target_name][packet_name]["Num_Updates_Run"] = 1
    
    is_first_run = (current_packet.get('Num_Updates_Run') == 1)
    
    # Get the field widths
    header_field_width = current_packet.get("Header_Field_Width", 25)
    telemetry_field_width = current_packet.get("Telemetry_Field_Width", 25)
    
    # Get value column widths from config
    header_value_width = HEADER_VALUE_COLUMN_WIDTH
    derived_value_width = DERIVED_VALUE_COLUMN_WIDTH
    telemetry_value_width = TELEMETRY_VALUE_COLUMN_WIDTH
    
    # Start the report
    print(f"\n>>> {'*':*^130}")
    print(f">>> {'Initial' if is_first_run else 'Changes since last'} "
          f"{target_name} {packet_name} Telemetry Report")
    print(f">>> {f' {target_name} {packet_name} Packet Header and COSMOS derived points ':-^130}")
    print(">>>")
    
    # ====================================================================================
    # PACKET HEADER SECTION
    # ====================================================================================
    if is_first_run:
        print(">>> Packet Header:")
        for field_name, format_type in COMMON_PACKET_FIELDS:
            if field_name in current_packet:
                formatted_value = _format_value(current_packet[field_name], format_type, header_value_width)
                print(f">>>   {field_name:<{header_field_width}} : {formatted_value}")
    else:
        # Changes report - show old and new with change indicators
        print(">>> Packet Header:")
        print(f">>>   {'Old':>{header_field_width + header_value_width + 3}} {'New':>{header_value_width + 4}}")
        
        for field_name, format_type in COMMON_PACKET_FIELDS:
            if field_name in current_packet and field_name in previous_packet:
                old_value = _format_value(previous_packet[field_name], format_type, header_value_width)
                new_value = _format_value(current_packet[field_name], format_type, header_value_width)
                
                # Check if value changed
                changed = (previous_packet[field_name] != current_packet[field_name])
                change_marker = " <---" if changed else ""
                
                print(f">>>   {field_name:<{header_field_width}} : {old_value} --> {new_value}{change_marker}")
        
        print(">>>")
        
        # Calculate and display CCSDS packet rate if we have the necessary fields
        if all(field in current_packet and field in previous_packet for field in 
               [RATE_CALC_CCSDS_SECONDS_FIELD, RATE_CALC_CCSDS_SUBSECS_FIELD, RATE_CALC_CCSDS_SEQUENCE_FIELD]):
            
            seq_delta = int(current_packet[RATE_CALC_CCSDS_SEQUENCE_FIELD]) - int(previous_packet[RATE_CALC_CCSDS_SEQUENCE_FIELD])
            
            if seq_delta > 0:
                # Calculate time delta including subseconds
                secs_delta = int(current_packet[RATE_CALC_CCSDS_SECONDS_FIELD]) - int(previous_packet[RATE_CALC_CCSDS_SECONDS_FIELD])
                subsecs_delta = int(current_packet[RATE_CALC_CCSDS_SUBSECS_FIELD]) - int(previous_packet[RATE_CALC_CCSDS_SUBSECS_FIELD])
                
                # Convert subseconds to seconds (assuming subseconds is in 2^-32 units like cFS)
                # Adjust this conversion if your system uses different subsecond units
                time_delta = secs_delta + (subsecs_delta / (2**32))
                
                rate = time_delta / seq_delta
                print(f">>>  Calculated Packet Rate: 1 every {rate} seconds")
            elif seq_delta == 0:
                print(f">>>  <!> No new Packet was received")
        
    print(">>>")
    
    # ====================================================================================
    # DERIVED FIELDS SECTION
    # ====================================================================================
    if is_first_run:
        print(">>> COSMOS Derived Points:")
        for field_name, format_type in DERIVED_PACKET_FIELDS:
            if field_name in current_packet:
                formatted_value = _format_value(current_packet[field_name], format_type, derived_value_width)
                print(f">>>   {field_name:<{header_field_width}} : {formatted_value}")
    else:
        # Changes report - show old and new with change indicators
        print(">>> COSMOS Derived Points:")
        print(f">>>   {'Old':>{header_field_width + derived_value_width + 3}} {'New':>{derived_value_width + 4}}")
        
        for field_name, format_type in DERIVED_PACKET_FIELDS:
            if field_name in current_packet and field_name in previous_packet:
                old_value = _format_value(previous_packet[field_name], format_type, derived_value_width)
                new_value = _format_value(current_packet[field_name], format_type, derived_value_width)
                
                # Check if value changed
                changed = (previous_packet[field_name] != current_packet[field_name])
                change_marker = " <---" if changed else ""
                
                print(f">>>   {field_name:<{header_field_width}} : {old_value} --> {new_value}{change_marker}")
        
        print(">>>")
        
        # Calculate and display COSMOS packet rate if we have the necessary fields
        if all(field in current_packet and field in previous_packet for field in 
               [RATE_CALC_COSMOS_TIMESECONDS_FIELD, RATE_CALC_COSMOS_COUNT_FIELD]):
            
            count_delta = int(current_packet[RATE_CALC_COSMOS_COUNT_FIELD]) - int(previous_packet[RATE_CALC_COSMOS_COUNT_FIELD])
            
            if count_delta > 0:
                time_delta = float(current_packet[RATE_CALC_COSMOS_TIMESECONDS_FIELD]) - float(previous_packet[RATE_CALC_COSMOS_TIMESECONDS_FIELD])
                rate = time_delta / count_delta
                print(f">>>  Calculated Packet Rate: 1 every {rate} seconds")
            elif count_delta == 0:
                print(f">>>  <!> No new Packet was received")
        
        # Check if PACKET_TIMEFORMATTED and RECEIVED_TIMEFORMATTED are the same (indicates misconfiguration)
        if DERIVED_PACKET_TIMEFORMATTED_FIELD in current_packet and DERIVED_RECEIVED_TIMEFORMATTED_FIELD in current_packet:
            if str(current_packet[DERIVED_PACKET_TIMEFORMATTED_FIELD]) == str(current_packet[DERIVED_RECEIVED_TIMEFORMATTED_FIELD]):
                print(f">>>  <!> {DERIVED_PACKET_TIMEFORMATTED_FIELD} needs to be fixed to be calculated from the header time-stamp,")
                print(f">>>      not mirror {DERIVED_RECEIVED_TIMEFORMATTED_FIELD}")
    
    # ====================================================================================
    # TELEMETRY VALUES SECTION
    # ====================================================================================
    print(">>>")
    printstr = f" {target_name} {packet_name} Telemetry "
    print(f">>> {printstr:-^130}")
    print(">>>")
    
    # Get all keys from the current packet, excluding special tracking fields and header/derived fields
    common_field_names = [field[0] for field in COMMON_PACKET_FIELDS]
    derived_field_names = [field[0] for field in DERIVED_PACKET_FIELDS]
    exclude_fields = common_field_names + derived_field_names + ["Num_Updates_Run", "Header_Field_Width", "Telemetry_Field_Width"]
    
    # Get telemetry field names (everything except excluded fields)
    tlm_field_names = [key for key in current_packet.keys() if key not in exclude_fields]
    
    # Build telemetry output as a list first (like generate_requirements_report)
    telemetry_lines = []
    telemetry_changed = False
    
    if is_first_run:
        # Initial packet - just build values
        if not tlm_field_names:
            telemetry_lines.append(">>>   (No telemetry items in this packet)")
        else:
            for tlm_point in tlm_field_names:
                formatted_value = str(current_packet[tlm_point]).rjust(telemetry_value_width)
                telemetry_lines.append(f">>> {tlm_point:<{telemetry_field_width}} : {formatted_value}")
    else:
        # Changes report - build header and values
        telemetry_lines.append(f">>> {'Old':>{telemetry_field_width + telemetry_value_width + 3}} {'New':>{telemetry_value_width + 4}}")
        
        if not tlm_field_names:
            telemetry_lines.append(">>>   (No telemetry items in this packet)")
        else:
            for tlm_point in tlm_field_names:
                if tlm_point in previous_packet:
                    old_val = previous_packet[tlm_point]
                    new_val = current_packet[tlm_point]
                    
                    # Check if value changed
                    changed = (old_val != new_val)
                    if not telemetry_changed and changed:
                        telemetry_changed = True
                    
                    # Only add to output if level_of_detail > 0 or if value changed
                    if level_of_detail > 0 or changed:
                        old_value_str = str(old_val).rjust(telemetry_value_width)
                        new_value_str = str(new_val).rjust(telemetry_value_width)
                        change_marker = " <---" if changed else ""
                        
                        telemetry_lines.append(f">>> {tlm_point:<{telemetry_field_width}} : {old_value_str} --> {new_value_str}{change_marker}")
    
    # Print the note if no telemetry changed, then print all telemetry lines
    if not is_first_run and not telemetry_changed:
        print(">>>    NOTE: No Telemetry Changed Since Last Report")
        print(">>>")
    
    # Print all telemetry lines
    print("\n".join(telemetry_lines))
    
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