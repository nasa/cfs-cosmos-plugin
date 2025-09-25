from openc3.script.suite import Group
# Verify ES commands work properly.  Not testing error cases.

# Group class name should indicate what the scripts are testing
class cfs_test_group_cfe_es(Group):
    """
    - Methods beginning with script_ or test_ are added to Script dropdown
    """

    def test_aliveness(self):
        """
        FSW Aliveness Test
        - Send a no-op command
            then verify the command was received (by checking the command counter incremented)
        - Reset the command counter
            then verify the command was received (by checking the command counter was cleared)
        """
        app_name = "CFE_ES"

        Group.print(f"Testing {app_name} aliveness on <%= target_name %>")

        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"{app_name}_HK", 1, 100)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER")

        # Send NOOP command, then check result to prove application is up and running
        cmd(f"<%= target_name %> {app_name}_CMD_NOOP")
        wait_check(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Send Reset Counters command, check resullt
        cmd(f"<%= target_name %> {app_name}_CMD_RESET_COUNTERS")
        wait_check(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER == 0", 100)


    def test_NoOp(self):
        """
        Test the no-op command.
        """
        cmd_count = tlm(f"<%= target_name %> ES_HK COMMAND_COUNTER")

        cmd(f"<%= target_name %> ES_CMD_NOOP")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Enable EVS events
        # FIXME: Are these not enabled by default?  If not, should this go in setup() in this file, or in the suite?
        #cmd("<%= target_name %> CFE_EVS_CMD_ENABLE_EVENT_TYPE with BIT_MASK INFO")
        #cmd("<%= target_name %> CFE_EVS_CMD_ENABLE_APP_EVENTS with APP_NAME 'SAMPLE_APP'")
        #wait(1)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 3 and " +
            "'No-op command' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_ProcessorRestart(self):
        """
        Test the Restart command specifying Processor Restart.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_RESTART RESTART_TYPE PROCESSOR")

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 1 and " +
            "'cFE ES Initialized' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())
    

    def test_PowerOnRestart(self):
        """
        Test the Restart command specifying Power-On Restart.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_RESTART RESTART_TYPE POWER_ON")

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 1 and " +
            "'cFE ES Initialized' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_StopApp(self):
        """
        Test the StopApp command.
        """

        cmd_count = tlm(f"<%= target_name %> ES_HK COMMAND_COUNTER")

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_STOP_APP APPLICATION c")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 7 and " +
            "'Stop Application SAMPLE_APP Initiated' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_StartApp(self):
        """
        Test the StartApp command.
        """

        cmd_count = tlm(f"<%= target_name %> ES_HK COMMAND_COUNTER")

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_START_APP APPLICATION SAMPLE_APP APP_ENTRY_POINT SAMPLE_APP_Main APP_FILE_NAME sample_app STACK_SIZE 16384 EXCEPTION_ACTION 0 PRIORITY 50")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 6 and " +
            "'Started SAMPLE_APP from sample_app' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_RestartApp(self):
        """
        Test the RestartApp command.
        """

        cmd_count = tlm(f"<%= target_name %> ES_HK COMMAND_COUNTER")

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_RESTART_APP APPLICATION SAMPLE_APP")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 10)"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_ReloadApp(self):
        """
        Test the ReloadApp command.
        """

        cmd_count = tlm(f"<%= target_name %> ES_HK COMMAND_COUNTER")

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_RELOAD_APP APPLICATION SAMPLE_APP APP_FILE_NAME sample_app")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 12)"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())
    

    def test_QueryOne(self):
        """
        Test the QueryOne command.
        """

        cmd_count = tlm(f"<%= target_name %> ES_HK COMMAND_COUNTER")

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        # FIXME: Debug events need to be enabled before this command - probably in setup function, if not enabled by default.
        cmd(f"<%= target_name %> ES_CMD_QUERY_ONE APPLICATION SAMPLE_APP")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 15 and " +
            "'Sent SAMPLE_APP application data' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_QueryAll(self):
        """
        Test the QueryAll command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        # FIXME: Debug events need to be enabled before this command - probably in setup function, if not enabled by default.
        cmd(f"<%= target_name %> ES_CMD_QUERY_ALL FILE_NAME apps.txt")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 16 and " +
            "'App Info file written to apps.txt' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_QueryAllTasks(self):
        """
        Test the QueryAllTasks command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        # FIXME: Debug events need to be enabled before this command - probably in setup function, if not enabled by default.
        cmd(f"<%= target_name %> ES_CMD_QUERY_ALL_TASKS FILE_NAME sample_app")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 87 and " +
            "'Task Info file written to sample_app' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_ClearSysLog(self):
        """
        Test the ClearSysLog command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_CLEAR_SYS_LOG")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 17 and " +
            "'Cleared Executive Services log data' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())
    

    def test_WriteSysLog(self):
        """
        Test the WriteSysLog command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_WRITE_SYS_LOG FILE_NAME logfile.txt")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 18 and " +
            "'logfile.txt written' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_OverwriteSysLog_Discard(self):
        """
        Test the OverwriteSysLog command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        # FIXME: Debug events need to be enabled before this command - probably in setup function, if not enabled by default.
        cmd(f"<%= target_name %> ES_CMD_OVERWRITE_SYS_LOG MODE DISCARD")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 70 and " +
            "'Set OverWriteSysLog Command Received with Mode setting = DISCARD' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())
    

    def test_OverwriteSysLog_Overwrite(self):
        """
        Test the OverwriteSysLog command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        # FIXME: Debug events need to be enabled before this command - probably in setup function, if not enabled by default.
        cmd(f"<%= target_name %> ES_CMD_OVERWRITE_SYS_LOG MODE OVERWRITE")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 70 and " +
            "'Set OverWriteSysLog Command Received with Mode setting = OVERWRITE' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_ClearERLog(self):
        """
        Test the ClearERLog command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_CLEAR_ER_LOG")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 19 and " +
            "'Cleared ES Exception and Reset Log data' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())
    

    def test_WriteERLog(self):
        """
        Test the WriteERLog command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        # FIXME: Debug events need to be enabled before this command - probably in setup function, if not enabled by default.
        cmd(f"<%= target_name %> ES_CMD_WRITE_ER_LOG FILE_NAME logfile.txt")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 20 and " +
            "'logfile.txt written' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_StartPerfData(self):
        """
        Test the StartPerfData command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        # FIXME: Debug events need to be enabled before this command - probably in setup function, if not enabled by default.
        cmd(f"<%= target_name %> ES_CMD_START_PERF_DATA TRIGGER_MODE START")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 57 and " +
            "'Start collecting performance data cmd received, trigger mode = START' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_StopPerfData(self):
        """
        Test the StopPerfData command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        # FIXME: Debug events need to be enabled before this command - probably in setup function, if not enabled by default.
        cmd(f"<%= target_name %> ES_CMD_STOP_PERF_DATA DATA_FILE_NAME datafile.txt")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 60 and " +
            "'Perf Stop Cmd Rcvd' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_SetPerfFilterMask(self):
        """
        Test the SetPerfFilterMask command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        # FIXME: Debug events need to be enabled before this command - probably in setup function, if not enabled by default.
        cmd(f"<%= target_name %> ES_CMD_SET_PERF_FILTER_MASK FILTER_MASK_NUM 1 FILTER_MASK 10")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 63 and " +
            "'Set Performance Filter Mask Cmd rcvd, num 1, val 0x00001010' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_SetPerfTriggerMask(self):
        """
        Test the SetPerfTriggerMask command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        # FIXME: Debug events need to be enabled before this command - probably in setup function, if not enabled by default.
        cmd(f"<%= target_name %> ES_CMD_SET_PERF_TRIGGER_MASK TRIGGER_MASK_NUM 1 TRIGGER_MASK 10")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 65 and " +
            "'Set Performance Trigger Mask Cmd rcvd,num 1, val 0x00001010' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_ResetPRCount(self):
        """
        Test the ResetPRCount command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_RESET_PR_COUNT")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 72 and " +
            "'Set Processor Reset Count to Zero' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_SetMaxPRCount(self):
        """
        Test the SetMaxPRCount command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_SET_MAX_PR_COUNT MAX_PR_COUNT 1")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 73 and " +
            "'Maximum Processor Reset Count set to: 1' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_DeleteCDS(self):
        """
        Test the DeleteCDS command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_DELETE_CDS CDS_NAME 'cdsfile'")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 78 and " +
            "'Successfully removed \'cdsfile\' from CDS' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())
    

    def test_SendMemPoolStats(self):
        """
        Test the SendMemPoolStats command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        # FIXME: Debug events need to be enabled before this command - probably in setup function, if not enabled by default.
        cmd(f"<%= target_name %> ES_CMD_SEND_MEM_POOL_STATS APPLICATION 'TO' POOL_HANDLE 0x00000000")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 81 and " +
            "'Successfully telemetered memory pool stats for 0x00000000' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_DumpCDSRegistry(self):
        """
        Test the DumpCDSRegistry command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        # FIXME: Debug events need to be enabled before this command - probably in setup function, if not enabled by default.
        cmd(f"<%= target_name %> ES_CMD_DUMP_CDS_REGISTRY DUMP_FILENAME 'dumpfile.txt'")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 83 and " +
            "'Successfully dumped CDS Registry to \'dumpfile.txt\'' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def test_ResetCounters(self):
        """
        Test the ResetCounters command.
        """

        # FIXME: First, cause command error counter to increment

        cmd(f"<%= target_name %> ES_CMD_RESET_COUNTERS")

        # Verify command count is reset to zero
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == 0", 100)

        # Verify command error count is reset to zero
        wait_check(f"<%= target_name %> ES_HK COMMAND_ERROR_COUNTER == 0", 100)

        # Wait for event
        event_expression = (
            f"tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'ES' and " +
            "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 4 and " +
            "'Successfully dumped CDS Registry to \'dumpfile.txt\'' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
            )
        wait_check_expression(event_expression, 5, 0.5, globals())


    def setup(self):
        """
        Test Group Setup
        - Runs when Group Setup button is pressed
        - Runs before all scripts when Group Start is pressed
        """
        pass

    def teardown(self):
        """
        Test Group Setup
        - Runs when Group Teardown button is pressed
        - Runs after all scripts when Group Start is pressed
        """
        pass
