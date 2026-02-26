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

from typing import Optional, Tuple, Union
from .system_config import (
    get_event_target_name,
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
    EVENT_TIME_FIELD
)

# Module-level variables to store event subscription IDs
_event_search_id = None   # For find_events
_event_logging_id = None  # For print_events_to_log
_event_packets = []  # To store packets for multiple find_events calls


def set_event_search_point(
    target_name: str = None, 
    packet_name: str = EVENT_PACKET_NAME
) -> str:
    """Set the point that a find_events call will search back to.
    
    This function subscribes to event packets and stores the subscription ID
    at the module level, so it can be used by find_events without requiring
    the ID to be passed in each time.
    
    Note: This function should be called multiple times. Each time it's called,
    it resets the point at which future find_events calls will begin searching.
    This is useful to narrow searches to specific sections of a test.
    
    Args:
        target_name: COSMOS target name for events (default: from system_config)
        packet_name: COSMOS packet name for events (default: from system_config)
    
    Returns:
        The subscription ID (also stored internally for use by find_events)
    """
    global _event_search_id, _event_packets
    
    # Import and use the COSMOS subscribe_packets function
    from openc3.script import subscribe_packets
    
    if target_name is None:
        target_name = get_event_target_name()
    
    # Reset the stored packets when setting a new search point
    _event_packets = []
    
    # Subscribe to event packets
    _event_search_id = subscribe_packets([[target_name, packet_name]])
    
    return _event_search_id


def open_event_log_for_script_logging(
    target_name: str = None, 
    packet_name: str = EVENT_PACKET_NAME
) -> str:
    """Subscribe to event packets for script logging.
    
    This function subscribes to event packets and stores the subscription ID
    at the module level, so it can be used by print_events_to_log without 
    requiring the ID to be passed in each time.
    
    Note: This function should only be called once at the beginning of a test,
    unlike set_event_search_point which may be called multiple times.
    
    Args:
        target_name: COSMOS target name for events (default: from system_config)
        packet_name: COSMOS packet name for events (default: from system_config)
    
    Returns:
        The subscription ID (also stored internally for use by print_events_to_log)
    """
    global _event_logging_id
    
    # Import and use the COSMOS subscribe_packets function
    from openc3.script import subscribe_packets
    
    if target_name is None:
        target_name = get_event_target_name()
    
    # Subscribe to event packets
    _event_logging_id = subscribe_packets([[target_name, packet_name]])
    
    return _event_logging_id


