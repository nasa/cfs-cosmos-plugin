from openc3.script.suite import Group
# Verify DS commands work properly.  Not testing error cases.

# Group class name should indicate what the scripts are testing
class cfs_test_group_cfs_ds(Group):
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
        
        Group.print("Testing DS aliveness on <%= target_name %>")
        
        wait_check_packet("<%= target_name %>", "DS_HK", 1, 100)
        
        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm("<%= target_name %> DS_HK COMMAND_COUNTER")
        
        # Send NOOP command, then check result to prove application is up and running
        cmd("<%= target_name %> DS_CMD_NOOP")
        wait_check(f"<%= target_name %> DS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # Send Reset Counters command, check resullt
        cmd("<%= target_name %> DS_CMD_RESET_COUNTERS")
        wait_check("<%= target_name %> DS_HK COMMAND_COUNTER == 0", 100)
    
    
    def test_01_NoOp(self):
        """
        Test the no-op command.
        """
        
        cmd_count = tlm(f"<%= target_name %> DS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> DS_CMD_NOOP")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> DS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)


    def test_02_SetAppState(self):
        """
        Test the SetAppState command.
        """
        
        cmd_count = tlm(f"<%= target_name %> DS_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> DS_CMD_SET_APP_STATE with ENABLE_STATE ENABLE'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> DS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify other telemetry changed as expected
        wait_check(f"<%= target_name %> DS_HK APP_ENABLE_STATE == 1", 100)


    def test_03_SetFilterFile(self):
        """
        Test the SetFilterFile command.
        """
        
        cmd_count = tlm(f"<%= target_name %> DS_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> DS_CMD_SET_FILTER_FILE with MESSAGE_ID 0x1A00, FILTER_PARAMS_IDX 0, FILE_TABLE_IDX 0'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> DS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_04_SetFilterType(self):
        """
        Test the SetFilterType command.
        """
        
        cmd_count = tlm(f"<%= target_name %> DS_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> DS_CMD_SET_FILTER_TYPE with MESSAGE_ID 0x1A00, FILTER_PARAMS_IDX 0, FILTER_TYPE BY_COUNT'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> DS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_05_SetFilterParms(self):
        """
        Test the SetFilterParms command.
        """

        # NOTE: Source code abbreviates as "parms", while COSMOS file abbreviates as "params".
        
        cmd_count = tlm(f"<%= target_name %> DS_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> DS_CMD_SET_FILTER_PARAMS with MESSAGE_ID 0x1A00, FILTER_PARAMS_IDX 0, ALGORITHM_N 0, ALGORITHM_X 0, ALGORITHM_O 0'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> DS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_06_SetDestType(self):
        """
        Test the SetDestType command.
        """
        
        cmd_count = tlm(f"<%= target_name %> DS_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> DS_CMD_SET_DEST_TYPE with FILE_TABLE_IDX 0, FILE_NAME_TYPE 0'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> DS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)







    # FIXME: Next: DS_CMD_SET_DEST_STATE
    



# DS_CMD_SET_DEST_PATH
# DS_CMD_SET_DEST_BASE
# DS_CMD_SET_DEST_EXT
# DS_CMD_SET_DEST_SIZE
# DS_CMD_SET_DEST_AGE
# DS_CMD_SET_DEST_COUNT
# DS_CMD_CLOSE_FILE
# DS_CMD_GET_FILE_INFO
# DS_CMD_ADD_MID
# DS_CMD_CLOSE_ALL
# DS_CMD_REMOVE_MID


    # FIXME: Update this function for DS
    #
    def test_X_ResetCounters(self):
        """
        Test the ResetCounters command.
        """

        # Increment COMMAND_COUNTER and CHILD_CMD_COUNTER by sending CreateDirectory command
        cmd_count = tlm(f"<%= target_name %> DS_HK COMMAND_COUNTER")
        cmd("<%= target_name %> DS_CMD_CREATE_DIRECTORY with DIRECTORY '/cf/new-directory'")
        wait_check(f"<%= target_name %> DS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        wait_check(f"<%= target_name %> DS_HK COMMAND_COUNTER > 0", 100)
        wait_check(f"<%= target_name %> DS_HK CHILD_CMD_COUNTER > 0", 100)

        # Delete the created directory, for cleanup
        cmd_count = tlm(f"<%= target_name %> DS_HK COMMAND_COUNTER")
        cmd("<%= target_name %> DS_CMD_DELETE_DIRECTORY with DIRECTORY '/cf/new-directory'")
        wait_check(f"<%= target_name %> DS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # Cause COMMAND_ERROR_COUNTER and CHILD_CMD_ERR_COUNTER to increment,
        # by sending a DeleteDirectory command with a non-existant directory. 
        cmd("<%= target_name %> DS_CMD_DELETE_DIRECTORY with DIRECTORY '/ram/non-existant'")

        wait_check(f"<%= target_name %> DS_HK COMMAND_ERROR_COUNTER > 0", 100)
        wait_check(f"<%= target_name %> DS_HK CHILD_CMD_ERR_COUNTER > 0", 100)

        # Cause CHILD_CMD_WARN_COUNTER to increment,
        # by sending a DirListPkt command with an extremely-long directory/file path.
        cmd("<%= target_name %> DS_CMD_GET_DIR_LIST_PKT with DIRECTORY '/ram/path-too-long-path-too-long-path-too-long-path-too-long', DIR_LIST_OFFSET 0, GET_SIZE_TIME_MODE FALSE")

        wait_check(f"<%= target_name %> DS_HK CHILD_CMD_WARN_COUNTER > 0", 100)

        # Send ResetCounters command
        cmd(f"<%= target_name %> DS_CMD_RESET_COUNTERS")
        
        # Verify counters are reset to zero
        wait_check(f"<%= target_name %> DS_HK COMMAND_COUNTER == 0", 100)
        wait_check(f"<%= target_name %> DS_HK COMMAND_ERROR_COUNTER == 0", 100)
        wait_check(f"<%= target_name %> DS_HK CHILD_CMD_COUNTER == 0", 100)
        wait_check(f"<%= target_name %> DS_HK CHILD_CMD_ERR_COUNTER == 0", 100)
        wait_check(f"<%= target_name %> DS_HK CHILD_CMD_WARN_COUNTER == 0", 100)


    def setup(self):
        """
        Test Group Setup
        - Runs when Group Setup button is pressed
        - Runs before all scripts when Group Start is pressed
        """
        # Wait for a new housekeeping packet, to ensure we're using its latest status info
        wait_check_packet(f"<%= target_name %>", "DS_HK", 1, 100)

        # Ensure that DS events are enabled
        cmd("<%= target_name %> CFE_EVS_CMD_ENABLE_APP_EVENTS with APP_NAME 'DS'")
        wait(1)
        
        # Ensure that DEBUG and INFO events are enabled
        cmd("<%= target_name %> CFE_EVS_CMD_ENABLE_EVENT_TYPE with BIT_MASK DEBUG")
        cmd("<%= target_name %> CFE_EVS_CMD_ENABLE_EVENT_TYPE with BIT_MASK INFO")
        wait(1)
        pass


    def teardown(self):
        """
        Test Group Setup
        - Runs when Group Teardown button is pressed
        - Runs after all scripts when Group Start is pressed
        """
        pass