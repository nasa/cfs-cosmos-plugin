# CS one-shot procedure checks

`test_02_OneShot` and `test_03_CancelOneShot` resolve `SAMPLE_LIB_Buffer`
through MM before checksumming its 16 bytes. The cancellation check waits for
running telemetry before sending cancellation. Both procedures verify that the
one-shot flag clears and that the CS command-error counter does not increase.
A failed check cancels a still-running one-shot started by the procedure.

These checks require MM, CS, and SAMPLE_LIB to be loaded, symbol lookup to be
enabled, and a housekeeping stream for MM and CS. No other client should send
commands to those applications during the checks. They use the current sample
library's 16-byte buffer; no memory is written by the procedures.

The one-shot consumes one byte per child-task cycle. With the default
`CS_CHILD_TASK_DELAY` of 1000 milliseconds, completion takes approximately
16 seconds, allowing the running state to appear in housekeeping. Missions with
a different child delay or slow telemetry must review the observation window
before using these checks. The procedures retain the suite's 100-second waits.
The checksum is not assumed to be zero: the sample buffer contains application
data and may have been changed by other memory tests.

Run the offline command/telemetry sequencing tests from the repository root:

```sh
python -m unittest discover -s tests -v
```

The offline tests load the actual ERB-substituted procedure with a simulated
telemetry source. They cover completion, cancellation, counter rollover, missing
symbols, and cleanup after failures. They do not replace live COSMOS/cFS testing.
