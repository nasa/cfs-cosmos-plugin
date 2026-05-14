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

"""Utilities for working with event messages in COSMOS tests.

This module provides functions for managing event logging in a way that
prevents multiple logging sessions from being started and interfering with each other.

The background logging system ensures that:

1. Only one background logging session can be active at a time.
2. Attempting to starting a new logging session when one is already active will not create a new session.
3. Stopping a logging session will only occur if the provided name matches the active session.
"""

from openc3.script import script_create, script_run, running_script_stop, stash_set, stash_get
from typing import Optional, Tuple, Union, List
import time
from .system_config import (
    EVENT_PACKET_NAME,
    EVENT_TYPE_TO_TXT,
    EVENT_TXT_TO_TYPE,
    EVENT_BLOCK_TIMEOUT,
    EVENT_APP_FIELD,
    EVENT_ID_FIELD,
    EVENT_TYPE_FIELD,
    EVENT_MESSAGE_FIELD,
    EVENT_SCID_FIELD,
    EVENT_PROCID_FIELD,
    DERIVED_PACKET_TIMEFORMATTED_FIELD,
    LOGGER_INIT_WAIT_TIME
)

# Module-level variables to store event subscription IDs
_event_search_id = None   # For find_events
_event_logging_id = None  # For print_events_to_log
_event_packets = []  # To store packets for multiple find_events calls


def set_event_search_point(target_names: Union[str, List[str]]) -> str:
    """
    Set the point that a find_events call will search back to.
    
    This function subscribes to event packets for one or more targets and stores 
    the subscription ID at the module level, so it can be used by find_events 
    without requiring the ID to be passed in each time.
    
    Note: This function should be called multiple times. Each time it's called,
    it resets the point at which future find_events calls will begin searching.
    This is useful to narrow searches to specific sections of a test.
    
    Args:
        target_names: COSMOS target name(s) for events. Can be:
                     - str: Single target name
                     - List[str]: List of target names
    
    Returns:
        The subscription ID (also stored internally for use by find_events)
    
    Examples:
        set_event_search_point("TARGET1")  # Single target
        set_event_search_point(["TARGET1", "TARGET2"])  # Multiple targets
    """
    global _event_search_id, _event_packets
    
    # Import and use the COSMOS subscribe_packets function
    from openc3.script import subscribe_packets
    
    # Normalize input to list of targets
    if isinstance(target_names, str):
        targets = [target_names]
    elif isinstance(target_names, list):
        if not all(isinstance(target, str) for target in target_names):
            raise ValueError("All items in the target list must be strings.")
        targets = target_names
    else:
        raise ValueError("Invalid target_name type. Expected str or List[str]")
    
    # Reset the stored packets when setting a new search point
    _event_packets = []
    
    # Prepare subscription list
    subscription_list = [[target, EVENT_PACKET_NAME] for target in targets]
    
    # Subscribe to event packets
    _event_search_id = subscribe_packets(subscription_list)
    
    print(f" --> Event search point set for {", ".join(targets)}")
    
    return _event_search_id


