# COSMOS Test Utilities

This is a collection of Common FSW Test Utilities for testing with the OpenC3 \
COSMOS ground system.

## Overview

The COSMOS Test Utilities package provides a comprehensive set of tools for \
creating, running, and managing tests in the OpenC3 COSMOS ground system \
environment. These utilities help standardize test procedures and reduce \
unnecessary code in test scripts.

## Prerequisites

- Python 3.6 or higher
- Access to a COSMOS ground system environment
- OpenC3 COSMOS 5.0 or higher


## Quick Start

1. **Put this package into the directory structure you desire**
   
   The placement of this package should be in your PLUGIN/lib directory. \
   This will allow the package to be accessible to scripts when the gem is \
   built.

   Older versions of COSMOS (before 6.9.0) will need to create a Wheel file of\
   this package and load that in COSMOS seperately. There was a bug in COSMOS \
   that prevented the script runner from seeing Python packages in the lib dir.

2. **Configure for your mission:**

   Edit cosmos_test_utils\cosmos_test_utils\system_config.py to match your \
   COSMOS setup. This file contains all of the variable names and structures \
   that require project specific mnemonics to be set in order to work properly\
   with your system.

   Things like:
   ```python
   # Packet name for all event messages on the system
   EVENT_PACKET_NAME = "CFE_EVS_LONG_EVENT_MSG"
   
   # Event packet field names
   EVENT_APP_FIELD     = "PACKET_ID_APP_NAME"      # Application name field
   EVENT_ID_FIELD      = "PACKET_ID_EVENT_ID"      # Event ID field 
   EVENT_TYPE_FIELD    = "PACKET_ID_EVENT_TYPE"    # Event type field
   EVENT_MESSAGE_FIELD = "MESSAGE"                 # Event message text field
   EVENT_SCID_FIELD    = "PACKET_ID_SPACECRAFT_ID" # Spacecraft ID field
   EVENT_PROCID_FIELD  = "PACKET_ID_PROCESSOR_ID"  # Processor ID field
   ```

3. <strong id="create-wheel-file">If you are on COSMOS 6.9.0 or later, you are done.</strong>

<br>

<details>
<summary><strong>If you are on an earlier version of COSMOS, follow these instructions:</strong></summary>

4. **(CONDITIONAL) Create the wheel file for loading into COSMOS**

   > **NOTE:** This step is only needed if running an older version of COSMOS.\
   > Skip this step if you are running on the latest version of COSMOS.\
   > If the Script runner does not recognize the modules, then you will\
   > have to build and load the Wheel.

   ```bash
   python -m build --wheel
   ```

5. **Load the package into COSMOS:**
   1. With COSMOS running, browse to "ADMIN CONSOLE"
   2. On the top of that page, select "Packages"
   3. Click where it says "Click to select file(s) to add to COSMOS"
   4. Browse to where the wheel file was created, select it, and press "open" \
   (nominally: PLUGIN\lib\cosmos_test_utils\dist)
   5. Press the button on the right labeled "Upload"

   After COSMOS finishes processing the Wheel file, you should see the\
   package appear in the list under "Python Packages" at the _**bottom**_ of the page.

</details>

<br>

## Suggested Use
   
   The easiest way to integrate this into your test scripts is to include the \
   following line it your tests:
   ```python
   import cosmos_test_utils as ctu
   ```
   This will give you access to all functions and Classes available in the \
   package in your scripts and avoid name collisions. The examples further in \
   this file import specific functions to show how selective import could work \
   if desired. 

   You should be able to get your particular IDE to recognize the functions of\
   this package and even enable autocompletion. You will need to refer to help\
   specific to that IDE in order to do that. 

   This README only encompasses things related to this package.


## System Configuration

The package includes a `system_config.py` file that contains mission-specific \
configuration parameters. Users need to customize this file to match their \
specific COSMOS environment. If you do not have common header field names and \
you want to use this you will have to rework your headers to have the same \
names across all packets. This package was designed with CCSDS headers in \
mind, but I tried to make things generic enough that if other headers are used\
this could be used as well. Feedback is appreciated.

Key configurations include:
- Event message packet name
- Event packet field names
- Event type mappings
- Common telemetry field names
- Default timeouts and polling intervals

See the cosmos_test_utils/cosmos_test_utils/system_config.py for all configurable \
variables.

## Key Features

### Test Tracking Utilities

The test tracking utilities provide a hierarchical framework for organizing\
and tracking tests, sub-tests, and test steps with automatic status \
determination and reporting.

