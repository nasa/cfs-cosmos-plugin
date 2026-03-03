"""
COSMOS Test Utilities Package

A collection of utility functions for testing with the OpenC3 COSMOS ground system.
"""

from .cosmos_test_utils.system_config import (
    EVENT_TARGET_NAME,
    set_event_target_name,
    get_event_target_name,
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

from .cosmos_test_utils.event_utils import (
    set_event_search_point,
    open_event_log_for_script_logging,
    find_events,
    print_events_to_log,
    start_background_event_logging,
    stop_background_event_logging,
    is_background_event_logging_running,
    open_event_log_for_search
)

from .cosmos_test_utils.print_utils import (
    test_print,
    print_command_history
)

from .cosmos_test_utils.telemetry_utils import (
    get_tlm_point,
    report_telemetry,
    report_all_telemetry,
    report_all_targets_telemetry
)

from .cosmos_test_utils.requirement_utils import RequirementTracker

from .cosmos_test_utils.wait_utils import (
    wait_for_telemetry_value,
    wait_for_telemetry_expression,
    wait_for_telemetry_change,
    wait_for_sequence_count_change,
    wait_check_telemetry,
    wait_for_telemetry_in_range,
    wait_for_telemetry_in_timing_range,
    wait_multiple_telemetry
)

from .cosmos_test_utils.timing_utils import (
    TimingTracker,
    measure_command_response_time
)

from .cosmos_test_utils.command_utils import CommandSender

# Define the version
__version__ = '1.0.2'