def find_events(
    target: str,
    app_name: str,
    event_id: int,
    event_type: str,
    partial_message_text: str,
    expected_num_found: int = 1,
    subscription_id: Optional[str] = None
) -> Union[Tuple[bool, int], Tuple[bool, int, str]]:
    """Find specific events in the event message stream.
    
    Before using this function with the default subscription_id=None,
    you must call set_event_search_point() to set up the event subscription.
    
    Args:
        target: Target name to filter by
        app_name: Application name to filter by
        event_id: Event ID to filter by
        event_type: Event type ('DEBUG', 'INFO', 'ERROR', 'CRIT')
        partial_message_text: Text to search for in the event message
        expected_num_found: Number of matching events expected (default: 1)
        subscription_id: Optional specific subscription ID to use
                        (default: None, which uses the module-level ID)
    
    Returns:
        If subscription_id is None:
            Tuple containing:
              - bool: True if the expected number of events were found
              - int: Number of events found
        If subscription_id is provided:
            Tuple containing:
              - bool: True if the expected number of events were found
              - int: Number of events found
              - int: Updated subscription ID to use in future calls
    
    Raises:
        RuntimeError: If subscription_id=None and set_event_search_point() has not been called
    """
    global _event_search_id, _event_packets
    
    # Determine which subscription ID to use
    if subscription_id is None:
        # Use the module-level ID
        if _event_search_id is None:
            raise RuntimeError(
                "Event search subscription not initialized in cosmos_test_utils.event_utils. "
                "You must call set_event_search_point() before using find_events() "
                "to set up event packet subscriptions. "
                "Add this to your script:\n\n"
                "    from cosmos_test_utils import set_event_search_point\n"
                "    set_event_search_point()  # Call this to start event searching\n\n"
                "Alternatively, you can provide a specific subscription_id parameter to this function from a separate COSMOS subscribe_packets() call."
            )
        search_id = _event_search_id
    else:
        # Use the user-provided ID
        search_id = subscription_id
    
    # Import and use the COSMOS get_packets function
    from openc3.script import get_packets
        
    num_found = 0
    num_searched = 0
    
    # Print search details
    print(f"Searching for {expected_num_found} event(s) with details:")
    print(f"  Target: {target}")
    print(f"  App: {app_name}")
    print(f"  ID: {event_id}")
    print(f"  Type: {event_type}")
    print(f"  Partial text: '{partial_message_text}'")
    
    # Get all packets since the last time this method was called
    # Block time is configured in system_config.py
    search_id, new_packets = get_packets(search_id, block=EVENT_BLOCK_TIMEOUT)
    
    # Append new packets to the stored packets
    _event_packets.extend(new_packets)
    
    # If we're using the module-level ID, update it
    if subscription_id is None:
        _event_search_id = search_id
    
    for packet in _event_packets:
        num_searched += 1
        if (packet['target_name'] == target and
            packet[EVENT_APP_FIELD] == app_name and
            packet[EVENT_ID_FIELD] == event_id and
            packet[EVENT_TYPE_FIELD] == EVENT_TXT_TO_TYPE[event_type] and
            partial_message_text in packet[EVENT_MESSAGE_FIELD]):
            num_found += 1
    
    print(f"{'<*>' if num_found == expected_num_found else '<!>'} "
          f"Event message(s) {'found' if num_found == expected_num_found else '-NOT- found'}. "
          f"Searched {num_searched} and found {num_found} of target ({expected_num_found})")
    
    # Return the updated subscription ID along with results if user provided one
    if subscription_id is not None:
        return (num_found == expected_num_found, num_found, search_id)
    else:
        return (num_found == expected_num_found, num_found)


def capture_events_for_script_logging(target_names: Union[str, List[str]]) -> str:
    """
    Subscribe to event packets for script logging.
    
    This function subscribes to event packets from one or more targets and stores 
    the subscription ID at the module level, so it can be used by print_events_to_log 
    without requiring the ID to be passed in each time.
    
    Note: This function should only be called once at the beginning of a test.
    Calling it multiple times may overwrite previous subscriptions.
    
    Args:
        target_names: COSMOS target name(s) for events. Can be:
                     - str: Single target name
                     - List[str]: List of target names
    
    Returns:
        The subscription ID (also stored internally for use by print_events_to_log)
    
    Examples:
        capture_events_for_script_logging("TARGET1")  # Single target
        capture_events_for_script_logging(["TARGET1", "TARGET2"])  # Multiple targets
    
    Raises:
        ValueError: If target_names is not str or List[str], or if any item in the list is not a string.
    """
    global _event_logging_id
    
    # Import and use the COSMOS subscribe_packets function
    from openc3.script import subscribe_packets
    
    # Normalize input to list of targets
    if isinstance(target_names, str):
        targets = [target_names]
    elif isinstance(target_names, list):
        if not all(isinstance(target, str) for target in target_names):
            raise ValueError("All items in the target list must be strings.")
        targets = target_names
    else:
        raise ValueError("Invalid target_name type. Expected str or List[str]")
    
    # Prepare subscription list
    subscription_list = [[target, EVENT_PACKET_NAME] for target in targets]
    
    # Check if there's an existing subscription
    if _event_logging_id is not None:
        print(" <!> Warning: A previous call to capture_events_for_script_logging was made. "
              "This new subscription may overwrite the previous one.")
    
    # Subscribe to event packets
    _event_logging_id = subscribe_packets(subscription_list)
    
    return _event_logging_id