Key features include:
- Hierarchical test structure (tests can contain sub-tests and steps)
- Automatic test and step numbering
- Pass/Fail status tracking with automatic propagation to parent tests
- Auto-determined test names from function/class names with override capability
- Flexible test type labeling (Test, Group, and Custom)
- Per-test RequirementTracker instances with parent-child status propagation
- Integration with event logging, telemetry reporting, and background packet logging
- Automatic initialization and cleanup of test resources
- Incomplete test/step detection with warnings
- Optional step-level status tracking
- Comprehensive test reports with requirement tracking
- Overall test status determined by all children (fails if any child fails or is untested)

Basic usage examples:
```python
from cosmos_test_utils import test_initialization, test_step_start, test_step_end, test_end

# Initialize a test (auto-determines name from function/class)
test_initialization(
    ["TARGET"],
    packets_to_report=[["TARGET", "POWER_TLM"], ["TARGET", "HK_TLM"]]
)

# Or override the auto-determined name and type
test_initialization(
    ["TARGET"],
    override_test_name="Full Mission Suite",
    override_type="Suite"
)

# Start a test step (returns step number)
step_num = test_step_start("Initialize Power Subsystem")

# Perform test operations...
# ... commands, telemetry checks, etc. ...

# End the step with status
result = test_step_end("Pass", "Power subsystem initialized successfully")

# Start another step with optional status tracking
step_num = test_step_start("Validate Battery Levels", track_step_status=True)
# ... test operations ...
result = test_step_end("Fail", "Battery level below threshold")

# End the test (automatically determines overall status)
final_status = test_end()  # Returns "P" or "F"
```

The test tracking system automatically:
- Creates a RequirementTracker for each test level
- Starts background Event logging and Event capturing to test log
- Reports initial telemetry for specified packets, if any packets provided
- Propagates status changes up the test hierarchy
- Detects incomplete tests/steps and reports warnings
- Generates comprehensive reports with requirement tracking
- Cleans up resources (stops background logging)

Hierarchical test example:
```python
# Top-level suite
test_initialization(["SC"], override_test_name="Mission Suite", override_type="Suite")

# Sub-test 1
test_initialization(["SC"], override_test_name="Power Tests", override_type="Group")
step_num = test_step_start("Check Battery")
test_step_end("Pass")
test_end()  # Power Tests complete, test status determined from all steps

# Sub-test 2
test_initialization(["SC"], override_test_name="Comm Tests", override_type="Group")
step_num = test_step_start("Check Radio")
test_step_end("Pass")
test_end()  # Comm Tests complete, test status determined from all steps

test_end()  # Mission Suite complete, status based on all sub-tests
```

<br>

### Command Utilities

The CommandSender class provides robust functionality for sending commands, \
verifying responses, and tracking command history in COSMOS tests.

Key features include:
- Sending basic commands and commands with parameters
- Executing commands multiple times with configurable delay between each
- Verifying command responses with flexible comparison operators (==, !=, <, <=, >, >=, contains, does_not_contain)
- Tracking and reporting on requirements associated with commands
- Timing requirement verification with configurable time windows (min_time/max_time)
- Automatic requirement status updates (Pass/Fail) based on command responses
- Detailed command history tracking with configurable detail levels (0=basic, 1=standard, 2=verbose)
- Integration with RequirementTracker for automated requirement tracking
- Multiple command execution with incremental telemetry value verification
- Custom print function support for enhanced logging
- Optional early termination on first failure for command sequences

Basic usage examples:
```python
from cosmos_test_utils import CommandSender, RequirementTracker

# Initialize a command sender with optional requirement tracker
tracker = RequirementTracker()
sender = CommandSender(req_tracker=tracker)

# Send a basic command
sender.send_command("TARGET NOOP")

# Send a command and verify the response
success = sender.send_cmd_with_response_check(
    "TARGET SET_MODE with MODE 'SCIENCE'",
    target="TARGET", packet="HK_TLM", 
    item="MODE", comparison="==", comparison_value="SCIENCE"
)

# Send command with requirement verification
success = sender.send_cmd_with_requirement(
    "TARGET SET_MODE with MODE 'SCIENCE'",
    "TARGET", "HK_TLM", "MODE", "==", "SCIENCE",
    requirement_ids="REQ-123"
)

# Send command with timing requirement
success = sender.send_cmd_with_timing_requirement(
    "TARGET QUICK_RESPONSE",
    "TARGET", "STATUS_TLM", "READY", "==", True,
    "REQ-TIMING-001",
    min_time=0.5,
    max_time=2.0
)

# Print command history with different detail levels
sender.print_command_history(detail_level=1)  # Standard detail
```

