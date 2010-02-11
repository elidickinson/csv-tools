#!/usr/bin/env python
"""---------------------------------------------
USAGE: csv2sqlite.py input [options] [source file]
	-v, --verbose	Verbose mode. Adds extra comments to SQL
"""

__author__ = "Eli Dickinson (eli-at-elidickinson-com)"
__version__ = "0.1"

import csv, sys, getopt, re, os, string, time

def printUsage():
	printError(__doc__)

def printVerbose(msg):
	global verboseMode
	if verboseMode:
		print "-- " + str(msg)

def printError(message):
	try:
		sys.stderr.write(message + "\n")
	except UnicodeEncodeError:
		sys.stderr.write(message.encode("utf8"))


def createTable(header):
	global tableName, verboseMode, keyField
	fieldNames = [] # not yet used
	retval = "\nDROP TABLE IF EXISTS `%s`;" % tableName
	retval += "\nCREATE TABLE `%s` (\n" % tableName
	fieldDefs = []
	for field in header:
		fieldName = re.sub("[^a-zA-Z0-9_]+","_",field).strip("_").lower()
		fieldNames.append(fieldName)
		if fieldName == 'email': # special case hack
			collation = "COLLATE NOCASE"
		else:
			collation = ""
		if keyField and keyField == fieldName:
			keyOptions = "PRIMARY KEY"
		else:
			keyOptions = ""
		fieldDefs.append("`%s` TEXT %s %s" % (fieldName, collation, keyOptions))
	retval += ",\n".join(fieldDefs) # string.join(fieldDefs, ",")
	retval += "\n);\n\n"
	return retval

def insertRow(row):
	global tableName
	row = ["'%s'" % x.replace("'","''") for x in row]
	values = ",".join(row)
	retval = "INSERT INTO `%s` VALUES (%s);" % (tableName,values)
	return retval

def main(argv):
	global tableName, verboseMode, keyField
	tableName = None
	keyField = None # TODO: allow numeric value to specify column by number
	verboseMode = True # default on
	header = None
	skipRows = 0
	ignoreColumns = None
	tableExists = False

	try:
		opts, args = getopt.getopt(argv, "h:t:k:vq",  \
			["help", "verbose", "quiet", "header=", "tablename=", "output=", "key=", "skip=", "ignore=", "tableexists"])
	except getopt.GetoptError:
		printError("Invalid argument error")
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
		elif opt in ("-q", "--quiet"):
			verboseMode = False
		elif opt in ("-k", "--key"):
			keyField = arg
		elif opt in ("--skip"):
			skipRows = int(arg)
		elif opt in ("--ignore"):
			ignoreColumns = arg.split(",")
		elif opt in ("--tableexists"):
			tableExists = True

	# print args
	if len(args) != 1:
		printUsage()
		return 1
	input_filename = args[0]
	
	printVerbose("csv2sql.py - Version %s - Run date: %s" % (__version__, time.ctime()) )
	printVerbose("Source file: %s - %d bytes - Stamped %s" \
		% (os.path.basename(input_filename), os.path.getsize(input_filename), time.ctime(os.path.getmtime(input_filename))) )
	printVerbose("Skipping %d row(s)" % skipRows)
	
	input = file(input_filename,'r')
	if tableName == None:
		tableName = os.path.basename(input_filename)
		tableName = tableName.lower()
		tableName = re.sub('\..*$','',tableName)
		tableName = re.sub('[^a-z0-9_]+','_',tableName)
	
	# sniff dialect of csv 
	input_chunk = input.read(1024)
	try:
		dialect = csv.Sniffer().sniff(input_chunk)
	except csv.Error:
		printVerbose("Unable to sniff CSV dialect")
		commas = input_chunk.count(",")
		tabs = input_chunk.count("	")
		if(commas > tabs):
			dialect = "excel"
			printVerbose("Guessing Excel CSV")
		elif(tabs > commas):
			dialect = "excel-tab"
			printVerbose("Guessing Excel TSV")

	# reset input file back to beginning
	input.seek(0)
	#c = csv.DictReader(input,dialect = dialect)
	c = csv.reader(input,dialect = dialect)
	if header == None:
		header = c.next()
	for i in range(skipRows):
		c.next()
	printVerbose("Using header row: %s" % header)
	if not tableExists:
		print createTable(header)
	print "\nbegin;\n"
	for row in c:
		print insertRow(row)
	print "\ncommit;\n"
	input.close()
	return 0


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:])) # slice this filename off args