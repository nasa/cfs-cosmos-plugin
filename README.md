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

   Your IDE can be setup to recognize that directory as a place to resolve \
   the functions and enable autocompletion for easier development. Use your \
   favorite search to find out how to do that. 
   
   Other options for placement may be in a specific TARGET/lib so that if that\
   target is not included the package will not be built into the gem file \
   loaded into COSMOS. This would be the way to go if you have a sepcific \
   testing target that are not deployed to users.
   
   Older versions of COSMOS (before 6.9.0) will need to create a Wheel file of\
   this package and load that in COSMOS. There was a bug in COSMOS that \
   prevented the script runner from seeing Python packages.

2. **Configure for your mission:**

   Edit cosmos_test_utils\cosmos_test_utils\system_config.py to match your \
   COSMOS setup. This file contains all of the variable names and structures \
   that require project specific mnemonics to be set in order to work properly\
   with your system.

   Things like:
   ```python
   EVENT_TARGET_NAME = "YOUR_EVS_TARGET"
   EVENT_PACKET_NAME = "YOUR_CFS_LONG_EVENT_PACKET"
   ```

3. **If you are on COSMOS 6.9.0 or later, you are done.**

<br>

<details>
<summary><strong>If you are on an earlier version of COSMOS, follow these instructions:</strong></summary>

4. <strong id="create-wheel-file">(CONDITIONAL) Create the wheel file for loading into COSMOS</strong>

   > **NOTE:** This step is only needed if running an older version of COSMOS.\
   > Skip this step if you are running on the latest version of COSMOS.\
   > If the Script runner does not recognize the modules, then you will\
   > have to build and load the Wheel.

   I built and tested with 3.12, but you can build with Python 3.6 or higher.

   ```bash
   python3.12 -m build --wheel
   ```

5. **Load the package into COSMOS:**
   1. With COSMOS running, browse to "ADMIN CONSOLE"
   2. On the top of that page, select "Packages"
   3. Click where it says "Click to select file(s) to add to COSMOS"
   4. Browse to where the wheel file was created, select it, and press "open" \
   (nominally: PLUGIN\lib\cosmos_test_utils\dist)
   5. Press the button on the right labeled "Upload"

   After COSMOS finishes processing the Wheel file, you should see the\
   package appear in the list under "Python Packages" at the bottom of the page.

</details>


## Suggested Use
   
   The easiest way to integrate this into your test scripts is to include the \
   following line it your tests:
   ```python
   import cosmos_test_utils as ctu
   ```
   This will give you access to all functions available in the package in your \
   scripts and avoid name collisions. The examples further in this file import \
   specific functions to show how selective import could work if desired. 

   Depending on where you place the package source, you should be able to get \
   your particular IDE to recognize the functions of this package and even enable \
   autocompletion. You will need to refer to help specific to that IDE in order to \
   do that. 

   This README only encompasses things related to this package.


## System Configuration

The package includes a `system_config.py` file that contains mission-specific \
configuration parameters. Users should customize this file to match their specific \
COSMOS environment. If you do not have common CCSDS header field names and \
you want to use this you will have to rework your headers to have the same names \
across all packets.

Key configurations include:
- Event message target and packet names
- Event packet field names
- Event type mappings
- Common telemetry field names
- Default timeouts and polling intervals

See the cosmos_test_utils/cosmos_test_utils/system_config.py for all configurable \
variables.

## Key Features

### Command Utilities

The CommandSender class provides robust functionality for sending commands, \
verifying responses, and tracking command history in COSMOS tests. Key features \
include:
- Sending basic commands and commands with parameters
- Executing commands multiple times with a configurable delay between each
- Verifying command responses with flexible comparison options
- Tracking and reporting on requirements associated with commands
- Detailed command history tracking and reporting
- Ability to set time constraints on the responses for timing requirement testing

Basic usage example:
```python
from cosmos_test_utils import CommandSender

# Initialize a command sender
sender = CommandSender()

# Send a command and verify the response
success = sender.send_cmd_with_response_check(
    "TARGET SET_MODE with MODE 'SCIENCE'",
    target="TARGET", packet="HK_TLM", 
    item="MODE", comparison="==", comparison_value="SCIENCE"
)

# Get response time from last command (optional)
last_cmd = sender.get_command_history(1)[0]
if 'response' in last_cmd:
    response_time = last_cmd['response']['time']
    print(f"Last command response time: {response_time:.3f}s")

```


For comprehensive usage examples demonstrating all of the features, see \
`examples/command_examples.py`. \

This file includes:
- Basic command sending
- Multiple command execution
- Response checking
- Requirement verification
- Timing requirement verification
- Command history access and printing at various detail levels

