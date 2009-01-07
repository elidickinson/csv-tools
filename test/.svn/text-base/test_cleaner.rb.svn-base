require 'test/unit'
require 'csv_cleaner'

class TC_cleaner < Test::Unit::TestCase
  # def setup
  # end

  # def teardown
  # end

  # def test_oneliner
  #   c = CsvCleaner.new('onliner.csv','testout.csv')
  # end

  def test_cc_trimming
    cc = CsvCleaner.new({:trim_fields => false })
    assert_equal([' A ',' B'],cc.line_to_row(' A , B'))
    
    cc = CsvCleaner.new({:trim_fields => true })
    assert_equal(['A','B'],cc.line_to_row(' A , B'))
  end
  
  def test_cc_basic
    cc = CsvCleaner.new({:trim_fields => false })

    shouldbe = ['A','B','C']
    
    test = "A,B,C"
    assert_equal(shouldbe,cc.line_to_row(test))

    test = 'A,"B",C'
    assert_equal(shouldbe,cc.line_to_row(test))
    
    
    
    # blank line
    assert_nil cc.line_to_row('')
  end
  
  def test_cc_broken
    cc = CsvCleaner.new
    assert_nil cc.line_to_row('A,"B')
  end
  # def test_cc_cleaning
  #   cc = CsvCleaer.new
  # end
  
  def test_file_oneliner
    cfc = CsvFileCleaner("oneliner.csv","testoutput.csv")
    cfc.clean
    assert_equal "oneliner.csv","testoutput.csv"
    assert_csv_equal "oneliner.csv","testoutput.csv"
  end
  
  def csv_to_array(fn)
    f = File.new(fn,'r')
  end  

end