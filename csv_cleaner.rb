require 'csv'

class CsvCleaner
  def initialize(options = {})
    default_options = {:trim_fields => false}
    @options = default_options.merge options
  end
  
  # Takes a string representing one line of CSV, and returns an array representing
  #  the cleaned row.
  def line_to_row(line)
    
    return nil if line.empty?
    
    begin
      row = CSV::Reader.create(line).shift
    rescue CSV::IllegalFormatError => e
      row = bad_row(line)
    end
    unless row.nil?
      row = row.collect{|f| f.strip } if @options[:trim_fields]
    end
    return row
  end
  
  def bad_row(line)
    # puts "Bad Row: #{line}"
    nil
  end
  
end

class CsvFileCleaner < CsvCleaner
  def initialize(in_name,out_name)
    @in_name = in_name
    @out_name = out_name
    @infile = File.new(in_name,'r')
    @writer = CSV::Writer.create(File.new(out_name,'w'))
    p in_name
    p out_name
    super
  end
  
  def clean
    while(line = @infile.gets)
        row = line_to_row(line)
        # p row
        @writer << row
    end
  end
end

if __FILE__ == $0
  cfc = CsvFileCleaner($*.shift,$*.shift)
  cfc.clean
end