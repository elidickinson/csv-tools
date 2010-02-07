import csv, sys, getopt

def printUsage():
	print """---------------------------------------------
USAGE: csv2sqlite.py input [output] [tableName]

If output is not specified or is '-', sql statements will be sent to stdout."

If tableName is not specified, the table name will be automatically generated
from input filename or output filename.

	'contacts.sql' --> tablename = 'contacts'."""

def printVerbose(msg):
	global verboseMode
	if verboseMode:
		print msg


def main(argv):
	global tableName, verboseMode
	tableName = None
	verboseMode = False

	try:
		opts, args = getopt.getopt(argv, "h:t:v",  \
			["help", "verbose", "header=", "tablename=", "output="])
	except getopt.GetoptError:
		print "Invalid argument error"
		printUsage()
		sys.exit(2)
	
	for opt, arg in opts:
		if opt == "--help":
			printUsage()
			sys.exit()
		elif opt in ("-h", "--header"):
			header = arg.split(",")
		elif opt in ("-t", "--tablename"):
			tableName = arg
		elif opt in ("-v", "--verbose"):
			verboseMode = True
	
	print args
	if len(args) != 1:
		printUsage()
		return 1
	input_filename = args[0]

	input = file(input_filename,'r')
	if tableName == None:
		tableName = input_filename.replace('.csv','').replace(' ','_')

	# if len(argv) == 2:
	# 	output = sys.stdout
	# else:
	# 	if argv[2] == '-':
	# 		output = sys.stdout
	# 	else:
	# 		output = file(argv[2],'w')
	# 		tableName = argv[2].replace('.sql','').replace(' ','_')

	# sniff dialect of csv 
	dialect = csv.Sniffer().sniff(input.read(1024))
	
	# reset input file back to beginning
	input.seek(0)
	
	c = csv.reader(input, dialect)
	header = c.next()
	printVerbose(header)
	input.close()
	return 0


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:])) # slice this filename off args