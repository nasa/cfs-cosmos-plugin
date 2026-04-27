# 1. Read file and chop off the 64-byte cFE File Header
raw = File.binread(get_target_file('CFS-1/lib/ta_dump.bin').path)[64..-1]

data = { 
  'CORES_AVAILABLE'  => raw[0,2].unpack1('v'), 
  'OSAL_CORES_MAX' => raw[2,2].unpack1('v'), 
  'MAX_AFFINITY_BITS'=> raw[4,2].unpack1('v') 
}

type_map = {0 => 'OS_DEFAULT', 1 => 'MASK', 2 => 'ADDED'}
stat_map = {0 => 'UNKNOWN', 1 => 'OK', 2 => 'ERROR'}

# 2. Divide by the TRUE struct size (48 bytes)
task_bytes_only = raw.length - 8
num_tasks_in_file = task_bytes_only / 48

puts "Found #{num_tasks_in_file} tasks (48 bytes each) in this dump!"

# 3. The Magic Fix: Z20 (String) + V6 (6 Ints) + x4 (Skip 4 bytes padding)
raw[8..-1].unpack("Z20V6x4" * num_tasks_in_file).each_slice(7).with_index do |t, i| 
  break if i >= 64
  
  type_str = type_map[t[1]] || 'OS_DEFAULT'
  stat_str = stat_map[t[2]] || 'UNKNOWN'

  data.merge!("TASK_NAME_#{i}"=>t[0].strip, 
              "TA_TYPE_#{i}"=>type_str, 
              "TA_STATUS_#{i}"=>stat_str, 
              "TA_MASK1_#{i}"=>t[3].to_i, 
              "TA_MASK2_#{i}"=>t[4].to_i, 
              "TA_FROM_OS1_#{i}"=>t[5].to_i, 
              "TA_FROM_OS2_#{i}"=>t[6].to_i) 
end

# 4. Inject!
inject_tlm('CFS-1', 'TA_AFFINITY_FILE', data)