The example file also demonstrates how to use the CommandSender with both real \
COSMOS functions and mock functions for testing purposes.


### Event Utilities

Capture and analyze event messages from the system under test.

Key features include:

- Setting up event search and logging
- Finding specific events
- Printing captured events to the test log
- Background event logging to console or file
- Automatic event printing with test operations  

Basic usage example:

```python
from cosmos_test_utils import set_event_search_point, find_events, start_background_event_logging, stop_background_event_logging
from openc3.script import cmd 

#start logging all events to a separate file
start_background_event_logging()

# Start event capture
set_event_search_point()

# Send commands
cmd("TARGET COMMAND")

# Check for specific events
success, count = find_events(
    "TARGET_APP", 5, "INFO", "Command executed"
)

# Stop the parallel process that is putting events into a separate log
stop_background_event_logging()
```

For more detailed usage examples, see `examples/event_examples.py`. This \
comprehensive example demonstrates all key features of the event utilities, \
including basic searching, script logging, and background event logging \
in more detail.

### Requirement Tracking

The RequirementTracker class provides functionality for tracking and reporting on \
requirements verification during testing. 

Key features include:
- Setting and updating requirement statuses
- Handling multiple requirements simultaneously
- Generating detailed reports with requirement histories
- Enforcing valid state transitions for requirements

Basic usage example:
```python
from cosmos_test_utils import RequirementTracker

# Initialize a tracker
req_tracker = RequirementTracker()

# Initialize requirement status (Optional, but good practice to flag any untested requirements in the test)
req_tracker.set_multiple_requirements("REQ-123, REQ-456", "U", "Initialize Requirements expected to be tested.")

# Set requirement status
req_tracker.set_requirement("REQ-123", "P", "Verified by command test")
req_tracker.set_requirement("REQ-456", "F", "Failed timeout condition")

# Generate report
print(req_tracker.generate_requirements_report())
```

The RequirementTracker can also be used to track anything, like telemetry points \
or tests executed. The requirement to be updated is just a string that you can \
set to anything:

```python
req_tracker.set_requirement("HK_CmdCnt", "P", "Verified that this increments as expected")
req_tracker.set_requirement("Noop EM", "P", "Event Message received as expected")
```
Use of this will only be limited by your creativity.

For comprehensive usage examples demonstrating all features, see \
`examples/requirement_examples.py`. 

This file includes:
- Basic RequirementTracker usage
- Setting and updating requirement states
- Generating basic and detailed reports
- Setting multiple requirements at once
- Testing requirement state transition rules
- Using different report styles

The example file demonstrates various ways to use the RequirementTracker class, \
including integration with COSMOS Group printing for test suites.


### Telemetry Utilities

The telemetry utilities provide functions for monitoring and reporting telemetry \
changes in COSMOS tests. Key features include:

- Reporting changes in specific telemetry packets
- Monitoring multiple packets across a target
- System-wide telemetry reporting
- Customizable detail levels for reports
- Ability to exclude specific packets or targets

Basic usage example:
```python
from cosmos_test_utils import report_telemetry, report_all_telemetry, report_all_targets_telemetry

# Report initial packet, all points
report_telemetry("TARGET", "HK_PACKET", level_of_detail=1)

# ... perform operations ...
# Report changes in that specific packet
report_telemetry("TARGET", "HK_PACKET")

# Report all telemetry for a target. 
# Any packets not previously reported will be treated as an intial packet in the report.
report_all_telemetry("TARGET")

# Report all telemetry across all targets 
# Any pkts not previously reported are treated as an intial pkt in the report.
report_all_targets_telemetry()
```

These utilities automatically track the previous state of telemetry, allowing for \
easy identification of changes between calls. The first call to `report_telemetry` \
for a specific packet will be treated as an initial report.

For comprehensive usage examples demonstrating all features, see \
`examples/telemetry_examples.py`.

This file includes:
- Basic telemetry change reporting
- Multiple packet monitoring
- System-wide telemetry reporting
- Custom telemetry change detection

The example file demonstrates various ways to use the telemetry utilities, \
including:
- Setting different detail levels
- Excluding specific packets or targets
- Simulating spacecraft operations and analyzing resulting changes


### Wait Utilities

Wait for specific telemetry conditions with flexible comparison options.

```python
from cosmos_test_utils import wait_for_telemetry_value, wait_for_telemetry_in_range

# Wait for a specific value
success = wait_for_telemetry_value(
    "TARGET", "HK_PACKET", "MODE", "==", "SCIENCE", 
    timeout=10.0
)

# Wait for a value in a range
success = wait_for_telemetry_in_range(
    "TARGET", "HK_PACKET", "VOLTAGE", 
    min_value=10.0, max_value=15.0
)
```

