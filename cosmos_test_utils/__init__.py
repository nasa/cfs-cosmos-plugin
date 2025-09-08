"""
COSMOS Test Utilities Package

A collection of utility functions for testing with the OpenC3 COSMOS ground system.
"""

from .system_config import (
    EVENT_TARGET_NAME,
    EVENT_PACKET_NAME,
    EVENT_TYPE_TO_TXT,
    EVENT_TXT_TO_TYPE,
    EVENT_BLOCK_TIMEOUT,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_WAIT_TIMEOUT,
    COMMON_PACKET_TIME_SECONDS_FIELD,
    COMMON_PACKET_TIME_SUBSECS_FIELD,
    COMMON_PACKET_SEQUENCE_COUNT_FIELD,
    COMMON_PACKET_TIME_SECONDS_DESC,
    COMMON_PACKET_TIME_SUBSECS_DESC,
    COMMON_PACKET_SEQUENCE_DESC
)

from .event_utils import (
    open_event_log_for_search,
    open_event_log_for_script_logging,
    find_events,
    print_events_to_log,
    start_background_event_logging,
    stop_background_event_logging,
    is_background_event_logging_running
)

from .print_utils import (
    test_print,
    print_command_history
)

from .telemetry_utils import (
    report_telemetry,
    report_all_telemetry,
    report_all_targets_telemetry
)

from .requirement_utils import RequirementTracker

from .wait_utils import (
    wait_for_telemetry_value,
    wait_for_telemetry_expression,
    wait_for_telemetry_change,
    wait_for_sequence_count_change,
    wait_check_telemetry,
    wait_for_telemetry_in_range,
    wait_for_telemetry_in_timing_range,
    wait_multiple_telemetry
)

from .timing_utils import (
    TimingTracker,
    measure_command_response_time
)

from .command_utils import CommandSender

# Define the version
__version__ = '1.0.0'
