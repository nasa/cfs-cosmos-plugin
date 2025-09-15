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

        # Check for NoOp event
        # FIXME: how?


    def test_ProcessorRestart(self):
        """
        Test the Restart command specifying Processor Restart.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_RESTART RESTART_TYPE PROCESSOR")

        # FIXME: Wait for event message CFE_ES_INIT_INF_EID (1)
    

    def test_PowerOnRestart(self):
        """
        Test the Restart command specifying Power-On Restart.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_RESTART RESTART_TYPE POWER_ON")

        # FIXME: Wait for event message CFE_ES_INIT_INF_EID (1)


    def test_StopApp(self):
        """
        Test the StopApp command.
        """

        cmd_count = tlm(f"<%= target_name %> ES_HK COMMAND_COUNTER")

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_STOP_APP APPLICATION SAMPLE_APP")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message FIXME (probably the app's termination message)


    def test_StartApp(self):
        """
        Test the StartApp command.
        """

        cmd_count = tlm(f"<%= target_name %> ES_HK COMMAND_COUNTER")

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_START_APP APPLICATION SAMPLE_APP APP_ENTRY_POINT SAMPLE_APP_Main APP_FILE_NAME sample_app STACK_SIZE 16384 EXCEPTION_ACTION 0 PRIORITY 50")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message FIXME (probably the app's init message)


    def test_RestartApp(self):
        """
        Test the RestartApp command.
        """

        cmd_count = tlm(f"<%= target_name %> ES_HK COMMAND_COUNTER")

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_RESTART_APP APPLICATION SAMPLE_APP")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message


    def test_ReloadApp(self):
        """
        Test the ReloadApp command.
        """

        cmd_count = tlm(f"<%= target_name %> ES_HK COMMAND_COUNTER")

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_RELOAD_APP APPLICATION SAMPLE_APP APP_FILE_NAME sample_app")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message
    

    def test_QueryOne(self):
        """
        Test the QueryOne command.
        """

        cmd_count = tlm(f"<%= target_name %> ES_HK COMMAND_COUNTER")

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_QUERY_ONE APPLICATION SAMPLE_APP")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message


    def test_QueryAll(self):
        """
        Test the QueryAll command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_QUERY_ALL FILE_NAME sample_app")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message


    def test_QueryAllTasks(self):
        """
        Test the QueryAllTasks command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_QUERY_ALL_TASKS FILE_NAME sample_app")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message


    def test_ClearSysLog(self):
        """
        Test the ClearSysLog command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_CLEAR_SYS_LOG")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message
    

    def test_WriteSysLog(self):
        """
        Test the WriteSysLog command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_WRITE_SYS_LOG FILE_NAME logfile.txt")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message


    def test_OverwriteSysLog_Discard(self):
        """
        Test the OverwriteSysLog command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_OVERWRITE_SYS_LOG MODE DISCARD")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message
    

    def test_OverwriteSysLog_Overwrite(self):
        """
        Test the OverwriteSysLog command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_OVERWRITE_SYS_LOG MODE OVERWRITE")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message


    def test_ClearERLog(self):
        """
        Test the ClearERLog command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_CLEAR_ER_LOG")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message
    

    def test_WriteERLog(self):
        """
        Test the WriteERLog command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_WRITE_ER_LOG FILE_NAME logfile.txt")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message


    def test_StartPerfData(self):
        """
        Test the StartPerfData command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_START_PERF_DATA TRIGGER_MODE START")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message


    def test_StopPerfData(self):
        """
        Test the StopPerfData command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_STOP_PERF_DATA DATA_FILE_NAME datafile.txt")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message


    def test_SetPerfFilterMask(self):
        """
        Test the SetPerfFilterMask command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_SET_PERF_FILTER_MASK FILTER_MASK_NUM 1 FILTER_MASK 10")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message


    def test_SetPerfTriggerMask(self):
        """
        Test the SetPerfTriggerMask command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_SET_PERF_TRIGGER_MASK TRIGGER_MASK_NUM 1 TRIGGER_MASK 10")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message


    def test_ResetPRCount(self):
        """
        Test the ResetPRCount command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_RESET_PR_COUNT")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message


    def test_SetMaxPRCount(self):
        """
        Test the SetMaxPRCount command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_SET_MAX_PR_COUNT MAX_PR_COUNT 1")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message


    def test_DeleteCDS(self):
        """
        Test the DeleteCDS command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_DELETE_CDS CDS_NAME 'cdsfile.bin'")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message
    

    def test_SendMemPoolStats(self):
        """
        Test the SendMemPoolStats command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_SEND_MEM_POOL_STATS APPLICATION 'TO' POOL_HANDLE 0x00000000")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message


    def test_DumpCDSRegistry(self):
        """
        Test the DumpCDSRegistry command.
        """

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_DUMP_CDS_REGISTRY DUMP_FILENAME 'dumpfile.txt'")

        # Verify command count incremented
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # FIXME: Wait for event message



    # FIXME: Test CFE_ES_RESET_COUNTERS_CC (after other tests increment all counters (cmd count, cmd error count)
    def test_ResetCounters(self):
        """
        Test the ResetCounters command.
        """

        # FIXME: First, cause command error counter to increment

        # FIXME: Verify correct names for command, parameter name, and parameter value.  Also in other tests.

        cmd(f"<%= target_name %> ES_CMD_RESET_COUNTERS")

        # Verify command count is reset to zero
        wait_check(f"<%= target_name %> ES_HK COMMAND_COUNTER == 0", 100)

        # Verify command error count is reset to zero
        wait_check(f"<%= target_name %> ES_HK COMMAND_ERROR_COUNTER == 0", 100)

        # FIXME: Wait for event message

    
        











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
