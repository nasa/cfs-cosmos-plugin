#------------------------------------------------------------------------------
# Class to maintain FSW Message Info
#------------------------------------------------------------------------------
class FswMsgInfo
    attr_accessor :fsw_msg_base_stream_id
    attr_accessor :fsw_msg_packet_names
    def initialize(params)
        @fsw_msg_base_stream_id = params[:base_stream_id]
        @fsw_msg_packet_names = params[:packet_names]
    end
end

#------------------------------------------------------------------------------
# cFS Command / Telemetry Message ID Reference Names
# mapped to Message ID values (per CPU) and pkt names
#------------------------------------------------------------------------------
$CFS_CMD_TLM_LIST = {
    # -------------------------------------------------------------------------
    # Commands
    # -------------------------------------------------------------------------
    "CFE_EVS_CMD" => FswMsgInfo.new(
        base_stream_id: 0x1801,
        packet_names: [
            "CFE_EVS_CMD_NOOP",
            "CFE_EVS_CMD_RESET_COUNTERS",
            "CFE_EVS_CMD_ENABLE_EVENT_TYPE",
            "CFE_EVS_CMD_DISABLE_EVENT_TYPE",
            "CFE_EVS_CMD_SET_EVENT_FORMAT_MODE",
            "CFE_EVS_CMD_ENABLE_APP_EVENT_TYPE",
            "CFE_EVS_CMD_DISABLE_APP_EVENT_TYPE",
            "CFE_EVS_CMD_ENABLE_APP_EVENTS",
            "CFE_EVS_CMD_DISABLE_APP_EVENTS",
            "CFE_EVS_CMD_RESET_APP_COUNTER",
            "CFE_EVS_CMD_SET_FILTER",
            "CFE_EVS_CMD_ENABLE_PORTS",
            "CFE_EVS_CMD_DISABLE_PORTS",
            "CFE_EVS_CMD_RESET_FILTER",
            "CFE_EVS_CMD_RESET_ALL_FILTERS",
            "CFE_EVS_CMD_ADD_EVENT_FILTER",
            "CFE_EVS_CMD_DELETE_EVENT_FILTER",
            "CFE_EVS_CMD_WRITE_APP_DATA_FILE",
            "CFE_EVS_CMD_WRITE_LOG_DATA_FILE",
            "CFE_EVS_CMD_SET_LOG_MODE",
            "CFE_EVS_CMD_CLEAR_LOG",
        ]
    ),
    "CFE_SB_CMD" => FswMsgInfo.new(
        base_stream_id: 0x1803,
        packet_names: [
            "CFE_SB_CMD_NOOP",
            "CFE_SB_CMD_RESET_COUNTERS",
            "CFE_SB_CMD_SEND_SB_STATS",
            "CFE_SB_CMD_WRITE_ROUTING_INFO",
            "CFE_SB_CMD_ENABLE_ROUTE",
            "CFE_SB_CMD_DISABLE_ROUTE",
            "CFE_SB_CMD_WRITE_PIPE_INFO",
            "CFE_SB_CMD_WRITE_MAP_INFO",
        ]
    ),
    "CFE_TBL_CMD" => FswMsgInfo.new(
        base_stream_id: 0x1804,
        packet_names: [
                "CFE_TBL_CMD_NOOP",
                "CFE_TBL_CMD_RESET_COUNTERS",
                "CFE_TBL_CMD_LOAD",
                "CFE_TBL_CMD_DUMP",
                "CFE_TBL_CMD_VALIDATE",
                "CFE_TBL_CMD_ACTIVATE",
                "CFE_TBL_CMD_DUMP_REGISTRY",
                "CFE_TBL_CMD_SEND_REGISTRY",
                "CFE_TBL_CMD_DELETE_CDS",
                "CFE_TBL_CMD_ABORT_LOAD",
        ]
    ),
    "CFE_TIME_CMD" => FswMsgInfo.new(
        base_stream_id: 0x1805,
        packet_names: [
            "CFE_TIME_CMD_NOOP",
            "CFE_TIME_CMD_RESET_COUNTERS",
            "CFE_TIME_CMD_SEND_DIAGNOSTIC",
            "CFE_TIME_CMD_SET_SOURCE",
            "CFE_TIME_CMD_SET_STATE",
            "CFE_TIME_CMD_ADD_DELAY",
            "CFE_TIME_CMD_SUB_DELAY",
            "CFE_TIME_CMD_SET_TIME",
            "CFE_TIME_CMD_SET_MET",
            "CFE_TIME_CMD_SET_STCF",
            "CFE_TIME_CMD_SET_LEAP_SECONDS",
            "CFE_TIME_CMD_ADD_ADJUST",
            "CFE_TIME_CMD_SUB_ADJUST",
            "CFE_TIME_CMD_ADD_ONE_HZ_ADJUSTMENT",
            "CFE_TIME_CMD_SUB_ONE_HZ_ADJUSTMENT",
            "CFE_TIME_CMD_SET_SIGNAL",
        ]
    ),
    "CFE_ES_CMD" => FswMsgInfo.new(
            base_stream_id: 0x1806,
            packet_names: [
                "CFE_ES_CMD_NOOP",
                "CFE_ES_CMD_RESET_COUNTERS",
                "CFE_ES_CMD_RESTART",
                "CFE_ES_CMD_START_APP",
                "CFE_ES_CMD_STOP_APP",
                "CFE_ES_CMD_RESTART_APP",
                "CFE_ES_CMD_RELOAD_APP",
                "CFE_ES_CMD_QUERY_ONE",
                "CFE_ES_CMD_QUERY_ALL",
                "CFE_ES_CMD_CLEAR_SYS_LOG",
                "CFE_ES_CMD_WRITE_SYS_LOG",
                "CFE_ES_CMD_CLEAR_ER_LOG",
                "CFE_ES_CMD_WRITE_ER_LOG",
                "CFE_ES_CMD_START_PERF_DATA",
                "CFE_ES_CMD_STOP_PERF_DATA",
                "CFE_ES_CMD_SET_PERF_FILTER_MASK",
                "CFE_ES_CMD_SET_PERF_TRIGGER_MASK",
                "CFE_ES_CMD_OVER_WRITE_SYS_LOG",
                "CFE_ES_CMD_RESET_PR_COUNT",
                "CFE_ES_CMD_SET_MAX_PR_COUNT",
                "CFE_ES_CMD_DELETE_CDS",
                "CFE_ES_CMD_SEND_MEM_POOL_STATS",
                "CFE_ES_CMD_DUMP_CDS_REGISTRY",
                "CFE_ES_CMD_QUERY_ALL_TASKS",
            ]
        ),
    "CFE_SB_SUB_RPT_CTRL" => FswMsgInfo.new(
        base_stream_id: 0x180E,
        packet_names: [
            "CFE_SB_SUB_RPT_CTRL_ENABLE_SUB_REPORTING",
            "CFE_SB_SUB_RPT_CTRL_DISABLE_SUB_REPORTING",
            "CFE_SB_SUB_RPT_CTRL_SEND_PREV_SUBS",
        ]
    ),
    "TO_LAB_CMD" => FswMsgInfo.new(
        base_stream_id: 0x1880,
        packet_names: [
            "TO_LAB_CMD_NOOP",
            "TO_LAB_CMD_RESET_COUNTERS",
            "TO_LAB_CMD_ADD_PACKET",
            "TO_LAB_CMD_SEND_DATA_TYPES",
            "TO_LAB_CMD_REMOVE_PACKET",
            "TO_LAB_CMD_REMOVE_ALL",
            "TO_LAB_CMD_ENABLE_OUTPUT",
        ]
    ),
    "CI_LAB_CMD" => FswMsgInfo.new(
        base_stream_id: 0x1884,
        packet_names: [
            "CI_LAB_CMD_NOOP",
            "CI_LAB_CMD_RESET_COUNTERS",
        ]
    ),

    # -------------------------------------------------------------------------
    # Telemetry
    # -------------------------------------------------------------------------
    "CFE_ES_HK" => FswMsgInfo.new(
        base_stream_id: 0x0800,
        packet_names: [
            "CFE_ES_HK",
        ]
    ),
    "CFE_EVS_HK" => FswMsgInfo.new(
        base_stream_id: 0x0801,
        packet_names: [
            "CFE_EVS_HK",
        ]
    ),
    "CFE_TESTCASE_HK" => FswMsgInfo.new(
        base_stream_id: 0x0802,
        packet_names: [
            "CFE_TESTCASE_HK",
        ]
    ),
    "CFE_SB_HK" => FswMsgInfo.new(
        base_stream_id: 0x0803,
        packet_names: [
            "CFE_SB_HK",
        ]
    ),
    "CFE_TBL_HK" => FswMsgInfo.new(
        base_stream_id: 0x0804,
        packet_names: [
            "CFE_TBL_HK",
        ]
    ),
    "CFE_TIME_HK" => FswMsgInfo.new(
        base_stream_id: 0x0805,
        packet_names: [
            "CFE_TIME_HK",
        ]
    ),
    "CFE_TIME_DIAG" => FswMsgInfo.new(
        base_stream_id: 0x0806,
        packet_names: [
            "CFE_TIME_DIAG",
        ]
    ),
    "CFE_EVS_LONG_EVENT_MSG" => FswMsgInfo.new(
        base_stream_id: 0x0808,
        packet_names: [
            "CFE_EVS_LONG_EVENT_MSG",
        ]
    ),
    "CFE_EVS_SHORT_EVENT_MSG" => FswMsgInfo.new(
        base_stream_id: 0x0809,
        packet_names: [
            "CFE_EVS_SHORT_EVENT_MSG",
        ]
    ),
    "CFE_SB_STATS" => FswMsgInfo.new(
        base_stream_id: 0x080A,
        packet_names: [
            "CFE_SB_STATS",
        ]
    ),
    "CFE_ES_APP" => FswMsgInfo.new(
        base_stream_id: 0x080B,
        packet_names: [
            "CFE_ES_APP",
        ]
    ),
    "CFE_TBL_REG" => FswMsgInfo.new(
        base_stream_id: 0x080C,
        packet_names: [
            "CFE_TBL_REG",
        ]
    ),
    "CFE_SB_ALLSUBS" => FswMsgInfo.new(
        base_stream_id: 0x080D,
        packet_names: [
            "CFE_SB_ALLSUBS",
        ]
    ),
    "CFE_SB_ONESUB" => FswMsgInfo.new(
        base_stream_id: 0x080E,
        packet_names: [
            "CFE_SB_ONESUB",
        ]
    ),
    "CFE_ES_MEMSTATS" => FswMsgInfo.new(
        base_stream_id: 0x0810,
        packet_names: [
            "CFE_ES_MEMSTATS",
        ]
    ),
    "TO_LAB_HK" => FswMsgInfo.new(
        base_stream_id: 0x0880,
        packet_names: [
            "TO_LAB_HK",
        ]
    ),
    "CI_LAB_HK" => FswMsgInfo.new(
        base_stream_id: 0x0884,
        packet_names: [
            "CI_LAB_HK",
        ]
    ),
}


