# cFS Globals

# -------------------------------------------------------------------------------------------------
# Defines the format of our cFS target names
# -------------------------------------------------------------------------------------------------
def cfs_target_name_from_cpu_num(cpu_num)
  return "CFS-#{cpu_num}"
end

# -------------------------------------------------------------------------------------------------
# Gets the CPU number of the provided cFS target name
# -------------------------------------------------------------------------------------------------
def cfs_cpu_num_from_target_name(target_name)
  return Integer(target_name.delete("CFS\-") || '')
rescue ArgumentError
    nil
end

# -------------------------------------------------------------------------------------------------
# Number of CPU instances of the FSW that can be interfaced with
# -------------------------------------------------------------------------------------------------
$cfs_total_valid_cpus = 1

# -------------------------------------------------------------------------------------------------
# Get the cmd port based on the cpu_num
#     Context: CI_LAB has a base port number of 1234 but it increments it for CPUs past 1
# -------------------------------------------------------------------------------------------------
def cfs_get_port_num_cmd(cpu_num_input)
  cpu_num = cpu_num_or_nil(cpu_num_input)
  port_num = 1234
  port_num_str = String.new
  if (cpu_num == nil)
      port_num_str << "cfs_get_port_num_cmd error: could not convert #{cpu_num_input} to an integer"
  elsif ((cpu_num < 1) && (cpu_num > $cfs_total_valid_cpus))
      port_num_str << "cfs_get_port_num_cmd error: should be between 1 and #{$cfs_total_valid_cpus} (inclusive). instead got: #{cpu_num}."
  else
      port_num = port_num + (cpu_num - 1)
      port_num_str << sprintf("%d", port_num)
  end
  return port_num_str
end

# -------------------------------------------------------------------------------------------------
# Port number of the TO_LAB output port
# -------------------------------------------------------------------------------------------------
$cfs_tlm_port = 1235

# -------------------------------------------------------------------------------------------------
# Get the tlm port of the FSW
# -------------------------------------------------------------------------------------------------
def cfs_get_port_num_tlm
  return $cfs_tlm_port
end

# -------------------------------------------------------------------------------------------------
# EDS Enabled / Disabled Flag
# Must be boolean (`true` or `false`)
# -------------------------------------------------------------------------------------------------
$cfs_globals_eds_enabled = false

# Set the related global variable, based on the input (called from plugin.txt)
# The user should have entered either "true" or "false"
def cfs_globals_set_eds_enabled(eds_enabled_input_string)
  if eds_enabled_input_string == "true"
    $cfs_globals_eds_enabled = true
  else
    $cfs_globals_eds_enabled = false
  end
end


# -------------------------------------------------------------------------------------------------
# FSW Target Memory Size
# Must be `32` or `64`
# -------------------------------------------------------------------------------------------------
$cfs_globals_mem_size = 32

# Set the related global variable, based on the input (called from plugin.txt)
# The user should have entered either "32" or "64"
def cfs_globals_set_mem_size(mem_size_input_string)
  if mem_size_input_string == "64"
    $cfs_globals_mem_size = 64
  else
    $cfs_globals_mem_size = 32
  end
end


# -------------------------------------------------------------------------------------------------
# FSW Target's Processor Endianness
# Must be "LITTLE_ENDIAN" or "BIG_ENDIAN"
# -------------------------------------------------------------------------------------------------
$cfs_globals_endianness = "LITTLE_ENDIAN"

# Set the related global variable, based on the input (called from plugin.txt)
# The user should have entered either "true" or "false"
def cfs_globals_set_endianness(endianness_input_string)
  if endianness_input_string == "BIG_ENDIAN"
    $cfs_globals_endianness = "BIG_ENDIAN"
  else
    $cfs_globals_endianness = "LITTLE_ENDIAN"
  end
end
