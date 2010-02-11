#!/usr/bin/env python
"""---------------------------------------------
USAGE: cleancsv.py [options] input [input2 ...] 
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

def sniffDialect(file):
	input_chunk = file.read(1024)
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
	file.seek(0)
	return dialect

def cleanFile(filename):
	orig_filename = filename
	ren_filename = filename + ".orig"
	os.rename(orig_filename, ren_filename)
	try:
		input = file(ren_filename,'r')
		output = file(orig_filename, 'w')
		dialect = sniffDialect(input)
		c = csv.reader(input,dialect = dialect)
		o = csv.writer(output, delimiter = c.dialect.delimiter)
		rowCount = 0
		header = c.next()
		if header:
			o.writerow(header)
			rowCount+=1
			expected_num_rows = len(header)
			for row in c:
				if len(row) != expected_num_rows:
					printVerbose("Wrong number of columns %s" % row)
				else:
					o.writerow(row)
					rowCount+=1
		printVerbose("%d rows processed" % rowCount)
	# except csv.Error as err:
		# if err == 'line contains NULL byte':
		# 	pass
	except Exception as err:
		printError("ERROR: %s " % err)
		printError("ERROR: Something went wrong, unable to parse %s. Reverting changes." % orig_filename)
		os.rename(ren_filename, orig_filename)
		pass
	input.close()
	output.close()

def main(argv):
	global verboseMode
	verboseMode = True # default on

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
		elif opt in ("-v", "--verbose"):
			verboseMode = True
		elif opt in ("-q", "--quiet"):
			verboseMode = False


	# print args
	if len(args) == 0:
		printUsage()
		return 1
	for arg in args:
		printVerbose("Cleaning %s" % (arg))
		cleanFile(arg)

	return 0


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:])) # slice this filename off args