<br>

### Event Utilities

The event utilities provide comprehensive functionality for capturing, \
analyzing, and logging event messages or packets from the system under test.

Key features include:
- Module-level subscription management (no need to pass subscription IDs)
- Event search with flexible filtering (application, event ID, type, message text)
- Support for single or multiple targets in event subscriptions
- Script log integration with automatic event printing
- Background packet logging for any packets (not limited to events)
- Named logging sessions for independent management of multiple loggers
- Check for active logging sessions to prevent conflicts
- Batch operations to stop all background loggers at once
- Optional COSMOS Group.print integration for test suite compatibility
- Synchronization flags for reliable logger initialization

Basic usage examples:
```python
from cosmos_test_utils import (
    set_event_search_point, find_events,
    capture_events_for_script_logging, print_events_to_log,
    start_background_packet_logging, stop_background_packet_logging
)
from openc3.script import cmd

# Event searching - set up once, use multiple times
set_event_search_point("TARGET")
cmd("TARGET COMMAND")
success, count = find_events(
    "TARGET", "TARGET_APP", 5, "INFO", "Command executed"
)

# Script log integration - set up once at test start
capture_events_for_script_logging(["TARGET1", "TARGET2"])
cmd("TARGET1 COMMAND")
print_events_to_log()  # Print all events since last call

# Background logging to separate file/console
start_background_packet_logging("TARGET")  # Logs event packets
start_background_packet_logging([["TARGET", "HK_TLM"]])  # Logs any packet
# ... perform test operations ...
stop_background_packet_logging()  # Stop the logger
```

<br>

### Requirement Tracking

The RequirementTracker class provides functionality for tracking and reporting\
on verification items during testing, which is predominately tied to requirements.

Key features include:
- Six states: U (Untested), P (Passed), F (Failed), I (Needs Inspection), A (Needs Analysis), IA (Needs Inspection & Analysis)
- Enforced state transition rules (e.g., F is terminal, cannot transition from I/A/IA to P)
- Setting single or multiple requirements with the same state and message
- Event history tracking for all state changes with timestamps (to support Debug mode)
- Querying requirements individually, all at once, or filtered by state
- Debug mode for detailed event history in reports
- Generate reports as formatted strings or print directly to test logs
- Integration with CommandSender for automated requirement verification
- Flexible tracking - can track any string identifier (requirements, telemetry points, test steps)
- Custom print function support for integration with test frameworks
- Reset functionality to clear all tracked requirements

Basic usage examples:
```python
from cosmos_test_utils import RequirementTracker

# Initialize a tracker
req_tracker = RequirementTracker()

# Initialize requirement status (optional but recommended)
req_tracker.set_multiple_requirements("REQ-123, REQ-456", "U", "Initialize Requirements expected to be tested.")

# Set requirement statuses
req_tracker.set_requirement("REQ-123", "P", "Verified by command test")
req_tracker.set_requirement("REQ-456", "F", "Failed timeout condition")

# Set multiple requirements at once
req_tracker.set_multiple_requirements("REQ-789, REQ-790", "P", "Both verified by telemetry check")

# Get specific requirement info
req_info = req_tracker.get_requirement("REQ-123")

# Get all requirements with a specific state
failed_reqs = req_tracker.get_requirements_by_state("F")

# Enable debug mode for detailed history
req_tracker.set_debug_mode(True)

# Generate and print report
print(req_tracker.generate_requirements_report())

# Or print directly to test log
req_tracker.requirements_report()  # Uses test_print by default
```

The RequirementTracker can also be used to track anything, like telemetry\
points or tests executed. The requirement ID is just a string that you can set\
to anything:

```python
req_tracker.set_requirement("HK_CmdCnt", "P", "Verified that this increments as expected")
req_tracker.set_requirement("Noop EM", "P", "Event Message received as expected")
req_tracker.set_requirement("Test_Step_5", "F", "Did not complete within expected time")
```

Use of this will only be limited by your creativity.

<br>

### Telemetry Utilities

The telemetry utilities provide comprehensive functions for retrieving,\
validating, monitoring, and reporting telemetry changes in COSMOS tests.

