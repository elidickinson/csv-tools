require 'rubygems'
require 'fastercsv'
require 'sqlite3'

class Csv2Sqlite
  attr_accessor :DB
  def initialize(db_name)
    @DB = SQLite3::Database.new(db_name)
  end
  
  def add_csv(fname)
    f = File.open(fname, 'rb')
    tablename = File.split(fname)[1].gsub(/\.csv$/i,'').gsub(/[^0-9a-zA-Z_]/,'')
    
    csv = FasterCSV.new(f)
    
    cols = csv.shift
    cols = cols.collect { |c| c.gsub(/[^0-9a-zA-Z_]/,'')} 
    createstr = cols.collect{ |c| c + " varchar" }  
    createstr = createstr.join(",")
    @DB.execute("Create table #{tablename} (#{createstr})")
    while row = csv.shift and !row.empty?
      
      placeholders = []
      cols.length.times { placeholders << "?" }

      insertstr = "Insert into #{tablename} (#{cols.join(',')}) VALUES (#{placeholders.join(',')});"
      # insertstr = "insert into #{tablename} "
      # 
      # i = 0
      # cols.each{ |c| 
      #   inserstr += " #{c} = #{row[i]} "
      #   i++ 
      # }
      # insertstr += cols.
      # cols.each { |c| }
      # p insertstr
      @DB.execute(insertstr, *row)
    end
    # db.execute(".import #{table} #{tablename}")
  end
end

if __FILE__ == $0
  # 
  c2s = Csv2Sqlite.new("csv.db")
  # c2s.parse_file(fname)
  files = ARGV
  
  files.each do |fname|
    puts fname
    raise "Input file '#{fname}' does not exist" if !File.exist?(fname)
    c2s.add_csv(fname)
  end
  exec "sqlite3 csv.db"
end