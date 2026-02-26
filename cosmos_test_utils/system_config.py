# NASA Docket No. GSC-19606-1, and identified as Test Utilities Python
# package to facilitate testing software with the open source COSMOS
# ground system”
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

"""
System configuration settings for the COSMOS test utilities.

These settings can be customized by users to match their specific COSMOS environment.
Users should modify this file to match their mission-specific configuration.
"""

# Target and packet names for event messages
# Due to the way COSMOS builds the gems, the Target name cannot be a ruby embedded variable
EVENT_TARGET_NAME = "TARGET_NAME_NEEDS_SET"
EVENT_PACKET_NAME = "EVS_LONG_EVENT"

def set_event_target_name(target_name: str):
    """
    Set the EVENT_TARGET_NAME for use in event utilities.
    Use this function to change the target name on a multi-target system
    
    Args:
        target_name: The name of the target to set
    """
    global EVENT_TARGET_NAME
    EVENT_TARGET_NAME = target_name

def get_event_target_name():
    """
    Get the EVENT_TARGET_NAME that is currently set for use in event utilities.
    Use this function to find what the currently set target name is
    """
    global EVENT_TARGET_NAME
    return EVENT_TARGET_NAME

# Event packet field names
EVENT_APP_FIELD = "APP"           # Application name field
EVENT_ID_FIELD = "EID"            # Event ID field 
EVENT_TYPE_FIELD = "EVENTTYPE"    # Event type field
EVENT_MESSAGE_FIELD = "EVMSG"     # Event message text field
EVENT_SCID_FIELD = "SCID"         # Spacecraft ID field
EVENT_PROCID_FIELD = "PROCID"     # Processor ID field
# Next is the COSMOS Formatted time field. 
# This is a standard derived value, but if your project uses a different derived mnemonic for the timestamp (seconds and subseconds), place it here
EVENT_TIME_FIELD = "PACKET_TIMEFORMATTED"  

# Event type mappings structures, both directions
EVENT_TYPE_TO_TXT = {
    '1': 'DEBUG',
    '2': 'INFO', 
    '3': 'ERROR',
    '4': 'CRIT'
}

EVENT_TXT_TO_TYPE = {
    'DEBUG': 1,
    'INFO': 2,
    'ERROR': 3,
    'CRIT': 4
}

# Common telemetry packet field names 
# Usually found in a template (starts with '_') in the PLUGIN/targets/TARGET/cmd_tlm directory
COMMON_PACKET_TIME_SECONDS_FIELD = "CCSDS_SECONDS"    # Packet time seconds field name
COMMON_PACKET_TIME_SUBSECS_FIELD = "CCSDS_SUBSECS"    # Packet time subseconds field name
COMMON_PACKET_SEQUENCE_COUNT_FIELD = "CCSDS_SEQUENCE"  # Packet sequence counter field name

# Common telemetry packet field descriptions:
# Descriptions for the above fields when they are printed in reports
COMMON_PACKET_TIME_SECONDS_DESC = "CCSDS Packet Time Seconds"
COMMON_PACKET_TIME_SUBSECS_DESC = "CCSDS Packet Time SubSeconds"
COMMON_PACKET_SEQUENCE_DESC = "CCSDS Packet Sequence Count"

# Configuration variables:
# (Not project specific, but effect the default behavior of various functions)

# Block time (in milliseconds) when waiting for events
EVENT_BLOCK_TIMEOUT = 4000

# Default settings for telemetry waiting
DEFAULT_POLL_INTERVAL = 0.1
DEFAULT_WAIT_TIMEOUT = 30.0

