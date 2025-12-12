from openc3.script.suite import Group
# Verify ES commands work properly.  Not testing error cases.

sample_app_needs_shutdown_at_end = False

# Group class name should indicate what the scripts are testing
class cfs_test_group_cfe_es(Group):
    """
    - Methods beginning with script_ or test_ are added to Script dropdown
    """
    
    def test_00_Aliveness(self):
        """
        FSW Aliveness Test
        - Send a no-op command
            then verify the command was received (by checking the command counter incremented)
        - Reset the command counter
            then verify the command was received (by checking the command counter was cleared)
        """
        
        Group.print("Testing CFE_ES aliveness on <%= target_name %>")
        
        wait_check_packet("<%= target_name %>", "CFE_ES_HK", 1, 100)
        
        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm("<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send NOOP command, then check result to prove application is up and running
        cmd("<%= target_name %> CFE_ES_CMD_NOOP")
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # Send Reset Counters command, check resullt
        cmd("<%= target_name %> CFE_ES_CMD_RESET_COUNTERS")
        wait_check("<%= target_name %> CFE_ES_HK COMMAND_COUNTER == 0", 100)
    
    
    def test_01_NoOp(self):
        """
        Test the no-op command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CFE_ES_CMD_NOOP")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # DS: I found that the cFS-integration-sandbox version of cFS was sending out all packets at 1/sec
        #     This is causing many packets to be dropped. Issue is: https://developer.nasa.gov/cFS/cFS/issues/435
        #     That is why the event verification is spotty throughout the test. Sometimes the event message gets dropped.
        #     Regardless, The event verification is being descoped for now, so I'm commenting out all EM verification 
        #     sections for the initial iteration of this function.
        #     I will be adding a python package I created that will make finding event messages way simpler in future revisions.
        
        # FIXME: Command succeeds with correct message, but check fails sometimes.
        # Verify event message
        #wait_check("<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME == 'CFE_ES'", 100)
        #wait_check("<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID == 3", 100)
        # FIXME: error: wait_check("'No-op command' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE'", 100)
        #wait_check_expression("'No-op command' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')", 10, 0.5, globals())
        
        # FIXME: This section is redundant with the section after (except this doesn't guarantee they're all true at the same time).
        #        I thought it passed before without it (after removing 'f' below), but this time it didn't.
        #        Then another run, these lines failed, even though correct on terminal.
        #        Is it a random timing thing?  Some of the similar checks in other test steps also failing when correct on terminal.
        # Wait for event
        # wait_check_expression("tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES'", 5, 0.5, globals())
        # wait_check_expression("tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 3", 5, 0.5, globals())
        # wait_check_expression("'No-op command' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')", 5, 0.5, globals())
        
        # Wait for event
        # event_expression = (
        #     "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #     "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 3 and " +
        #     "'No-op command' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #     )
        # wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    # FIXME: Currently don't have a good way to restart cFS from COSMOS.
    #        Default CFS platform just stops FSW from a reset command.
    def test_02_ProcessorRestart(self):
        """
        Test the Restart command specifying Processor Restart.
        """
            
        Group.print("Test Skipped: Currently do not have a good way to restart cFS from COSMOS")
        Group.print("              Default CFS platform just stops FSW from a reset command.")
        
        ## Send command under test
        #cmd(f"<%= target_name %> CFE_ES_CMD_RESTART with RESTART_TYPE PROCESSOR")
        #
        ##    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        ##        See my comment about event messages in the test_01_NoOp function
        ## Wait for event
        ##event_expression = (
        ##    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        ##    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 1 and " +
        ##    "'cFE ES Initialized' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        ##    )
        ##wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    # FIXME: Currently don't have a good way to restart cFS from COSMOS.
    #        Default CFS platform just stops FSW from a reset command.
    def test_03_PowerOnRestart(self):
        """
        Test the Restart command specifying Power-On Restart.
        """
        Group.print("Test Skipped: Currently do not have a good way to restart cFS from COSMOS")
        Group.print("              Default CFS platform just stops FSW from a reset command.")
        
        ## Send command under test
        #cmd(f"<%= target_name %> CFE_ES_CMD_RESTART with RESTART_TYPE POWER_ON")
        #
        ##    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        ##        See my comment about event messages in the test_01_NoOp function
        ## Wait for event
        ##event_expression = (
        ##    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        ##    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 1 and " +
        ##    "'cFE ES Initialized' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        ##    )
        ##wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_04_StopApp_StartApp(self):
        """
        Test the StopApp and StartApp commands.
        It is determined whether the Sample_App is running at the start or not
        and then the order of the test steps are changed based on this info.
        the Sample_App will be in the same state as it was when this test began 
        """
        
        if(self.is_Sample_App_Running()):
            #Sample_App is running
            self.StopApp_test()
            wait(1)
            self.StartApp_test()
            wait(1)
        else:
            # Sample_app is not running
            self.StartApp_test()
            wait(1)
            self.StopApp_test()
            wait(1)
    
    
    def test_05_RestartApp(self):
        """
        Test the RestartApp command.
        """
        
        stopSampleAppAtEnd = False
        # This test needs the Sample_App running
        # If it is not running, start it, setting a var to stop it at the end of the test
        # This is to make this test runnable even if the setup function was not executed
        if(not self.is_Sample_App_Running()):
            stopSampleAppAtEnd = True
            self.StartApp_test()
            wait(1)
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_RESTART_APP with APPLICATION 'SAMPLE_APP'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # FIXME: Add check for expected text of message.
        # FIXME: Command succeeds with correct message, but check fails.
        #    DS: Same issue as the StartApp event. Right after ES sends the restart event, the sample app sends it's 
        #        init event, so the event you are checking against is the sample app message.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 10"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
        
        wait(10) # Wait for the app to fully restart (5 for stop, 5 for start).
        
        if(stopSampleAppAtEnd):
            self.StopApp_test()
    
    
    def test_06_ReloadApp(self):
        """
        Test the ReloadApp command.
        """
        
        stopSampleAppAtEnd = False
        # This test needs the Sample_App running
        # If it is not running, start it, setting a var to stop it at the end of the test
        # This is to make this test runnable even if the setup function was not executed
        if(not self.is_Sample_App_Running()):
            stopSampleAppAtEnd = True
            self.StartApp_test()
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_RELOAD_APP with APPLICATION 'SAMPLE_APP', APP_FILE_NAME 'sample_app'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # FIXME: Add check for expected text of message.
        # FIXME: Command succeeds with correct message, but check fails.
        #    DS: Same issue as the StartApp and RestartApp event. Right after ES sends the reload event, the sample app sends it's 
        #        init event, so the event you are checking against is the sample app message.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 12"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
        
        wait(10) # Wait for the app to fully restart (5 for stop, 5 for start).

        if(stopSampleAppAtEnd):
            self.StopApp_test()
    
    
    def test_07_QueryOne(self):
        """
        Test the QueryOne command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_QUERY_ONE with APPLICATION 'CS'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # FIXME: Command succeeds with correct message, but check fails.
        #    DS: This is due to an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 15 and " +
        #    "'Sent CS application data' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_08_QueryAll(self):
        """
        Test the QueryAll command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_QUERY_ALL with FILE_NAME 'apps.txt'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # FIXME: Command succeeds with correct message, but check fails.
        #    DS: This is due to an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 16 and " +
        #    "'App Info file written to /ram/apps.txt' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_09_QueryAllTasks(self):
        """
        Test the QueryAllTasks command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under tests
        cmd(f"<%= target_name %> CFE_ES_CMD_QUERY_ALL_TASKS with FILE_NAME 'sample_app'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        #    DS: This is due to an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 87 and " +
        #    "'Task Info file written to /ram/sample_app' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_10_WriteSysLog(self):
        """
        Test the WriteSysLog command.
        """
        
        cmd_count = tlm("<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd("<%= target_name %> CFE_ES_CMD_WRITE_SYS_LOG with FILE_NAME 'logfile.txt'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        #    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 18 and " +
        #    "'/ram/logfile.txt written' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_11_ClearSysLog(self):
        """
        Test the ClearSysLog command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_CLEAR_SYS_LOG")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # FIXME: Command succeeds with correct message, but check fails SOMETIMES.
        #    DS: This is due to an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 17 and " +
        #    "'Cleared Executive Services log data' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_12_OverwriteSysLog_Discard(self):
        """
        Test the OverwriteSysLog command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_OVER_WRITE_SYS_LOG with MODE DISCARD")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        #    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 70 and " +
        #    "'Set OverWriteSysLog Command Received with Mode setting = 1' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_13_OverwriteSysLog_Overwrite(self):
        """
        Test the OverwriteSysLog command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_OVER_WRITE_SYS_LOG with MODE OVERWRITE")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        #    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 70 and " +
        #    "'Set OverWriteSysLog Command Received with Mode setting = 0' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_14_WriteERLog(self):
        """
        Test the WriteERLog command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_WRITE_ER_LOG with FILE_NAME 'logfile.txt'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        #    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 20 and " +
        #    "'/ram/logfile.txt written' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_15_ClearERLog(self):
        """
        Test the ClearERLog command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_CLEAR_ER_LOG")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        #    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 19 and " +
        #    "'Cleared ES Exception and Reset Log data' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_16_StartPerfData(self):
        """
        Test the StartPerfData command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_START_PERF_DATA with TRIGGER_MODE START")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        #    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 57 and " +
        #    "'Start collecting performance data cmd received, trigger mode = 0' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_17_StopPerfData(self):
        """
        Test the StopPerfData command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_STOP_PERF_DATA with DATA_FILE_NAME 'datafile.txt'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # FIXME: Command succeeds with correct message, but check fails.
        #    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 60 and " +
        #    "'Perf Stop Cmd Rcvd' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_18_SetPerfFilterMask(self):
        """
        Test the SetPerfFilterMask command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_SET_PERF_FILTER_MASK with FILTER_MASK_NUM 1, FILTER_MASK 10")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # FIXME: Command succeeds with correct message, but check fails.
        #    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 63 and " +
        #    "'Set Performance Filter Mask Cmd rcvd, num 1, val 0x0000000A' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_19_SetPerfTriggerMask(self):
        """
        Test the SetPerfTriggerMask command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_SET_PERF_TRIGGER_MASK with TRIGGER_MASK_NUM 1, TRIGGER_MASK 10")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        #    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 65 and " +
        #    "'Set Performance Trigger Mask Cmd rcvd,num 1, val 0x0000000A' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_20_ResetPRCount(self):
        """
        Test the ResetPRCount command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_RESET_PR_COUNT")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        #    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 72 and " +
        #    "'Set Processor Reset Count to Zero' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_21_SetMaxPRCount(self):
        """
        Test the SetMaxPRCount command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_SET_MAX_PR_COUNT with MAX_PR_COUNT 1")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        #    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 73 and " +
        #    "'Maximum Processor Reset Count set to: 1' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    # FIXME: Add this back when we start implementing non-nominal test cases.
    #
    # def test_X_DeleteCDS_Error_AppActive(self):
    #     """
    #     Test the DeleteCDS command.
    #     """
    #
    #     # First, delete the CS app, so we're allowed to delete its CDS
    #     CFE_ES_DeleteApp(AppID)
    #
    #     cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
    #
    #     # Send command under test
    #     cmd(f"<%= target_name %> CFE_ES_CMD_DELETE_CDS with CDS_NAME 'CS.CS_CDS'")
    #
    #     # Verify command count incremented
    #     wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    #
    #     # Wait for event
    #     event_expression = (
    #         "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
    #         "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 78 and " +
    #         "'Successfully removed \'cdsfile\' from CDS' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
    #         )
    #     wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_22_DeleteCDS(self):
        """
        Test the DeleteCDS command.
        """
        
        # First, stop the CS app, so we're allowed to delete its CDS
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> CFE_ES_CMD_STOP_APP with APPLICATION 'CS'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        wait(5)  # Wait for the CS app to finish exiting
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_DELETE_CDS with CDS_NAME 'CS.CS_CDS'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # FIXME: Command succeeds with correct message, but check fails.
        #    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 78 and " +
        #    "'Successfully removed \'CS.CS_CDS\' from CDS' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
        
        # Re-start the CS app, to restore the system state to as it was before this step
        cmd(f"<%= target_name %> CFE_ES_CMD_START_APP with APPLICATION 'CS', APP_ENTRY_POINT 'CS_AppMain', APP_FILE_NAME 'cs', STACK_SIZE 16384, EXCEPTION_ACTION 0, PRIORITY 65")
    
    
    def test_23_SendMemPoolStats(self):
        """
        Test the SendMemPoolStats command.
        """
        
        # Get and save SB HK mempool handle.  Needed for command.
        sb_mempool_handle = tlm("<%= target_name %> CFE_SB_HK MEM_POOL_HANDLE")
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_SEND_MEM_POOL_STATS with APPLICATION 'TO', POOL_HANDLE {sb_mempool_handle}")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        #    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 81 and " +
        #    f"'Successfully telemetered memory pool stats for {sb_mempool_handle}' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_24_DumpCDSRegistry(self):
        """
        Test the DumpCDSRegistry command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_DUMP_CDS_REGISTRY with DUMP_FILENAME 'dumpfile.txt'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # FIXME: Command succeeds with correct message, but check fails.
        #    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 83 and " +
        #    "'Successfully dumped CDS Registry to \'/ram/dumpfile.txt\'' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def test_25_ResetCounters(self):
        """
        Test the ResetCounters command.
        """
        
        # First, cause command error counter to increment.  Send cmd with invalid parameter.
        cmd(f"<%= target_name %> CFE_ES_CMD_DUMP_CDS_REGISTRY with DUMP_FILENAME 1")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_RESET_COUNTERS")
        
        # Verify counter are reset to zero
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER == 0", 100)
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_ERROR_COUNTER == 0", 100)
    
    
    def is_Sample_App_Running(self) -> bool:
        """
        This function determines if the Sample_App is running
        
        Returns:
            bool: 
                - True if Sample_App is running
                - False if Sample_App is notrunning
        """
        # save counters to dermine if Sample_App is running
        saved_cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        seq_count = tlm(f"<%= target_name %> CFE_ES_HK CCSDS_SEQUENCE")
        
        # Send QUERY_ONE command to test if Sample_app is running or not
        cmd(f"<%= target_name %> CFE_ES_CMD_QUERY_ONE with APPLICATION 'SAMPLE_APP'")
        
        # wait for a new packet
        wait(1)
        
        # If this check fails, stop the test, no telemetry packet was received within the timeout
        wait_check(f"<%= target_name %> CFE_ES_HK CCSDS_SEQUENCE > {seq_count}", 100)
        
        current_cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        if(current_cmd_count == (saved_cmd_count + 1)):
            # Sample_app is found to be running
            return True
        else:
            # Sample_app is not found to be running or the wait_check failed (no tlm received)
            return False
    
    
    def StopApp_test(self):
        """
        Test the StopApp command.
        Called from the StopApp_StartApp test
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")
        
        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_STOP_APP with APPLICATION 'SAMPLE_APP'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        wait(5) # wait for the application to stop
        
        #    DS: There is an issue with the cFS-integration-sandbox telemetry being dropped.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 7 and " +
        #    "'Stop Application SAMPLE_APP Initiated' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def StartApp_test(self):
        """
        Test the StartApp command.
        Called from the StopApp_StartApp test
        """
        
        cmd_count = tlm(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER")

        # Send command under test
        cmd(f"<%= target_name %> CFE_ES_CMD_START_APP with APPLICATION 'SAMPLE_APP', APP_ENTRY_POINT 'SAMPLE_APP_Main', APP_FILE_NAME 'sample_app', STACK_SIZE 16384, EXCEPTION_ACTION 0, PRIORITY 50")

        # Verify command count incremented
        wait_check(f"<%= target_name %> CFE_ES_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        wait(5) # wait for the application to start
        
        # FIXME: Command succeeds with correct message, but check fails.
        #    DS: This is because right after ES sends the started event, the sample app sends it's 
        #        init event, so the event you are checking against is the sample app message.
        #        See my comment about event messages in the test_01_NoOp function
        # Wait for event
        #event_expression = (
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME') == 'CFE_ES' and " +
        #    "tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID') == 6 and " +
        #    "'Started SAMPLE_APP from /cf/sample_app.so' in tlm('<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE')"
        #    )
        #wait_check_expression(event_expression, 10, 0.5, globals())
    
    
    def setup(self):
        """
        Test Group Setup
        - Runs when Group Setup button is pressed
        - Runs before all scripts when Group Start is pressed
        """
        global sample_app_needs_shutdown_at_end # lets python know we plan to change this global in this function
        
        # If the Sample_App is not running, start it, setting a var to stop it at the end of the test
        # this call here ensures that the system is in the state needed 
        if(not self.is_Sample_App_Running()):
            sample_app_needs_shutdown_at_end = True
            self.StartApp_test()
        
        # Ensure that ES events are enabled
        cmd("<%= target_name %> CFE_EVS_CMD_ENABLE_APP_EVENTS with APP_NAME 'CFE_ES'")
        wait(1)
        
        # Ensure that DEBUG and INFO events are enabled
        cmd("<%= target_name %> CFE_EVS_CMD_ENABLE_EVENT_TYPE with BIT_MASK DEBUG")
        cmd("<%= target_name %> CFE_EVS_CMD_ENABLE_EVENT_TYPE with BIT_MASK INFO")
        wait(1)
        

    def teardown(self):
        """
        Test Group Setup
        - Runs when Group Teardown button is pressed
        - Runs after all scripts when Group Start is pressed
        """
        
        # this call here ensures that the system is in the state it was in when it started 
        if(sample_app_needs_shutdown_at_end):
            self.StopApp_test()
        
