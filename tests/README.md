# Local conversion tests

Install the open-source `openc3` and `minitest` gems, then run from the repository root:

```sh
ruby -I targets/CFS/lib tests/test_cfs_time_conversion.rb
```

The tests render the actual telemetry and file header definitions, parse them using
OpenC3, and read their binary packet buffers. No running COSMOS server or flight
software is required, and no commands are transmitted. Telemetry subseconds use
16-bit binary fractions; standard cFE file timestamps use 32-bit binary fractions.
The existing epoch convention and the separate microsecond converter are preserved.