def print_events_to_log(
    log_id: Optional[int] = None,
    use_group_print: bool = False
) -> Optional[int]:
    """Print all received event messages to the test log since the last call.
    
    Before using this function with the default log_id=None,
    you must call capture_events_for_script_logging() to set up the event subscription.
    
    Args:
        log_id: Optional specific subscription ID to use
               (default: None, which uses the module-level ID)
        use_group_print: If True, use Group.print; if False, use built-in print
        
    Returns:
        Optional[int]: Updated subscription ID if a specific log_id was provided
        
    Raises:
        RuntimeError: If log_id=None and capture_events_for_script_logging() has not been called
    """
    global _event_logging_id
    
    # Determine which subscription ID to use
    if log_id is None:
        # Use the module-level ID
        if _event_logging_id is None:
            raise RuntimeError(
                "Event logging subscription not initialized in cosmos_test_utils.event_utils. "
                "You must call capture_events_for_script_logging() before using print_events_to_log() "
                "or other functions that depend on event logging (like test_print). "
                "Add this to your script:\n\n"
                "    from cosmos_test_utils import capture_events_for_script_logging\n"
                "    capture_events_for_script_logging()  # Call this once at the start of your test\n\n"
                "Alternatively, you can provide a specific log_id parameter to this function from a separate COSMOS subscribe_packets() call."
            )
        current_log_id = _event_logging_id
    else:
        # Use the user-provided ID
        current_log_id = log_id
    
    # Determine print function
    if use_group_print:
        from openc3.script.suite import Group
        print_func = Group.print
    else:
        print_func = print

    # Import and use the COSMOS get_packets function
    from openc3.script import get_packets
    
    # Get all packets since the last time this method was called
    current_log_id, packets = get_packets(current_log_id)
    
    # If we're using the module-level ID, update it
    if log_id is None:
        _event_logging_id = current_log_id
        
    # Print each event packet using the system config event type mapping
    for packet in packets:
        target = f"{packet['target_name']}"
        ptime = f"{packet[DERIVED_PACKET_TIMEFORMATTED_FIELD]}"
        app = f"{packet[EVENT_APP_FIELD]}"
        eid = f"{packet[EVENT_ID_FIELD]}"
        etype = f"{packet[EVENT_TYPE_FIELD]}"
        scid = f"{packet[EVENT_SCID_FIELD]}"
        procid = f"{packet[EVENT_PROCID_FIELD]}"
        emsg = f"{packet[EVENT_MESSAGE_FIELD]}"
        
        event = f"{target:<10} {ptime:<23} scid:{scid:<3} procid:{procid:<2} {EVENT_TYPE_TO_TXT[etype]:<5} {app:<13} {eid:>3}: {emsg}"
        print_func("Event: " + event)
        
    # Return the updated subscription ID if a specific one was provided
    if log_id is not None:
        return current_log_id
    
    
def is_background_packet_logging_running(name: Optional[str] = None) -> bool:
    """
    Check if a background packet logging session is running.
    
    Args:
        name (str, optional): Name of the specific logging session to check for.
            If None, checks if any logger is running.
    
    Returns:
        bool: True if a logging session is running, False otherwise.
    """
    loggers = stash_get('background_packet_loggers') or {}
    
    # Replace spaces with underscores in the name
    name = name.replace(' ', '_')
    
    if name:
        return name in loggers
    return bool(loggers)


def _is_packet_already_logged(target: str, packet: str) -> bool:
    """
    Check if a specific target-packet pair is already being logged.
    """
    loggers = stash_get('background_packet_loggers') or {}
    for logger_info in loggers.values():
        if any(item == [target, packet] for item in logger_info['data']):
            return True
    return False


