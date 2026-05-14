"""
COSMOS Test Utilities Package

A collection of utility functions for testing with the OpenC3 COSMOS ground system.
"""

from .cosmos_test_utils.system_config import (
    EVENT_PACKET_NAME,
    COMMON_PACKET_FIELDS,
    DERIVED_PACKET_FIELDS,
    EVENT_BLOCK_TIMEOUT,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_WAIT_TIMEOUT,
    LOGGER_INIT_WAIT_TIME
)

from .cosmos_test_utils.event_utils import (
    set_event_search_point,
    capture_events_for_script_logging,
    find_events,
    print_events_to_log,
    is_background_packet_logging_running,
    start_background_packet_logging,
    stop_background_packet_logging,
    stop_all_background_packet_logging
)

from .cosmos_test_utils.print_utils import (
    test_print,
    print_command_history
)

from .cosmos_test_utils.telemetry_utils import (
    get_tlm_point,
    get_telemetry_values,
    validate_telemetry,
    report_telemetry,
    report_all_telemetry,
    report_all_targets_telemetry
)

from .cosmos_test_utils.test_tracking_utils import (
    test_initialization,
    test_step_start,
    test_step_end,
    test_end
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
__version__ = '2.0.0'