Key features include:
- Single telemetry point retrieval (RAW, CONVERTED, or FORMATTED)
- Multiple telemetry value retrieval with optional filtering of header/derived fields
- Telemetry validation against single or multiple expected conditions
- Detailed packet reports with header fields, derived fields, and telemetry values
- Automatic change tracking between successive reports
- Configurable formatting with field-specific format types (hex, dec, float, time, string)
- Packet rate calculations (both CCSDS and COSMOS-derived)
- Change indicators highlighting modified values
- Three detail levels (0=changes only, 1=all values, initial=first report)
- Target-wide telemetry reporting across all packets
- System-wide telemetry reporting across all targets
- Flexible filtering to exclude specific packets or targets
- Configurable column widths via system_config

Basic usage examples:
```python
from cosmos_test_utils import (
    get_tlm_point, get_telemetry_values, validate_telemetry,
    report_telemetry, report_all_telemetry, report_all_targets_telemetry
)

# Get a single telemetry point
value = get_tlm_point("TARGET", "HK_PACKET", "MODE")
raw_value = get_tlm_point("TARGET", "HK_PACKET", "MODE", type='RAW')

# Get multiple telemetry values (filtered by default)
all_values = get_telemetry_values("TARGET", "HK_PACKET")
first_five = get_telemetry_values("TARGET", "HK_PACKET", num_items=5)

# Validate telemetry conditions
success = validate_telemetry(['TARGET', 'HK_PACKET', 'MODE', 'SCIENCE'])
success = validate_telemetry([
    ['TARGET', 'HK_PACKET', 'MODE', 'SCIENCE'],
    ['TARGET', 'HK_PACKET', 'BATTERY', '>=', 75]
])

# Report initial packet with all points
report_telemetry("TARGET", "HK_PACKET", level_of_detail=1)

# ... perform operations ...
# Report changes in that specific packet (level 0 = changes only)
report_telemetry("TARGET", "HK_PACKET")

# Report all telemetry for a target, excluding specific packets
report_all_telemetry("TARGET", exclude_packets=["DEBUG_PKT"])

# Report all telemetry across all targets, excluding targets/packets
report_all_targets_telemetry(
    exclude_targets=["IGNORED_TARGET"],
    exclude_packets=["DEBUG_PKT"]
)
```

The `report_telemetry` function is extremely useful, automatically tracking\
the previous state of telemetry, allowing for easy identification of changes\
between calls. The first call to `report_telemetry` for a specific packet will\
be treated as an initial report, but at any time you can reset the initial\
state if desired.

<br>

### Wait Utilities

The wait utilities provide comprehensive functions for waiting on and\
verifying telemetry conditions with flexible comparison options and \
requirement tracking.

Key features include:
- Wait for single telemetry value with flexible comparison operators (==, !=, <, <=, >, >=, contains, does_not_contain)
- Wait for multiple conditions simultaneously (all or any logic)
- Wait for telemetry value changes (any change detection)
- Wait for sequence counter increments (new packet detection)
- Wait for values within ranges (inclusive or exclusive)
- Wait for conditions within specific timing windows (min_time/max_time)
- Optional response timing measurement
- Integration with RequirementTracker for automated pass/fail tracking
- Expression-based waiting (COSMOS expressions)
- Value retrieval after waiting (check and return final value)
- State change tracking for multiple conditions
- Configurable timeouts and polling intervals
- Custom print function support for logging
- Sequence counter rollover handling

Basic usage examples:
```python
from cosmos_test_utils import (
    wait_for_telemetry_value, wait_for_telemetry_change,
    wait_for_sequence_count_change, wait_for_telemetry_in_range,
    wait_multiple_telemetry, wait_for_telemetry_in_timing_range
)

# Wait for a specific value
success = wait_for_telemetry_value(
    "TARGET", "HK_PACKET", "MODE", "==", "SCIENCE", 
    timeout=10.0
)

# Wait for any value change
success = wait_for_telemetry_change("TARGET", "HK_PACKET", "MODE")

# Wait for new packet (sequence count increment)
success = wait_for_sequence_count_change("TARGET", "HK_PACKET")

# Wait for value in range
success = wait_for_telemetry_in_range(
    "TARGET", "HK_PACKET", "VOLTAGE", 
    min_value=10.0, max_value=15.0
)

# Wait for multiple conditions (all must be true in this case)
success, results = wait_multiple_telemetry([
    ['TARGET', 'HK_PACKET', 'MODE', 'SCIENCE'],
    ['TARGET', 'HK_PACKET', 'BATTERY', '>=', 75]
])

# Wait with timing requirements and requirement tracking
from cosmos_test_utils import RequirementTracker
tracker = RequirementTracker()
success, response_time = wait_for_telemetry_in_timing_range(
    "TARGET", "HK_PACKET", "MODE", "==", "SCIENCE",
    min_time=1.0, max_time=5.0,
    requirement_ids="REQ-123", req_tracker=tracker
)

# Wait with return timing (no requirement tracking)
success, elapsed_time = wait_for_telemetry_value(
    "TARGET", "HK_PACKET", "MODE", "==", "SCIENCE",
    return_timing=True
)
```