def _normalize_input(input_data):
    """
    Normalize various input formats for packet logging into a standard format.

    Converts input into a list of [TARGET, PACKET] pairs. If PACKET is not specified,
    it defaults to EVENT_PACKET_NAME. Handles str and list inputs.
    """
    if isinstance(input_data, str):
        return [[input_data, EVENT_PACKET_NAME]]
    elif isinstance(input_data, list):
        normalized = []
        for item in input_data:
            if isinstance(item, str):
                normalized.append([item, EVENT_PACKET_NAME])
            elif isinstance(item, list):
                if len(item) == 1:
                    normalized.append([item[0], EVENT_PACKET_NAME])
                elif len(item) >= 2:
                    if len(item) > 2:
                        print(f" <!> Warning: More than 2 items in pair {item}. Ignoring excess items.")
                    normalized.append([item[0], item[1]])
        return normalized
    else:
        raise ValueError("Invalid input format")


def start_background_packet_logging(what_to_log, name: str = "default") -> None:
    """
    Start a background packet logging script.
    
    This function manages a background process that continuously logs specified packet messages.
    It allows logging of multiple packets from different targets.
    
    Note:
        To specify a single target-packet pair, use a nested list: [["TARGET", "PACKET"]]
        A single list [TARGET, PACKET] will be interpreted as two separate targets with default packets.
    
    Args:
        what_to_log: Required. Can be one of the following:
            - str: Single TARGET (logs default EVENT_PACKET_NAME)
            - list of str: Multiple TARGETs (each logs default EVENT_PACKET_NAME)
            - list of lists: Multiple [TARGET, PACKET] pairs
            - Mixed list of str and lists: Combination of TARGETs and [TARGET, PACKET] pairs
        name: Unique identifier for this logging session (default: "default")
    
    Raises:
        ValueError: If what_to_log is None or empty
    
    Examples:
        start_background_packet_logging("TARGET1")  # Logs default packet for TARGET1
        start_background_packet_logging(["TARGET1", "TARGET2"])  # Logs default packet for both targets
        start_background_packet_logging([["TARGET1", "PACKET1"]])  # Logs specific packet for TARGET1
        start_background_packet_logging([["TARGET1", "PACKET1"], ["TARGET2", "PACKET2"]])  # Logs specific packets
        start_background_packet_logging([["TARGET1", "PACKET1"], "TARGET2"])  # Mixed: specific for TARGET1, default for TARGET2
    """
    # Validate that what_to_log is provided
    if what_to_log is None:
        raise ValueError("what_to_log is required and cannot be None. Please specify at least one target.")
    
    if isinstance(what_to_log, list) and len(what_to_log) == 0:
        raise ValueError("what_to_log cannot be an empty list. Please specify at least one target.")
    
    normalized_data = _normalize_input(what_to_log)
    
    # Replace spaces with underscores in the name
    name = name.replace(' ', '_')
    
    # Check if logger with this name already exists
    if is_background_packet_logging_running(name):
        print(f"Background packet logging '{name}' is already running. Stopping and restarting...")
        stop_background_packet_logging(name)
    
    # Check if any packets are already being logged
    for target, packet in normalized_data:
        if _is_packet_already_logged(target, packet):
            print(f"Packet {target} {packet} is already being logged. Cannot start new logger.")
            return None

    print(f"Starting background packet logging '{name}' for: {normalized_data}")
    
    try:
        # Set up the synchronization flag - initialize to "starting"
        # Use unique keys per logger name to avoid race conditions
        stash_set(f'packet_logger_ready_{name}', 'starting')
        
        # Store the packet information in stash with unique keys per logger
        stash_set(f'packet_log_count_{name}', len(normalized_data))
        all_event_packets = all(packet == EVENT_PACKET_NAME for _, packet in normalized_data)
        stash_set(f'all_event_packets_{name}', all_event_packets)
        
        for i, (target, packet) in enumerate(normalized_data):
            stash_set(f'packet_log_target_{name}_{i}', target)
            stash_set(f'packet_log_packet_{name}_{i}', packet)
        
        # If all packets are EVENT_PACKET_NAME, store event field information
        if all_event_packets:
            from .system_config import (
                EVENT_TYPE_TO_TXT, EVENT_APP_FIELD, EVENT_ID_FIELD, EVENT_TYPE_FIELD,
                EVENT_MESSAGE_FIELD, EVENT_SCID_FIELD, EVENT_PROCID_FIELD, DERIVED_PACKET_TIMEFORMATTED_FIELD
            )
            stash_set(f'evt_app_field_{name}', EVENT_APP_FIELD)
            stash_set(f'evt_id_field_{name}', EVENT_ID_FIELD)
            stash_set(f'evt_type_field_{name}', EVENT_TYPE_FIELD)
            stash_set(f'evt_msg_field_{name}', EVENT_MESSAGE_FIELD)
            stash_set(f'evt_scid_field_{name}', EVENT_SCID_FIELD)
            stash_set(f'evt_procid_field_{name}', EVENT_PROCID_FIELD)
            stash_set(f'evt_time_field_{name}', DERIVED_PACKET_TIMEFORMATTED_FIELD)
            
            # Store the event type mapping
            stash_set(f'evt_type_count_{name}', len(EVENT_TYPE_TO_TXT))
            for i, (k, v) in enumerate(EVENT_TYPE_TO_TXT.items()):
                stash_set(f'evt_type_key_{name}_{i}', k)
                stash_set(f'evt_type_val_{name}_{i}', v)
        
        # Store the logger name in stash so the script can access it
        stash_set(f'logger_name_{name}', name)
        
        # Create a unique script name
        script_name = f"{name}_pkt_log_rpt.rb"
        
        # Create the Ruby script content with synchronization
        script_content = f'''
        # Packet logging script created by cosmos_test_utils
        set_line_delay(0.0)
        
        # Get the logger name to use for unique stash keys
        logger_name = stash_get('logger_name_{name}')
        
        # Get packet information from stash using unique keys
        packet_log_count = stash_get("packet_log_count_#{{logger_name}}").to_i
        all_event_packets = stash_get("all_event_packets_#{{logger_name}}")
        packets_to_subscribe = []
        (0...packet_log_count).each do |i|
            target = stash_get("packet_log_target_#{{logger_name}}_#{{i}}")
            packet = stash_get("packet_log_packet_#{{logger_name}}_#{{i}}")
            packets_to_subscribe << [target, packet]
        end
        
        # Subscribe to packets
        id = subscribe_packets(packets_to_subscribe)
        
        # Print header
        puts "Background Packet Logging Started"
        puts "================================="
        packets_to_subscribe.each do |target, packet|
            puts "Logging: #{{target}} #{{packet}}"
        end
        puts "================================="
        
        if all_event_packets
            # Get event field information using unique keys
            EVENT_APP_FIELD = stash_get("evt_app_field_#{{logger_name}}")
            EVENT_ID_FIELD = stash_get("evt_id_field_#{{logger_name}}")
            EVENT_TYPE_FIELD = stash_get("evt_type_field_#{{logger_name}}")
            EVENT_MESSAGE_FIELD = stash_get("evt_msg_field_#{{logger_name}}")
            EVENT_SCID_FIELD = stash_get("evt_scid_field_#{{logger_name}}")
            EVENT_PROCID_FIELD = stash_get("evt_procid_field_#{{logger_name}}")
            DERIVED_PACKET_TIMEFORMATTED_FIELD = stash_get("evt_time_field_#{{logger_name}}")
            
            # Get event type mapping
            EVENT_TYPE_TO_TXT = {{}}
            event_type_count = stash_get("evt_type_count_#{{logger_name}}").to_i
            (0...event_type_count).each do |i|
                k = stash_get("evt_type_key_#{{logger_name}}_#{{i}}")
                v = stash_get("evt_type_val_#{{logger_name}}_#{{i}}")
                EVENT_TYPE_TO_TXT[k] = v
            end
            
            # Print header line for event packets
            header = "       TARGET     PACKET_TIMEFORMATTED    SCID     PROCID    Type  App           EID: Event Message Text"
            puts header
        end
        
        # Signal that we're ready to capture packets
        stash_set("packet_logger_ready_#{{logger_name}}", 'ready')
        
        begin
            while true
                id, packets = get_packets(id, block: 1000)
                packets.each do |packet|
                    if all_event_packets
                        target = packet['target_name']
                        ptime = packet[DERIVED_PACKET_TIMEFORMATTED_FIELD].to_s
                        app = packet[EVENT_APP_FIELD].to_s
                        eid = packet[EVENT_ID_FIELD].to_s
                        etype = packet[EVENT_TYPE_FIELD].to_s
                        scid = packet[EVENT_SCID_FIELD].to_s
                        procid = packet[EVENT_PROCID_FIELD].to_s
                        emsg = packet[EVENT_MESSAGE_FIELD].to_s
                        
                        # Log event message received
                        event = sprintf("%-10s %-23s scid:%-3s procid:%-2s %-5s %-13s %3s: %s",
                                        target, ptime, scid, procid, EVENT_TYPE_TO_TXT[etype], app, eid, emsg)
                        puts "Event: " + event
                    else
                        target_name = packet['target_name']
                        packet_name = packet['packet_name']
                        time = packet['PACKET_TIMEFORMATTED']
                        
                        # Log basic packet information
                        puts "#{{time}}:"
                        puts "  #{{target_name}} #{{packet_name}}"
                        
                        # Log all telemetry items
                        packet.each do |key, value|
                            next if ['target_name', 'packet_name', 'PACKET_TIMEFORMATTED'].include?(key)
                            puts "  #{{key}}: #{{value}}"
                        end
                        puts "--------------------------------"
                    end
                end
            end
        end
        '''
        
        # Use script_create to create the script
        script_create(script_name, script_content)
        
        # Start the script
        script_id = script_run(script_name)
        
        # Store logger information
        logger_info = {
            'id': script_id,
            'data': normalized_data,
            'name': name
        }
        
        # Update stash
        loggers = stash_get('background_packet_loggers') or {}
        loggers[name] = logger_info
        stash_set('background_packet_loggers', loggers)
        
        # Wait for the script to signal it's ready using unique key
        print("Waiting for packet logger to initialize...")
        max_wait_time = LOGGER_INIT_WAIT_TIME
        wait_start = time.time()
        
        while time.time() - wait_start < max_wait_time:
            try:
                status = stash_get(f'packet_logger_ready_{name}')
                if status == 'ready':
                    break
            except:
                pass
            time.sleep(0.1)
        else:
            # We timed out waiting for the script to be ready
            print("Warning: Timeout waiting for packet logger to initialize fully")
        
        print(f"Background packet logging '{name}' started (script ID: {script_id})")
        
    except Exception as e:
        print(f"Error starting background packet logging: {str(e)}")
        raise


