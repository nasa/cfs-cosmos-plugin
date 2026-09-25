require 'openc3/conversions/conversion'

module OpenC3
  # cFE subseconds are a binary fraction, not a count of microseconds.
  # Retain the existing seconds/epoch convention while decoding that fraction.
  class CfsTimeConversion < Conversion
    def initialize(seconds_item_name, subseconds_item_name, subseconds_bits)
      super()
      @seconds_item_name = seconds_item_name
      @subseconds_item_name = subseconds_item_name
      @subseconds_bits = Integer(subseconds_bits)
      unless [16, 32].include?(@subseconds_bits)
        raise ArgumentError, 'cFS subseconds must be 16 or 32 bits'
      end
      @converted_type = :RUBY_TIME
      @converted_bit_size = 0
    end

    def call(value, packet, buffer)
      seconds = packet.read(@seconds_item_name, :RAW, buffer)
      fraction = Rational(packet.read(@subseconds_item_name, :RAW, buffer), 1 << @subseconds_bits)
      Time.at(seconds + fraction).sys
    end

    def to_s
      "cFS time #{@seconds_item_name} + #{@subseconds_item_name}/2^#{@subseconds_bits}"
    end

    def to_config(read_or_write)
      "    #{read_or_write}_CONVERSION #{self.class.name.class_name_to_filename} #{@seconds_item_name} #{@subseconds_item_name} #{@subseconds_bits}\n"
    end

    def as_json(*args)
      result = super(*args)
      result['params'] = [@seconds_item_name, @subseconds_item_name, @subseconds_bits]
      result
    end
  end
end
