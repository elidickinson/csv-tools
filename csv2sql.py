#!/usr/bin/env python
"""---------------------------------------------
USAGE: csv2sql.py [options] input.csv
	-v, --verbose	Verbose mode. Adds extra comments to SQL
	-q, --quiet		Disable verbose mode. Fewer comments in SQL
	-t <name>, --table-name=<name>	Use given name for table in
		SQL (otherwise it's generated from the input file name)
	--ignore=	Ignore the comma separated list of columns
	--skip=n	Skip given number of lines at start of file
		(after reading header)
	-k, --key=	Set key field (defaults to no key)
	--extract-domain	Creates new column named Domain with
	domain from extracted from field named 'email'
	--convert-dates		Attempt to make date fields SQL-friendly
	--mysql
	--sqlite (default)
"""

__author__ = "Eli Dickinson (eli%selidickinson.com)" % "@"
__version__ = "0.3"

import csv, sys, getopt, re, os, string, time
from datetime import datetime


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
	global tableName, verboseMode, keyField, addDomain, dbType
	fieldNames = []
	unknownCounter = 1
	retval = "\nDROP TABLE IF EXISTS `%s`;" % tableName
	retval += "\nCREATE TABLE `%s` (\n" % tableName
	fieldDefs = []
	for field in header:
		fieldName = re.sub("[^a-zA-Z0-9_]+","_",field).strip("_").lower()
		
		# dirty special case hack: remove Subscribe To
		# fieldName = re.sub("^subscribe_to_","",fieldName)
		
		# make sure names are not blank
		if fieldName == '':
			fieldName = 'unknown'
		if fieldName in fieldNames:
			fieldName += str(unknownCounter)
			unknownCounter += 1
		
		fieldNames.append(fieldName)
		
		if fieldName == 'email': # special case hack
			collation = "COLLATE NOCASE"
		else:
			collation = ""
		if keyField and keyField == fieldName:
			keyOptions = "PRIMARY KEY"
		else:
			keyOptions = ""
		
		if dbType == "sqlite":
			fieldDefs.append("`%s` TEXT %s %s" % (fieldName, collation, keyOptions))
		elif dbType == "mysql":
			fieldDefs.append("`%s` VARCHAR(255)" % (fieldName))
	if addDomain:
		fieldDefs.append("`domain` TEXT COLLATE NOCASE")
	retval += ",\n".join(fieldDefs) # string.join(fieldDefs, ",")
	if keyField and dbType == "mysql":
		retval += ",\nPRIMARY KEY (`%s`)" % keyField
	retval += "\n);\n\n"
	return retval



def insertRow(row):
	global tableName, convertDates
	if convertDates:
		for index,x in enumerate(row):
			if re.match("^\d+/\d+/\d+ \d+:\d+ (am|AM|pm|PM)$", x):
				try:
					dt = datetime.strptime(x, '%m/%d/%Y %I:%M %p')
					row[index] = dt.strftime('%Y-%m-%d %H:%M')
				except ValueError:
					printVerbose("Unable to convert %s to date" % x)
	if addDomain and len(row) > 1:
		# TODO assumes email is first
		email = row[0]
		domain = re.sub('^[^@]+@','',email)
		#domain = 'foo'
		row.append(domain)
	row = ["'%s'" % x.replace("'","''") for x in row]
	values = ",".join(row)
	retval = "INSERT INTO `%s` VALUES (%s);" % (tableName,values)
	return retval

def main(argv):
	global tableName, verboseMode, keyField, convertDates, addDomain, csvMode, dbType
	csvMode = None
	tableName = None
	keyField = None # TODO: allow numeric value to specify column by number
	verboseMode = True # default on
	convertDates = False
	addDomain = False
	header = None
	skipRows = 0
	ignoreColumns = None
	tableExists = False
	dbType = "sqlite"

	try:
		opts, args = getopt.getopt(argv, "?h:t:k:vq",  \
			["help", "verbose", "quiet", "extract-domain", "convert-dates", "header=", "table-name=", "tablename=", "version",\
			"output=", "key=", "skip=", "ignore=", "table-exists", "force-csv", "mysql","sqlite"])
	except getopt.GetoptError:
		printError("ERROR: Invalid argument")
		printUsage()
		sys.exit(2)
	
	for opt, arg in opts:
		if opt in ("--help","-?"):
			printUsage()
			sys.exit()
		elif opt in ("--version"):
			print "csv2sql.py by %s, Version: %s " % (__author__,__version__)
			sys.exit()
		elif opt in ("--force-csv"):
			csvMode = 'excel'
		elif opt in ("-h", "--header"):
			header = arg.split(",")
		elif opt in ("-t", "--tablename","--table-name"):
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
		elif opt in ("--tableexists", "--table-exists"):
			tableExists = True
		elif opt in ("--extract-domain"):
			addDomain = True
		elif opt in ("--convert-dates"):
			convertDates = True
		elif opt in ("--mysql"):
			dbType = "mysql"

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
	
	if csvMode == None:
		# sniff dialect of csv 
		input_chunk = input.read(4096)
		try:
			dialect = csv.Sniffer().sniff(input_chunk)
		except csv.Error:
			printVerbose("Unable to sniff CSV dialect")
			commas = input_chunk.count(",")
			tabs = input_chunk.count("	")
			if(commas >= tabs):
				dialect = "excel"
				printVerbose("Guessing Excel CSV")
			elif(tabs > commas):
				dialect = "excel-tab"
				printVerbose("Guessing Excel TSV")
	else:
		dialect = csvMode

	# reset input file back to beginning
	input.seek(0)
	#c = csv.DictReader(input,dialect = dialect)
	# import pprint
	# pprint.pprint(dialect)
	# if(type(dialect) == type(""))
	# 	printVerbose("Column delimiter is: " % dialect)
	# elif(dialect.delimiter == "\t")
	# 	printVerbose("Column delimiter is: " % dialect)
	printVerbose("CSV Delimiter is: %s" % (dialect if type(dialect) == type("") else dialect.delimiter))
	c = csv.reader(input,dialect = dialect)
	if header == None:
		header = c.next()
	for i in range(skipRows):
		c.next()
	printVerbose("Using header row: %s" % header)
	if not tableExists:
		print createTable(header)
	if dbType == "mysql":
		print "\START TRANSACTION;\n"
	elif dbType == "sqlite":
		print "\nbegin;\n"
	for row in c:
		print insertRow(row)
	print "\ncommit;\n"
	input.close()
	return 0


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:])) # slice this filename off args