These utilities provide flexible ways to wait for and verify telemetry\
conditions, supporting various comparison operators, timing requirements, and\
optional requirement tracking integration.

<br>

### Timing Utilities

The timing utilities provide comprehensive functions for measuring, tracking, \
and verifying timing requirements in COSMOS tests.

Key features include:
- Track multiple named timing events simultaneously
- High-precision timing option (using time.perf_counter())
- Start/stop/elapsed time measurement for named events
- Verify timing against min/max constraints
- Integration with RequirementTracker for automated pass/fail tracking
- Command response time measurement with flexible check functions
- Reset individual or all timers
- Running/stopped status tracking for all timers
- Comprehensive timing reports for all tracked events
- Ongoing elapsed time queries for running timers
- Custom print function support for logging

Basic usage examples:
```python
from cosmos_test_utils import TimingTracker, measure_command_response_time, RequirementTracker

# Create a timing tracker (optional high_precision=True for more accuracy)
timer = TimingTracker(high_precision=True)

# Start timing an operation
timer.start("critical_operation")

# Perform operation
cmd("TARGET COMMAND")

# Stop timer and get elapsed time
elapsed_time = timer.stop("critical_operation")

# Or get elapsed time without stopping (for running timers)
current_time = timer.elapsed("critical_operation")

# Verify timing meets constraints
success, elapsed, message = timer.verify_timing(
    "critical_operation", 
    min_time=1.0, 
    max_time=5.0
)
print(f"Timing result: {success}; elapsed: {elapsed}; message: {message}")

# Verify timing with requirement tracking
tracker = RequirementTracker()
success, elapsed, message = timer.verify_timing_requirement(
    requirement_ids="REQ-123, REQ-124",
    name="critical_operation",
    min_time=1.0,
    max_time=5.0,
    req_tracker=tracker
)

# Generate report of all timings
timer.report()

# Measure command response time with lambda functions
success, response_time = measure_command_response_time(
    lambda: cmd("TARGET COMMAND"),
    lambda: tlm("TARGET HK_TLM RESPONSE") == "COMPLETE",
    timeout=10.0
)
print(f"Command response time: {response_time:.3f} seconds")

# Reset specific or all timers
timer.reset("critical_operation")  # Reset one timer
timer.reset()  # Reset all timers
```

These utilities provide flexible ways to measure and verify timing\
requirements in your tests, supporting both simple elapsed time tracking and\
complex timing verification with requirement integration.

<br>

## Package Structure

```
cosmos_test_utils/
├── LICENSE                       # Apache 2.0 License
├── __init__.py                   # Package exports
├── pyproject.toml                # Package installation configuration
├── README.md                     # This file
├── stubs/                        # Type stubs for IDE support when developing
|                                 # this outside of a COSMOS environment
└── cosmos_test_utils/            # Main package code
    ├── command_utils.py          # Command sending and verification
    ├── event_utils.py            # Event message utilities
    ├── print_utils.py            # Enhanced printing with events
    ├── requirement_utils.py      # Requirement tracking and reporting
    ├── system_config.py          # Mission-specific configuration
    ├── telemetry_utils.py        # Telemetry tracking and reporting
    ├── test_tracking_utils.py    # Test and step auto-tracking and reporting
    ├── timing_utils.py           # Timing measurement utilities
    └── wait_utils.py             # Telemetry waiting functions
```

<br>

## Troubleshooting

### Common Issues

**Configuration Issues**: Verify `system_config.py` matches your COSMOS setup
- Check target names match your COSMOS targets
- Verify packet names match your telemetry definitions
- Ensure field names match your packet structures
- If packets are not being reported properly or the packet logger is creating an empty file then the config file may have a bad definition in it.

**Module Not found when running in COSMOS Script Runner**:
- You are likely on an older version of COSMOS
- Either update your COSMOS or build the package into a wheel file 
- See [creating a wheel file](#create-wheel-file)

<br>

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.