def stop_background_packet_logging(name: str = "default") -> None:
    """
    Stop a background packet logging script.
    
    Args:
        name: The unique identifier of the logging session to stop (default: "default")
    """
    try:
        loggers = stash_get('background_packet_loggers') or {}
        
        # Replace spaces with underscores in the name
        name = name.replace(' ', '_')
        
        if name in loggers:
            logger_info = loggers[name]
            script_id = logger_info['id']
            running_script_stop(script_id)
            
            # Remove from stash storage
            loggers.pop(name)
            stash_set('background_packet_loggers', loggers)
            
            print(f"Background packet logging '{name}' stopped (script ID: {script_id})")
        else:
            print(f"Background packet logging with name '{name}' not found (may not have been started or packet already being logged)")
    except Exception as e:
        print(f"Error stopping background packet logging: {str(e)}")


def stop_all_background_packet_logging() -> None:
    """
    Stop all running background packet logging scripts.
    
    This function iterates through all active packet loggers and stops them.
    It's useful for cleaning up all logging processes at once.
    """
    try:
        loggers = stash_get('background_packet_loggers') or {}
        if not loggers:
            print("No active background packet loggers found.")
            return

        for name, logger_info in list(loggers.items()):  # Use list() to avoid modifying dict during iteration
            script_id = logger_info['id']
            running_script_stop(script_id)
            
            print(f"Stopped background packet logging '{name}' (script ID: {script_id})")
            
            # Remove from loggers dictionary
            loggers.pop(name)
        
        # Update stash with empty loggers dictionary
        stash_set('background_packet_loggers', {})
        
        print("All background packet loggers have been stopped.")
    except Exception as e:
        print(f"Error stopping all background packet logging: {str(e)}")
