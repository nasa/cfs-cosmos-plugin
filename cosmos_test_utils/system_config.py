"""
System configuration settings for the COSMOS test utilities.

These settings can be customized by users to match their specific COSMOS environment.
Users should modify this file to match their mission-specific configuration.
"""

# Target and packet names for event messages
EVENT_TARGET_NAME = "CFE_EVS"
EVENT_PACKET_NAME = "EVS_LONG_EVENT"

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