#------------------------------------------------------------------------------
# Convert cpu_num string to an integer (or nil)
#------------------------------------------------------------------------------
def cpu_num_or_nil(string)
    Integer(string || '')
rescue ArgumentError
    nil
end

#------------------------------------------------------------------------------
# Translate cFS packet name to a $CFS_CMD_TLM_LIST key name
# The provided pkt_name should be in the $CFS_CMD_TLM_LIST (above)
#------------------------------------------------------------------------------
def get_cfs_cmd_tlm_list_key_from_pkt_name(pkt_name)
    cfs_msg_id_key_name = ""
    $CFS_CMD_TLM_LIST.each do |pkt_list_key, pkt_info|
        if pkt_info.fsw_msg_packet_names.include? pkt_name
            cfs_msg_id_key_name = pkt_list_key
        end
    end
    return cfs_msg_id_key_name
end

#------------------------------------------------------------------------------
# Given the 2-byte stream id, fill in the cpu number and return the result
#
# 1. stream_id_base
#    - base stream id (without 3-bit cpu number set)
#    - should have the mask 0xF8FF
# 2. cpu_num
#    - must be between 0 and 7 (inclusively)
#    - if a number outside this range is provided,
#      the input stream_id is returned (unmodified)
#
# Example:
#  - `sprintf("0x%04X", get_cfs_msg_id_from_base(0x1801, 0)` should return "0x1801"
#  - `sprintf("0x%04X", get_cfs_msg_id_from_base(0x1801, 1)` should return "0x1901"
#  - `sprintf("0x%04X", get_cfs_msg_id_from_base(0x1801, 7)` should return "0x1F01"
#------------------------------------------------------------------------------
def get_cfs_msg_id_from_base(stream_id_base, cpu_num)
    # The cpu num is a 3-bit field, so the max value is b'111' (7)
    cpu_num_min = 0
    cpu_num_max = 7
    # Set the CPU Number bit field
    if ((cpu_num >= cpu_num_min) && (cpu_num <= cpu_num_max))
        stream_id = stream_id_base
        stream_id = stream_id & 0xF8FF # clear the 3-bit cpu-num field
        stream_id = stream_id | (cpu_num << 8)
    else
        # On cpu_num range error, return the base by default
        stream_id = stream_id_base
    end
    return stream_id
