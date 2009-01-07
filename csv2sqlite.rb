require 'rubygems'
require 'sequel'
require 'fastercsv'

class Csv2Sqlite
  attr_accessor :fname
  attr_accessor :DB
  
  def initialize(options = Hash.new)
    #@fname = fname
    @options = {:primarykeys => []}.merge options
    if @options[:output]
      @DB = Sequel.connect("sqlite://#{@options[:output]}")
    else
      @DB = Sequel.sqlite # memory database
    end
  end
  
  def parse_string(csv_string)
    @fname = nil
    @table_exists = false
    FasterCSV.parse(csv_string) do |row|
      parse_row(row)
    end
  end
  
  
  def parse_file_slow(fname)
    require 'csv'
    rowcount = 0
    csv = CSV::Reader.create(File.open(fname,'rb'))
    def csv.skip_line
      @io.gets
    end
    
    begin
       while(row = csv.shift) do
         #parse_row(row)
         p row
         rowcount += 1
       end
    rescue CSV::IllegalFormatError => e
      puts "ERROR"
      puts e.message
      csv.skip_line
      retry
    end
    puts rowcount
  end
  
  def parse_file(fname)
    @fname = fname
    @table_exists = false
    csv = FasterCSV.open(fname, {:row_sep=>:auto})

    begin
      while(row = csv.shift) do
        parse_row(row)
      end
    rescue FasterCSV::MalformedCSVError => e
      puts "ERROR: #{e.message}. Rejecting row"
# #      puts csv.skip_line
#        csv = FasterCSV.open(fname, {:row_sep=>:auto})
#        def csv.skip_to_line(num)
#          num.times { @io.gets }
#        end
#        csv.skip_to_line 119
#        retry
    end
  end
  
  def print_stats
    @DB.tables.each do |t|
      dataset = @DB[t]
      puts "#{t.to_s.upcase.ljust(10)}: #{dataset.count} records"
    end
  end  
  
  def dump_db
    @DB.tables.each {|t| puts t.to_s; @DB[t].print }
  end
  
protected
  
  def create_table(tablename,header_row,primarykeys=[])
    @DB.create_table! tablename do 
      header_row.each do |c|
        if primarykeys.any? {|pk| pk == c}
          column c.intern, :text, {:unique=>true}
        else
          column c.intern, :text
        end 
      end
    end
  end
  
  def parse_row(row)
    if !@table_exists
      @header_row = row
      create_table(:csv,row,@options[:primarykeys])
      @table_exists = true
    else
      begin
        @DB[:csv] << row
      rescue Sequel::Error::InvalidStatement => e
        if e.message =~ /SQL logic error or missing database/
          # duplicate key
          create_table(:csv_dupes,@header_row) unless @DB.tables.include? :csv_dupes
          @DB[:csv_dupes] << row
        else
          raise e
        end
      end
    end
  end
end

if __FILE__ == $0
  require 'getoptlong.rb'
  optparser = GetoptLong.new
  optparser.set_options(
    ['--stats',   '-s', GetoptLong::NO_ARGUMENT],
    ['--dump',    '-d', GetoptLong::NO_ARGUMENT],
    ['--interactive',    '-i', GetoptLong::NO_ARGUMENT],
    ['--primarykeys',    '-p', GetoptLong::OPTIONAL_ARGUMENT],
    ['--output', '-o',  GetoptLong::OPTIONAL_ARGUMENT]
  )
  cmdline = Hash.new
  optparser.each_option do |k,v| 
    v = TRUE if v.empty?
    k = k.gsub(/-/,'').intern
    if cmdline[k].nil?
      cmdline[k] = v
    elsif cmdline[k].is_a? Array
      cmdline[k] << v
    else
      cmdline[k] = [cmdline[k], v]
    end
  end
  puts "options: "+cmdline.inspect
  fname = ARGV[0]
  raise "Input file '#{fname}' does not exist" if !File.exist?(fname)
  c2s = Csv2Sqlite.new cmdline
  c2s.parse_file(fname)
  c2s.print_stats if cmdline[:stats]
  c2s.dump_db if cmdline[:dump]
  if cmdline[:interactive]
    require 'irb'
    ARGV.clear
    DB = c2s.DB
    puts "Your data is in DB"
    IRB.start
  end
end