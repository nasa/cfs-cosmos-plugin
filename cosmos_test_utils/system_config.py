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

"""
System configuration settings for the COSMOS test utilities.

These settings can be customized by users to match their specific COSMOS environment.
Users should modify this file to match their mission-specific configuration.
"""

# Packet name for all event messages on the system
EVENT_PACKET_NAME = "CFE_EVS_LONG_EVENT_MSG"

# Event packet field names
EVENT_APP_FIELD     = "PACKET_ID_APP_NAME"      # Application name field
EVENT_ID_FIELD      = "PACKET_ID_EVENT_ID"      # Event ID field 
EVENT_TYPE_FIELD    = "PACKET_ID_EVENT_TYPE"    # Event type field
EVENT_MESSAGE_FIELD = "MESSAGE"                 # Event message text field
EVENT_SCID_FIELD    = "PACKET_ID_SPACECRAFT_ID" # Spacecraft ID field
EVENT_PROCID_FIELD  = "PACKET_ID_PROCESSOR_ID"  # Processor ID field

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
# If your project does not have some of these fields, set them to None
# and the reporting will handle their absence gracefully
COMMON_PACKET_STREAMID_FIELD       = "CCSDS_STREAMID"
COMMON_PACKET_SEQUENCE_COUNT_FIELD = "CCSDS_SEQUENCE" # Used directly in wait_utils.py as the default value for a parameter in wait_for_sequence_count_change()
COMMON_PACKET_LENGTH_FIELD         = "CCSDS_LENGTH"
COMMON_PACKET_TIME_SECONDS_FIELD   = "SECONDS"
COMMON_PACKET_TIME_SUBSECS_FIELD   = "SUBSECS"
COMMON_PACKET_SPARE_ALIGN_FIELD    = "SPARE_FOR_64_ALIGN"

# Derived fields that COSMOS appends to every telemetry packet 
# (Will not likely change, But if it does this package will likely need upated)
DERIVED_PACKET_TIMESECONDS_FIELD     = "PACKET_TIMESECONDS"
DERIVED_PACKET_TIMEFORMATTED_FIELD   = "PACKET_TIMEFORMATTED" #Used directly in telemetry_utils.py to warn if not being calculated from header time and event_utils.py for event logging purposes
DERIVED_RECEIVED_TIMESECONDS_FIELD   = "RECEIVED_TIMESECONDS"
DERIVED_RECEIVED_TIMEFORMATTED_FIELD = "RECEIVED_TIMEFORMATTED"  #Used directly in telemetry_utils.py to compare against DERIVED_PACKET_TIMEFORMATTED_FIELD
DERIVED_RECEIVED_COUNT_FIELD         = "RECEIVED_COUNT"
DERIVED_PACKET_TIME_FIELD            = "PACKET_TIME"


# NOTE: COMMON_PACKET_FIELDS and DERIVED_PACKET_FIELDS define both the fields
# to filter AND their display format. Each entry is a tuple of (field_name, format_type)
# 
# Valid format types:
#   'hex'    - Display as hexadecimal (e.g., 0x0800)
#   'dec'    - Display as decimal integer
#   'float'  - Display as floating point number
#   'time'   - Display as formatted time string
#   'string' - Display as string (default for unknown types)
#
# The order of fields in these lists determines the display order in reports.
# If your project doesn't have a field, you can remove it from the list.

COMMON_PACKET_FIELDS = [
    (COMMON_PACKET_STREAMID_FIELD,       'hex'),
    (COMMON_PACKET_SEQUENCE_COUNT_FIELD, 'dec'),
    (COMMON_PACKET_LENGTH_FIELD,         'dec'),
    (COMMON_PACKET_TIME_SECONDS_FIELD,   'dec'),
    (COMMON_PACKET_TIME_SUBSECS_FIELD,   'dec'),
    (COMMON_PACKET_SPARE_ALIGN_FIELD,    'dec'),
]

DERIVED_PACKET_FIELDS = [
    (DERIVED_PACKET_TIMESECONDS_FIELD,     'float'),
    (DERIVED_PACKET_TIMEFORMATTED_FIELD,   'time' ),
    (DERIVED_RECEIVED_TIMESECONDS_FIELD,   'float'),
    (DERIVED_RECEIVED_TIMEFORMATTED_FIELD, 'time' ),
    (DERIVED_RECEIVED_COUNT_FIELD,         'dec'  ),
    (DERIVED_PACKET_TIME_FIELD,            'time' ),
]

# Fields used for packet rate calculations in telemetry_utils.py
# Packet rate: calculated from packet header timestamps and sequence count
RATE_CALC_CCSDS_SECONDS_FIELD = COMMON_PACKET_TIME_SECONDS_FIELD
RATE_CALC_CCSDS_SUBSECS_FIELD = COMMON_PACKET_TIME_SUBSECS_FIELD
RATE_CALC_CCSDS_SEQUENCE_FIELD = COMMON_PACKET_SEQUENCE_COUNT_FIELD

# COSMOS rate: calculated from ground receipt timestamps and count
RATE_CALC_COSMOS_TIMESECONDS_FIELD = DERIVED_RECEIVED_TIMESECONDS_FIELD
RATE_CALC_COSMOS_COUNT_FIELD = DERIVED_RECEIVED_COUNT_FIELD

# Telemetry Report Display Configuration
# Separate column widths for different sections of the telemetry reports
# These are the Minimum width for Old and New value columns in their corresponding sections
# (will expand if needed for rare longer values)
HEADER_VALUE_COLUMN_WIDTH    = 25   # Width for header value columns - often contains longer formatted time strings
DERIVED_VALUE_COLUMN_WIDTH   = 25   # Width for derived value columns - often contains longer formatted time strings
TELEMETRY_VALUE_COLUMN_WIDTH = 16   # Width for telemetry value columns


# Configuration variables:
# Not project specific, but effect the default behavior of various functions

# Block time (in seconds) when waiting for events
EVENT_BLOCK_TIMEOUT = 4

# Default settings for telemetry polling and waiting
DEFAULT_POLL_INTERVAL = 0.1
DEFAULT_WAIT_TIMEOUT = 20.0

# Maximum time that the packet logger will wait for the background task to start.
# Increase if you see the procedure moving on before it should on slower systems.
LOGGER_INIT_WAIT_TIME = 30

# Length of random identifier appended to test names for unique background logging
# This prevents conflicts when the same test runs multiple times with different targets
# Recommended values: 3 (for ~10 instances), 4 (for ~100 instances), 6 (for ~1000+ instances)
# Each character uses lowercase letters and digits (36 possible values per character)
UNIQUE_LOG_IDENTIFIER_LENGTH = 3
