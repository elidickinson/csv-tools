require 'test/unit'
require 'csv2sqlite'

class TC_c2s < Test::Unit::TestCase
  # def setup
  # end

  # def teardown
  # end

  def test_oneliner
    csv_string = "a,b,c,d\nthis,is,a,test"
    c2s = Csv2Sqlite.new()
    c2s.parse_string(csv_string)
    tbl = c2s.DB[:rows]
    assert_equal(1,tbl.count)
    #puts c2s.dump_db
  end

  def test_fail
    #assert(false, 'Assertion was false.')
  end
end