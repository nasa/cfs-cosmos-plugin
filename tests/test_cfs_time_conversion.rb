# Run with the openc3 and minitest gems installed:
# ruby -I targets/CFS/lib tests/test_cfs_time_conversion.rb
require 'minitest/autorun'
require 'openc3'
require 'openc3/packets/packet_config'
require 'tempfile'
require 'cfs_packet_headers'

class CfsTimeConversionTest < Minitest::Test
  def packet_for(width)
    name = width == 16 ? 'CFE_ES_HK' : 'TEST_FILE'
    header = width == 16 ? cfs_tlm_hdr('CFS-1', name, 'Timestamp regression') :
                          cfs_file_hdr('CFS-1', name, 'Timestamp regression')
    Tempfile.create(['cfs-time', '.txt']) do |file|
      file.write(header)
      file.flush
      config = OpenC3::PacketConfig.new
      config.process_file(file.path, 'CFS-1')
      return config.telemetry['CFS-1'][name]
    end
  end

  [16, 32].each do |width|
    [0, 10, 4_000_000_000].each do |seconds|
      [0, 1, 1 << (width - 1), (1 << width) - 1].each do |subseconds|
        define_method("test_#{width}_bit_time_#{seconds}_#{subseconds}") do
          packet = packet_for(width)
          sec_name, sub_name, time_name = width == 16 ?
            ['SECONDS', 'SUBSECS', 'PACKET_TIME'] :
            ['CREATE_TIME_SECONDS', 'CREATE_TIME_SUBSECS', 'FILE_CREATE_TIME']
          packet.write(sec_name, seconds)
          packet.write(sub_name, subseconds)
          expected = seconds + Rational(subseconds, 1 << width)
          assert_equal expected, packet.read(time_name).to_r
          assert_equal seconds, packet.read(sec_name, :RAW)
          assert_equal subseconds, packet.read(sub_name, :RAW)
          # Read the same bytes through a fresh packet generated from the header.
          copy = packet_for(width)
          copy.buffer = packet.buffer
          assert_equal expected, copy.read(time_name).to_r
        end
      end
    end
  end

  def test_binary_fraction_converter_preserves_epoch_offset_hook
    packet = packet_for(16)
    packet.write('SECONDS', 10)
    packet.write('SUBSECS', 32_768)
    conversion = packet.get_item('PACKET_TIME').read_conversion

    conversion.instance_variable_set(:@epoch_offset_seconds, 100)

    assert_equal Rational(221, 2), conversion.call(nil, packet, packet.buffer).to_r
  end

  def test_explicit_buffer_is_used_without_mutating_packet
    packet = packet_for(16)
    packet.write('SECONDS', 10)
    packet.write('SUBSECS', 32_768)
    original = packet.buffer.dup
    packet.write('SECONDS', 20)
    conversion = packet.get_item('PACKET_TIME').read_conversion
    assert_equal Rational(21, 2), conversion.call(nil, packet, original).to_r
    assert_equal Rational(41, 2), packet.read('PACKET_TIME').to_r
  end

  [16, 32].each do |width|
    define_method("test_serialized_conversion_round_trip_#{width}") do
      packet = packet_for(width)
      item_name = width == 16 ? 'PACKET_TIME' : 'FILE_CREATE_TIME'
      conversion = packet.get_item(item_name).read_conversion
      params = conversion.as_json['params']
      assert_equal width, params.last
      reconstructed = OpenC3::CfsTimeConversion.new(*params)
      assert_equal conversion.to_config('READ'), reconstructed.to_config('READ')
      assert_includes conversion.to_config('READ'), width.to_s
      assert_includes conversion.to_s, "2^#{width}"
    end
  end

  def test_invalid_subsecond_width_is_rejected
    [0, 8, 64, -1].each do |width|
      assert_raises(ArgumentError) { OpenC3::CfsTimeConversion.new('SECONDS', 'SUBSECS', width) }
    end
  end

  def test_legacy_microsecond_converter_remains_unchanged
    require 'unix_time_conversion_epoch_offset'
    packet = OpenC3::Packet.new('CFS-1', 'LEGACY', :BIG_ENDIAN)
    packet.append_item('SECONDS', 32, :UINT)
    packet.append_item('MICROSECONDS', 32, :UINT)
    packet.write('SECONDS', 10)
    packet.write('MICROSECONDS', 500_000)
    conversion = OpenC3::UnixTimeConversionEpochOffset.new('SECONDS', 'MICROSECONDS')
    assert_equal Rational(21, 2), conversion.call(nil, packet, packet.buffer).to_r
  end
end