def find_events(
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
        if (packet[EVENT_APP_FIELD] == app_name and
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


def print_events_to_log(
    log_id: Optional[int] = None,
    use_group_print: bool = False
) -> Optional[int]:
    """Print all received event messages to the test log since the last call.
    
    Before using this function with the default log_id=None,
    you must call open_event_log_for_script_logging() to set up the event subscription.
    
    Args:
        log_id: Optional specific subscription ID to use
               (default: None, which uses the module-level ID)
        use_group_print: If True, use Group.print; if False, use built-in print
        
    Returns:
        Optional[int]: Updated subscription ID if a specific log_id was provided
        
    Raises:
        RuntimeError: If log_id=None and open_event_log_for_script_logging() has not been called
    """
    global _event_logging_id
    
    # Determine which subscription ID to use
    if log_id is None:
        # Use the module-level ID
        if _event_logging_id is None:
            raise RuntimeError(
                "Event logging subscription not initialized in cosmos_test_utils.event_utils. "
                "You must call open_event_log_for_script_logging() before using print_events_to_log() "
                "or other functions that depend on event logging (like test_print). "
                "Add this to your script:\n\n"
                "    from cosmos_test_utils import open_event_log_for_script_logging\n"
                "    open_event_log_for_script_logging()  # Call this once at the start of your test\n\n"
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
        ptime = f"{packet[EVENT_TIME_FIELD]}"
        app = f"{packet[EVENT_APP_FIELD]}"
        eid = f"{packet[EVENT_ID_FIELD]}"
        etype = f"{packet[EVENT_TYPE_FIELD]}"
        scid = f"{packet[EVENT_SCID_FIELD]}"
        procid = f"{packet[EVENT_PROCID_FIELD]}"
        emsg = f"{packet[EVENT_MESSAGE_FIELD]}"
        
        event = f"{ptime:<23} scid:{scid:<3} procid:{procid:<2} {EVENT_TYPE_TO_TXT[etype]:<5} {app:<13} {eid:>3}: {emsg}"
        print_func("Event: " + event)
        
    # Return the updated subscription ID if a specific one was provided
    if log_id is not None:
        return current_log_id
    
    
def start_background_event_logging(name: str = "default", filename: Optional[str] = None):
    """Start or restart a background event logging script.
    
    This function manages a background process that continuously logs event messages.
    It's designed to support multi-level logging (suite, group, and test level) without conflicts.

    Behavior:
    1. If no logging is active, starts a new logging session.
    2. If logging with the same name is active, stops and restarts it (useful for error recovery).
    3. If logging with a different name is active, does not start a new session (preserves suite-level logging).

    The background script runs parallel to the main test without interference.
    
    Args:
        name: Unique identifier for this logging session (default: "default")
        filename: Optional path for log file. If None, logs to COSMOS log only.
        
    Example:
        start_background_event_logging("my_test_logging")
        # ... run tests ...
        stop_background_event_logging("my_test_logging")
    """
    from openc3.script import script_create, script_run, stash_set, stash_get
    import time
    
    # Check if there's already a background logger running
    if is_background_event_logging_running(name):
        print(f"Background event logging '{name}' is already running. Stopping and restarting...")
        stop_background_event_logging(name)
    elif is_background_event_logging_running():
        existing_name = stash_get('background_event_log_name')
        print(f"Background event logging '{existing_name}' is already running.")
        return
    
    # Store the filename for the script to use (if provided)
    if filename:
        stash_set('eventlog', filename)
        print(f"Starting background event logging '{name}' to file: {filename} and COSMOS log file")
    else:
        # Clear any existing filename
        try:
            stash_set('eventlog', None)
        except:
            pass
        print(f"Starting background event logging '{name}' to COSMOS log file")

    try:
        # Set up the synchronization flag - initialize to "starting"
        stash_set('event_logger_ready', 'starting')

        # Store system_config values in stash for the script to access
        from .system_config import (
            get_event_target_name, EVENT_PACKET_NAME, EVENT_TYPE_TO_TXT,
            EVENT_APP_FIELD, EVENT_ID_FIELD, EVENT_TYPE_FIELD,
            EVENT_MESSAGE_FIELD, EVENT_SCID_FIELD, EVENT_PROCID_FIELD, EVENT_TIME_FIELD
        )

        # Store basic configuration
        stash_set('evt_target_name', get_event_target_name())
        stash_set('evt_packet_name', EVENT_PACKET_NAME)
        stash_set('evt_app_field', EVENT_APP_FIELD)
        stash_set('evt_id_field', EVENT_ID_FIELD)
        stash_set('evt_type_field', EVENT_TYPE_FIELD)
        stash_set('evt_msg_field', EVENT_MESSAGE_FIELD)
        stash_set('evt_scid_field', EVENT_SCID_FIELD)
        stash_set('evt_procid_field', EVENT_PROCID_FIELD)
        stash_set('evt_time_field', EVENT_TIME_FIELD)

        # Store the event type mapping
        stash_set('evt_type_count', len(EVENT_TYPE_TO_TXT))
        i = 0
        for k, v in EVENT_TYPE_TO_TXT.items():
            stash_set(f'evt_type_key_{i}', k)
            stash_set(f'evt_type_val_{i}', v)
            i += 1

        # Create the script content with synchronization
        script_content = '''
        # Event logging script created by cosmos_test_utils
        # Get configuration from stash
        set_line_delay(0.0)
        EVENT_TARGET_NAME = stash_get('evt_target_name')
        EVENT_PACKET_NAME = stash_get('evt_packet_name')
        EVENT_APP_FIELD = stash_get('evt_app_field')
        EVENT_ID_FIELD = stash_get('evt_id_field')
        EVENT_TYPE_FIELD = stash_get('evt_type_field')
        EVENT_MESSAGE_FIELD = stash_get('evt_msg_field')
        EVENT_SCID_FIELD = stash_get('evt_scid_field')
        EVENT_PROCID_FIELD = stash_get('evt_procid_field')
        EVENT_TIME_FIELD = stash_get('evt_time_field')

        # Get event type mapping
        EVENT_TYPE_TO_TXT = {}
        event_type_count = stash_get('evt_type_count').to_i
        (0...event_type_count).each do |i|
            k = stash_get("evt_type_key_#{i}")
            v = stash_get("evt_type_val_#{i}")
            EVENT_TYPE_TO_TXT[k] = v
        end

        # Check if a specific log file was requested
        log_filename = nil
        begin
            log_filename = stash_get('eventlog')
        rescue
            # No file specified, just print to COSMOS log
        end

        # Open log file if specified
        log_file = nil
        if log_filename
            log_file = File.open(log_filename, 'w')
            puts "Logging events to file: #{log_filename}"
        end

        # Subscribe to event packets
        id = subscribe_packets([[EVENT_TARGET_NAME, EVENT_PACKET_NAME]])

        # Print header line to describe each column
        header = "       PACKET_TIMEFORMATTED    SCID     PROCID    Type  App           EID: Event Message Text"
        puts header
        if log_file
            log_file.puts header
            log_file.flush
        end

        # Signal that we're ready to capture events
        stash_set('event_logger_ready', 'ready')

        begin
            while true
                id, packets = get_packets(id, :block => 1000, :count => 1)
                packets.each do |packet|
                    ptime = packet[EVENT_TIME_FIELD].to_s
                    app = packet[EVENT_APP_FIELD].to_s
                    eid = packet[EVENT_ID_FIELD].to_s
                    etype = packet[EVENT_TYPE_FIELD].to_s
                    scid = packet[EVENT_SCID_FIELD].to_s
                    procid = packet[EVENT_PROCID_FIELD].to_s
                    emsg = packet[EVENT_MESSAGE_FIELD].to_s

                    # Log event message received
                    event = sprintf("%-23s scid:%-3s procid:%-2s %-5s %-13s %3s: %s",
                                   ptime, scid, procid, EVENT_TYPE_TO_TXT[etype], app, eid, emsg)
                    event_line = "Event: " + event

                    puts event_line
                    if log_file
                        log_file.puts event_line
                        log_file.flush
                    end
                end
            end
        ensure
            if log_file
                log_file.close
            end
        end
        '''

        # Use script_create to create the script
        script_name = "event_logger_report.rb"
        script_create(script_name, script_content)

        # Start the script
        script_id = script_run(script_name)

        # Store the script ID and name for use in other functions
        stash_set('background_event_log_id', script_id)
        stash_set('background_event_log_name', name)

        # Wait for the script to signal that it's ready to capture events
        print("Waiting for event logger to initialize...")
        max_wait_time = 10.0  # Maximum time to wait for script to be ready
        wait_start = time.time()
        
        while time.time() - wait_start < max_wait_time:
            try:
                status = stash_get('event_logger_ready')
                if status == 'ready':
                    break
            except:
                pass

            time.sleep(0.1)
        else:
            # We timed out waiting for the script to be ready
            print("Warning: Timeout waiting for event logger to initialize fully")

        print(f"Background event logging '{name}' started (script ID: {script_id})")
        
    except Exception as e:
        print(f"Error starting background event logging: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def stop_background_event_logging(name: str = "default"):
    """Stop background event logging script.
    
    This stops the background event logging script with the specified name.
    If no script with the given name is running, this function does nothing.
    
    Args:
        name: The unique identifier of the logging session to stop (default: "default")
        
    Example:
        start_background_event_logging("my_test_logging")
        # ... run tests ...
        stop_background_event_logging("my_test_logging")
    """
    from openc3.script import running_script_stop, stash_get, stash_set
    
    try:
        if is_background_event_logging_running(name):
            script_id = stash_get('background_event_log_id')
            print(f"Stopping background event logging '{name}' (script ID: {script_id})")
            running_script_stop(script_id)
            
            # Clear the stored script ID and name
            stash_set('background_event_log_id', None)
            stash_set('background_event_log_name', None)
            
            # Clear the log filename
            try:
                stash_set('eventlog', None)
            except:
                pass
                
            print(f"Background event logging '{name}' stopped")
        else:
            current_name = stash_get('background_event_log_name')
            if current_name:
                print(f"Background event logging '{current_name}' is running, but not stopping it as it doesn't match the requested name '{name}'")
            else:
                print("No background event logging script is currently running")
    except Exception as e:
        print(f"Error stopping background event logging: {str(e)}")


def is_background_event_logging_running(name: str = "default") -> bool:
    """Check if background event logging is currently running.
    
    Args:
        name: Name to check for a specific logging session (default: "default")
    
    Returns:
        bool: True if background event logging is running (and matches the name if provided), False otherwise
        
    Example:
        if is_background_event_logging_running():
            print("Default logging session is active")
        
        if is_background_event_logging_running("my_test_logging"):
            print("Specific logging session is active")
    """
    from openc3.script import stash_get
    
    try:
        script_id = stash_get('background_event_log_id')
        current_name = stash_get('background_event_log_name')
        return script_id is not None and current_name == name
    except:
        return False


def open_event_log_for_search(
    target_name: str = None, 
    packet_name: str = EVENT_PACKET_NAME
) -> int:
    """Set the point that a find_events call will search back to.
    
    This is deprecated and included for backward compatibility.
    Use set_event_search_point() for more understandable code.
    """
    if target_name is None:
        target_name = get_event_target_name()
    
    return set_event_search_point(target_name, packet_name)