end


#------------------------------------------------------------------------------
# Embedded Ruby Utility to output a Message ID based on the following:
# 1. msg_id_name
#    - must be a key from the $CFS_CMD_TLM_LIST hash, above
# 2. cpu_num
#    - must be '1' or '2'
#------------------------------------------------------------------------------
def get_cfs_pkt_msg_id(pkt_name, cpu_num_input)
    pkt_list_key = get_cfs_cmd_tlm_list_key_from_pkt_name(pkt_name)
    cpu_num = cpu_num_or_nil(cpu_num_input)
    msg_id = String.new
    if !$CFS_CMD_TLM_LIST.key?(pkt_list_key)
        msg_id << "pkt_name error: #{pkt_name} not recognized"
    elsif (cpu_num == nil)
        msg_id << "cpu_num_input error: could not convert #{cpu_num_input} to an integer"
    elsif ((cpu_num < 1) && (cpu_num > 2))
        msg_id << "cpu_num_input error: should be 1 or 2. instead got: #{cpu_num}."
    else
        # Set all cpu numbers to be 1 to get default msgids
        cpu_num = 1

        msg_id_with_cpu_num = get_cfs_msg_id_from_base(
            $CFS_CMD_TLM_LIST[pkt_list_key].fsw_msg_base_stream_id,
            cpu_num-1)
        msg_id << sprintf("0x%04X", msg_id_with_cpu_num)
    end
    return msg_id
end

#------------------------------------------------------------------------------
# Tests for definitions in this file
#------------------------------------------------------------------------------
def cfs_cmd_tlm_list_test
    raise "TEST_FAIL" unless (get_cfs_pkt_msg_id("CFE_TBL_CMD", "1") == "0x1804")
    raise "TEST_FAIL" unless (get_cfs_pkt_msg_id("CFE_TBL_CMD", "2") == "0x1904")
end

# Uncomment to run tests
# cfs_cmd_tlm_list_test()
