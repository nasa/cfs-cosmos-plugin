from openc3.script.suite import Group
# Verify FM commands work properly.  Not testing error cases.

# Group class name should indicate what the scripts are testing
class cfs_test_group_cfs_fm(Group):
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
        
        Group.print("Testing FM aliveness on <%= target_name %>")
        
        wait_check_packet("<%= target_name %>", "FM_HK", 1, 100)
        
        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm("<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # Send NOOP command, then check result to prove application is up and running
        cmd("<%= target_name %> FM_CMD_NOOP")
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # Send Reset Counters command, check resullt
        cmd("<%= target_name %> FM_CMD_RESET_COUNTERS")
        wait_check("<%= target_name %> FM_HK COMMAND_COUNTER == 0", 100)
    
    
    def test_01_NoOp(self):
        """
        Test the no-op command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> FM_CMD_NOOP")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)


    def test_01_CopyFile(self):
        """
        Test the CopyFile command.
        """
        
        # First, upload the file to be copied
        # FIXME: How?

        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # FIXME: Needs to refer to SC filepaths, like "/ram/source.txt".  How do we upload files to there?
        #cmd("<%= target_name %> FM_CMD_COPY_FILE with OVERWRITE OVERWRITE, SOURCE '<%= target_name %>/procedures/cfs_test_groups_for_cfs_open_src/etc/source.txt', TARGET '<%= target_name %>/procedures/cfs_test_groups_for_cfs_open_src/etc/target.txt'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    
    
    def test_02_MoveFile(self):
        """
        Test the MoveFile command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> FM_CMD_MOVE_FILE with OVERWRITE OVERWRITE, SOURCE 'source.txt', TARGET 'target.txt'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_03_RenameFile(self):
        """
        Test the RenameFile command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> FM_CMD_RENAME_FILE with SOURCE 'source.txt', TARGET 'target.txt'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_04_DeleteFile(self):
        """
        Test the DeleteFile command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> FM_CMD_DELETE_FILE with FILENAME 'filename.txt'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_05_DeleteAllFiles(self):
        """
        Test the DeleteAllFiles command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> FM_CMD_DELETE_ALL_FILES with DIRECTORY '/ram/delete-these'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_06_DecompressFile(self):
        """
        Test the DecompressFile command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> FM_CMD_DECOMPRESS_FILE with SOURCE 'source.txt', TARGET 'target.txt'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_07_ConcatFiles(self):
        """
        Test the ConcatFiles command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> FM_CMD_CONCAT_FILES with SOURCE1 'source1.txt', SOURCE2 'source2.txt', TARGET 'target.txt'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_07_GetFileInfo(self):
        """
        Test the GetFileInfo command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> FM_CMD_GET_FILE_INFO with FILENAME 'file.txt', FILE_CRC NONE")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_08_GetOpenFiles(self):
        """
        Test the GetOpenFiles command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> FM_CMD_GET_OPEN_FILES")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)


    def test_09_CreateDirectory(self):
        """
        Test the CreateDirectory command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> FM_CMD_CREATE_DIRECTORY with DIRECTORY '/ram/new-directory'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)


    def test_10_DeleteDirectory(self):
        """
        Test the DeleteDirectory command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> FM_CMD_DELETE_DIRECTORY with DIRECTORY '/ram/delete-this'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)


    def test_11_GetDirListFile(self):
        """
        Test the GetDirListFile command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> FM_CMD_GET_DIR_LIST_FILE with DIRECTORY '/ram/directory', FILENAME 'filename.txt', GET_SIZE_TIME_MODE FALSE")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_12_GetDirListPkt(self):
        """
        Test the GetDirListPkt command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # FIXME: Does this need SPARE1/2/3?
        cmd("<%= target_name %> FM_CMD_GET_DIR_LIST_PKT with DIRECTORY '/ram/directory', DIR_LIST_OFFSET 0, GET_SIZE_TIME_MODE FALSE")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_13_MonitorFilesystemSpace(self):
        """
        Test the MonitorFilesystemSpace command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> FM_CMD_MONITOR_FILESYSTEM_SPACE")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)


    def test_14_SetTableState(self):
        """
        Test the SetTableState command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> FM_CMD_SET_TABLE_STATE with TABLE_ENTRY_INDEX 0, TABLE_ENTRY_STATE DISABLED")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)


    def test_14_SetPermissions(self):
        """
        Test the SetPermissions command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> FM_CMD_SET_PERMISSIONS with FILENAME 'filename.txt', MODE 777")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)


    def test_15_ResetCounters(self):
        """
        Test the ResetCounters command.
        """

        # These should already be incremented from earlier tests.
        wait_check(f"<%= target_name %> CFE_TIME_HK COMMAND_COUNTER > 0", 100)
        wait_check(f"<%= target_name %> CFE_TIME_HK CHILD_CMD_COUNTER > 0", 100)
        
        # Cause COMMAND_ERROR_COUNTER and CHILD_CMD_ERR_COUNTER to increment,
        # by sending a DeleteDirectory command with a non-existant directory. 
        cmd("<%= target_name %> FM_CMD_DELETE_DIRECTORY with DIRECTORY '/ram/non-existant'")

        wait_check(f"<%= target_name %> CFE_TIME_HK COMMAND_ERROR_COUNTER > 0", 100)
        wait_check(f"<%= target_name %> CFE_TIME_HK CHILD_CMD_ERR_COUNTER > 0", 100)

        # Cause CHILD_CMD_WARN_COUNTER to increment,
        # by sending a DirListPkt command with an extremely-long directory/file path.
        # FIXME: Does this need SPARE1/2/3?
        cmd("<%= target_name %> FM_CMD_GET_DIR_LIST_PKT with DIRECTORY '/ram/path-too-long-path-too-long-path-too-long-path-too-long-path-too-long-path-too-long-path-too-long-path-too-long-path-too-long-path-too-long', DIR_LIST_OFFSET 0, GET_SIZE_TIME_MODE FALSE")

        wait_check(f"<%= target_name %> CFE_TIME_HK CHILD_CMD_WARN_COUNTER > 0", 100)

        # Send ResetCounters command
        cmd(f"<%= target_name %> CFE_TIME_CMD_RESET_COUNTERS")
        
        # Verify counters are reset to zero
        wait_check(f"<%= target_name %> CFE_TIME_HK COMMAND_COUNTER == 0", 100)
        wait_check(f"<%= target_name %> CFE_TIME_HK COMMAND_ERROR_COUNTER == 0", 100)
        wait_check(f"<%= target_name %> CFE_TIME_HK CHILD_CMD_COUNTER == 0", 100)
        wait_check(f"<%= target_name %> CFE_TIME_HK CHILD_CMD_ERR_COUNTER == 0", 100)
        wait_check(f"<%= target_name %> CFE_TIME_HK CHILD_CMD_WARN_COUNTER == 0", 100)


    def setup(self):
        """
        Test Group Setup
        - Runs when Group Setup button is pressed
        - Runs before all scripts when Group Start is pressed
        """
        # Wait for a new housekeeping packet, to ensure we're using its latest status info
        wait_check_packet(f"<%= target_name %>", "FM_HK", 1, 100)

        # Ensure that FM events are enabled
        cmd("<%= target_name %> CFE_EVS_CMD_ENABLE_APP_EVENTS with APP_NAME 'FM'")
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