These utilities provide flexible ways to wait for and verify telemetry conditions, \
supporting various comparison operators and timing requirements.

For comprehensive usage examples demonstrating all features, see \
`examples/wait_examples.py`. 

This file includes:
- Basic telemetry value waiting
- Custom comparison operators
- Waiting for telemetry changes
- Sequence counter monitoring
- Range-based waiting
- Multiple condition waiting
- Integration with requirement tracking

The example file demonstrates various ways to use the wait utilities, including:
- Setting custom timeouts and polling intervals
- Using different comparison operators
- Handling multiple conditions simultaneously
- Integrating with requirement tracking systems


### Timing Utilities

The timing utilities provide functions for measuring, tracking, and verifying \
timing requirements in COSMOS tests. Key features include:

- Tracking multiple timing events simultaneously
- Verifying timing against specified constraints
- Integration with requirement tracking
- High-precision timing option
- Command response time measurement

Basic usage example:
```python
from cosmos_test_utils import TimingTracker, measure_command_response_time
from openc3.script import cmd, tlm

# Create a timing tracker
timer = TimingTracker()

# Start timing an operation
timer.start("critical_operation")

# Perform operation
cmd("TARGET COMMAND")

# Stop timer
timer.stop("critical_operation")

# Verify the amount of time is in the timing window as desired
# if stop is not called the timer will continue and this is just a snapshot at that point
success, elapsed, message = timer.verify_timing("critical_operation", min_time=1.0, max_time=5.0)
print(f"Timing result: {success}; elapsed time: {elapsed}; returned message: {message}")

# Measure command response time
success, response_time = measure_command_response_time(
    lambda: cmd("TARGET COMMAND"),
    lambda: tlm("TARGET HK_TLM RESPONSE") == "COMPLETE"
)

print(f"Command response time: {response_time:.3f} seconds")
```

These utilities provide flexible ways to measure and verify timing requirements in \
your tests, supporting both simple and complex timing scenarios.

For comprehensive usage examples demonstrating all features, see \
`examples/timing_examples.py`. 

This file includes:
- Basic timing tracking
- Multiple simultaneous timing events
- Verifying timing against requirements
- Command response time measurement
- Integration with requirement tracking  
  
The example file demonstrates various ways to use the timing utilities, including:
- Using high-precision timing
- Generating timing reports
- Verifying timing constraints
- Measuring command response times
- Integrating with requirement tracking systems


## Examples

To bring together all of the Key Features section take-aways:
The `examples/` directory contains detailed examples of each utility:

- `command_examples.py`: Command sending and verification
- `event_examples.py`: Event message handling
- `requirement_examples.py`: Requirement tracking
- `telemetry_examples.py`: Telemetry monitoring
- `timing_examples.py`: Timing measurement
- `wait_examples.py`: Telemetry waiting


## Package Structure

```
cosmos_test_utils/
├── __init__.py                   # Package exports
├── pyproject.toml                # Package installation configuration
├── README.md                     # This file
├── stubs/                        # Type stubs for IDE support when developing\
                                       # this outside of a COSMOS environment
├── examples/                     # Example usage scripts
│   ├── command_examples.py       # CommandSender examples
│   ├── event_examples.py         # Event utilities examples
│   ├── requirement_examples.py   # RequirementTracker examples
│   ├── telemetry_examples.py     # Telemetry utilities examples
│   ├── timing_examples.py        # TimingTracker examples
│   └── wait_examples.py          # Wait utilities examples
└── cosmos_test_utils/            # Main package code
    ├── command_utils.py          # Command sending and verification
    ├── event_utils.py            # Event message utilities
    ├── print_utils.py            # Enhanced printing with events
    ├── requirement_utils.py      # Requirement tracking and reporting
    ├── system_config.py          # Mission-specific configuration
    ├── telemetry_utils.py        # Telemetry tracking and reporting
    ├── timing_utils.py           # Timing measurement utilities
    ├── wait_utils.py             # Telemetry waiting functions
    └── write_event_log.py        # Background event logging script
```

## Troubleshooting

### Common Issues

**Configuration Issues**: Verify `system_config.py` matches your COSMOS setup
- Check target names match your COSMOS targets
- Verify packet names match your telemetry definitions
- Ensure field names match your packet structures

**Module Not found when running in COSMOS Script Runner**:
- You are likely on an older version of COSMOS
- Either update your COSMOS or build the package into a wheel file 
- See [creating a wheel file](#create-wheel-file)

## Support

For questions, issues, or support:
- **Examples**: See the `examples/` directory for detailed usage scenarios 
- **Issues**: Report bugs and feature requests through [TBD]
- **Contact**: Damon Stewart at NASA GSFC (damon.stewart@nasa.gov)

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.
