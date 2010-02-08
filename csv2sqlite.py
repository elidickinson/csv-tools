#!/usr/bin/env python
"""---------------------------------------------
USAGE: csv2sqlite.py input [options] [source file]
	-v, --verbose	Verbose mode. Prints to stdout.
"""

import csv, sys, getopt, re, os, string

def printUsage():
	print __doc__

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
	global tableName
	retval = "\nDROP TABLE IF EXISTS `%s`;" % tableName
	retval += "\n-- HEADER ROW\n-- %s" % "//".join(header)
	retval += "\nCREATE TABLE `%s` (\n" % tableName
	fieldDefs = []
	for field in header:
		fieldName = re.sub("[^a-zA-Z0-9_]+","_",field).strip("_").lower()
		if fieldName == 'email':
			collation = "COLLATE NOCASE"
		else:
			collation = ""
		fieldDefs.append("`%s` TEXT %s" % (fieldName, collation))
	print fieldDefs
	retval += ",\n".join(fieldDefs) # string.join(fieldDefs, ",")
	retval += "\n);\n\n"
	return retval

def insertRow(row):
	global tableName
	row = ["`"+x+"`" for x in row]
	values = ",".join(row)
	retval = "INSERT INTO `%s` VALUES (%s);" % (tableName,values)
	return retval

def main(argv):
	global tableName, verboseMode, keyField
	tableName = None
	keyField = None
	verboseMode = False

	try:
		opts, args = getopt.getopt(argv, "h:t:k:v",  \
			["help", "verbose", "header=", "tablename=", "output=", "key="])
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
		elif opt in ("-k", "--key"):
			keyField = arg
	
	print args
	if len(args) != 1:
		printUsage()
		return 1
	input_filename = args[0]

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
			printVerbose("Guess Excel TSV")

	# reset input file back to beginning
	input.seek(0)
	#c = csv.DictReader(input,dialect = dialect)
	c = csv.reader(input,dialect = dialect)
	header = c.next()
	printVerbose("Header row: %s" % header)
	print createTable(header)
	for row in c:
		print insertRow(row)
	input.close()
	return 0


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:])) # slice this filename off args