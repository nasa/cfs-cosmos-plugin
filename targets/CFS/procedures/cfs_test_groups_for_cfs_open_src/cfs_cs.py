from openc3.script.suite import Group
# Verify CS commands work properly.  Not testing error cases.

# Group class name should indicate what the scripts are testing
class cfs_test_group_cfs_cs(Group):
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
        
        Group.print("Testing CS aliveness on <%= target_name %>")
        
        wait_check_packet("<%= target_name %>", "CS_HK", 1, 100)
        
        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm("<%= target_name %> CS_HK COMMAND_COUNTER")
        
        # Send NOOP command, then check result to prove application is up and running
        cmd("<%= target_name %> CS_CMD_NOOP")
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # Send Reset Counters command, check resullt
        cmd("<%= target_name %> CS_CMD_RESET_COUNTERS")
        wait_check("<%= target_name %> CS_HK COMMAND_COUNTER == 0", 100)
    
    
    def test_01_NoOp(self):
        """
        Test the no-op command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_NOOP")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_02_OneShot(self):
        """
        Test the OneShot command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_ONE_SHOT with ADDRESS 0x00000000, SIZE 1, MAX_BYTES_PER_CYCLE 1")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Lastoneshotaddress == 0x00000000", 100)
        wait_check(f"<%= target_name %> CS_HK Lastoneshotsize == 1", 100)
        wait_check(f"<%= target_name %> CS_HK Lastoneshotmaxbytespercycle == 1", 100)
        wait_check(f"<%= target_name %> CS_HK Lastoneshotchecksum == 0", 100)
        # Recomputeinprogress does not stay FALSE long enough to show in packet.
        # Oneshotinprogress does not stay TRUE long enough to show in packet.
    

    def test_03_CancelOneShot(self):
        """
        Test the CancelOneShot command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_ONE_SHOT with ADDRESS 0x00000000, SIZE 1, MAX_BYTES_PER_CYCLE 1")
        cmd("<%= target_name %> CS_CMD_CANCEL_ONE_SHOT")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 2}", 100)
    

    def test_04_EnableAllCS(self):
        """
        Test the EnableAllCS command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_ENABLE_ALL_CS")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Checksumstate == 'ENABLED'", 100)
    

    def test_05_DisableAllCS(self):
        """
        Test the DisableAllCS command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_DISABLE_ALL_CS")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Checksumstate == 'DISABLED'", 100)
    

    def test_06_EnableCfeCore(self):
        """
        Test the EnableCfeCore command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_ENABLE_CFE_CORE")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Cfecorecsstate == 'ENABLED'", 100)
    

    def test_07_DisableCfeCore(self):
        """
        Test the DisableCfeCore command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_DISABLE_CFE_CORE")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Cfecorecsstate == 'DISABLED'", 100)


    def test_08_ReportBaselineCfeCore(self):
        """
        Test the ReportBaselineCfeCore command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_REPORT_BASELINE_CFE_CORE")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_09_RecomputeBaselineCfeCore(self):
        """
        Test the RecomputeBaselineCfeCore command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_RECOMPUTE_BASELINE_CFE_CORE")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        # Recomputeinprogress does not stay TRUE long enough to show in packet.
    

    def test_10_EnableOS(self):
        """
        Test the EnableOS command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_ENABLE_OS")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Oscsstate == 'ENABLED'", 100)
    

    def test_11_DisableOS(self):
        """
        Test the DisableOS command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_DISABLE_OS")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Oscsstate == 'DISABLED'", 100)
    

    def test_12_ReportBaselineOS(self):
        """
        Test the ReportBaselineOS command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_REPORT_BASELINE_OS")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_13_RecomputeBaselineOS(self):
        """
        Test the RecomputeBaselineOS command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_RECOMPUTE_BASELINE_OS")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        # Recomputeinprogress does not stay TRUE long enough to show in packet.


    def test_14_EnableEEPROM(self):
        """
        Test the EnableEEPROM command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_ENABLE_EEPROM")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Eepromcsstate == 'ENABLED'", 100)
    

    def test_15_DisableEEPROM(self):
        """
        Test the DisableEEPROM command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_DISABLE_EEPROM")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Eepromcsstate == 'DISABLED'", 100)
    

    def test_16_ReportBaselineEntryIDEeprom(self):
        """
        Test the ReportBaselineEntryIDEeprom command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_REPORT_BASELINE_EEPROM with EntryID 0")
        # FIXME: Entry ID invalid: 0
        #        Was not fixed by commenting out DisableEEPROM command.          <=======
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_17_RecomputeBaselineEntryIDEeprom(self):
        """
        Test the RecomputeBaselineEntryIDEeprom command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_RECOMPUTE_BASELINE_EEPROM with EntryID 0")
        # FIXME: Entry ID invalid: 0
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Recomputeinprogress == TRUE", 100) # FIXME: Does this stay true long enough to make it into the HK packet?


    def test_18_EnableEntryIDEepromCmd(self):
        """
        Test the EnableEntryIDEeprom command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_ENABLE_ENTRY_EEPROM with EntryID 0")
        # FIXME: Entry ID invalid: 0
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_18_DisableEntryIDEepromCmd(self):
        """
        Test the DisableEntryIDEeprom command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_DISABLE_ENTRY_EEPROM with EntryID 0")
        # FIXME: Entry ID invalid: 0
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_19_GetEntryIDEepromCmd(self):
        """
        Test the DisableEntryIDEeprom command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_GET_ENTRY_ID_EEPROM with Address 0x00000000")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_18_EnableMemory(self):
        """
        Test the EnableMemory command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_ENABLE_MEMORY")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Memorycsstate == 'ENABLED'", 100)
    

    def test_19_DisableMemory(self):
        """
        Test the DisableMemory command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_DISABLE_MEMORY")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Memorycsstate == 'DISABLED'", 100)
    

    def test_20_ReportBaselineEntryIDMemory(self):
        """
        Test the ReportBaselineEntryIDMemory command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_REPORT_BASELINE_MEMORY with EntryID 0")
        # FIXME: Entry ID invalid: 0
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_21_RecomputeBaselineMemory(self):
        """
        Test the RecomputeBaselineMemory command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_RECOMPUTE_BASELINE_MEMORY with EntryID 0")
        # FIXME: Entry ID invalid: 0
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Recomputeinprogress == TRUE", 100) # FIXME: Does this stay true long enough to make it into the HK packet?


    def test_22_EnableEntryIDMemory(self):
        """
        Test the EnableEntryIDMemory command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_ENABLE_ENTRY_MEMORY with EntryID 0")
        # FIXME: Entry ID invalid: 0
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_23_DisableEntryIDMemory(self):
        """
        Test the DisableEntryIDMemory command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_DISABLE_ENTRY_MEMORY with EntryID 0")
        # FIXME: Entry ID invalid: 0
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_24_GetEntryIDMemory(self):
        """
        Test the GetEntryIDMemory command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_GET_ENTRY_ID_MEMORY with Address 0x00000000")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_25_EnableTables(self):
        """
        Test the EnableTables command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_ENABLE_TABLES")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Tablescsstate == 'ENABLED'", 100)
    
 
    def test_26_DisableTables(self):
        """
        Test the DisableTables command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_DISABLE_TABLES")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Tablescsstate == 'DISABLED'", 100)
    

    def test_28_ReportBaselineTable(self):
        """
        Test the ReportBaselineTable command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_REPORT_BASELINE_TABLE with NAME 'MD.DWELL_TABLE4'")
        # FIXME: Table MD.DWELL_TABLE4 not found
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_29_RecomputeBaselineTable(self):
        """
        Test the RecomputeBaselineTable command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_RECOMPUTE_BASELINE_TABLE with NAME 'MD.DWELL_TABLE4'")
        # FIXME: Table MD.DWELL_TABLE4 not found
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Recomputeinprogress == TRUE", 100) # FIXME: Does this stay true long enough to make it into the HK packet?


    def test_30_EnableNameTable(self):
        """
        Test the EnableNameTable command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_ENABLE_NAME_TABLE with NAME 'MD.DWELL_TABLE4'")
        # FIXME: Table MD.DWELL_TABLE4 not found
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_31_DisableNameTable(self):
        """
        Test the DisableNameTable command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_DISABLE_NAME_TABLE with NAME 'MD.DWELL_TABLE4'")
        # FIXME: Table MD.DWELL_TABLE4 not found
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_32_DisableNameTable(self):
        """
        Test the DisableNameTable command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_DISABLE_NAME_TABLE with NAME 'MD.DWELL_TABLE4'")
        # FIXME: Table MD.DWELL_TABLE4 not found
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_33_EnableApps(self):
        """
        Test the EnableApps command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_ENABLE_APPS")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Appcsstate == 'ENABLED'", 100)
    

    def test_34_DisableApps(self):
        """
        Test the DisableApps command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_DISABLE_APPS")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Appcsstate == 'DISABLED'", 100)
    

    def test_35_ReportBaselineApp(self):
        """
        Test the ReportBaselineApp command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_REPORT_BASELINE_APP with NAME 'MD'")
        # FIXME: app MD not found
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_36_RecomputeBaselineApp(self):
        """
        Test the RecomputeBaselineApp command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_RECOMPUTE_BASELINE_APP with NAME 'MD'")
        # FIXME: app MD not found
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Recomputeinprogress == TRUE", 100) # FIXME: Does this stay true long enough to make it into the HK packet?


    def test_37_EnableNameApp(self):
        """
        Test the EnableNameApp command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_ENABLE_NAME_APP with NAME 'MD'")
        # FIXME: app MD not found
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Appcsstate == 'ENABLED'", 100)
    

    def test_38_DisableNameApp(self):
        """
        Test the DisableNameApp command.
        """
        
        cmd_count = tlm(f"<%= target_name %> CS_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> CS_CMD_DISABLE_NAME_APP with NAME 'MD'")
        # FIXME: app MD not found
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Verify any other telemetry changes
        wait_check(f"<%= target_name %> CS_HK Appcsstate == 'ENABLED'", 100)


    def test_39_ResetCounters(self):
        """
        Test the Reset Counters command.
        """

        # NOTE: Current initial version is simplified to only increment COMMAND_COUNTER and COMMAND_ERROR_COUNTER before reset.

        # Increment COMMAND_COUNTER by sending CreateDirectory command
        cmd("<%= target_name %> CS_CMD_NOOP")
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER > 0", 100)
        
        # Cause COMMAND_ERROR_COUNTER to increment,
        # by sending ReportBaselineApp cmd with invalid app name
        cmd("<%= target_name %> CS_CMD_REPORT_BASELINE_APP with NAME 'Nonexistent'")
        wait_check(f"<%= target_name %> CS_HK COMMAND_ERROR_COUNTER > 0", 100)

        # Send ResetCounters command
        cmd(f"<%= target_name %> CS_CMD_RESET_COUNTERS")
        
        # Verify counters are reset to zero
        wait_check(f"<%= target_name %> CS_HK COMMAND_COUNTER == 0", 100)
        wait_check(f"<%= target_name %> CS_HK COMMAND_ERROR_COUNTER == 0", 100)
        wait_check(f"<%= target_name %> CS_HK Eepromcserrcounter == 0", 100)
        wait_check(f"<%= target_name %> CS_HK Memorycserrcounter == 0", 100)
        wait_check(f"<%= target_name %> CS_HK Appcserrcounter == 0", 100)
        wait_check(f"<%= target_name %> CS_HK Tablescserrcounter == 0", 100)
        wait_check(f"<%= target_name %> CS_HK Cfecorecserrcounter == 0", 100)
        wait_check(f"<%= target_name %> CS_HK Oscserrcounter == 0", 100)
        wait_check(f"<%= target_name %> CS_HK Passcounter == 0", 100)


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
