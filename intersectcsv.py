#!/usr/bin/env python
import csv, sys, getopt
from collections import OrderedDict
# load first file into dict, then read second file and add/update fields

CSV_DIALECT = 'excel'

data = {}
data_fields = set()
data_key_field = None

def printError(message):
    try:
        sys.stderr.write(message + "\n")
    except UnicodeEncodeError:
        sys.stderr.write(message.encode("utf8"))

def file_to_dict(fname):
    with open(fname,'rb') as f:
        csv1 = csv.reader(f,dialect=CSV_DIALECT)
        header_row = csv1.next()
        data_key_field = header_row[0]
        data_fields.update(header_row)
        for row in csv1:
            row_dict = OrderedDict(zip(header_row,row))
            key_field = header_row[0]
            key_value = row[0]
            data[key_value] = row_dict

def update_dict(fname):
    with open(fname,'rb') as f:
        c = csv.reader(f,dialect=CSV_DIALECT)
        header_row = c.next()
        data_fields.update(header_row)
        for row in c:
            row_dict = OrderedDict(zip(header_row,row))
            key_field = header_row[0]
            key_value = row[0]
            if data.has_key(key_value):
                data[key_value] = dict(data[key_value].items() + row_dict.items())

def output_master(fname):
    with open(fname,'wb') as f:
        c = csv.writer(f)
        header_row = list(data_fields)
        c.writerow(header_row)
        for r in data.itervalues():
            data_row = [r.get(h) for h in header_row]
            c.writerow(data_row)

def main(argv):
    args = argv
    # print args
    if len(args) < 2:
        print "Needs at least two arguments"
        return 1

    print "Loading %s" % args[0]
    file_to_dict(args[0])

    for arg in args[1:]:
        print "Merging %s" % (arg)
        update_dict(arg)

    outfilename = "output.csv"
    print "Outputting combined data to %s" % outfilename
    output_master(outfilename)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:])) # slice this filename off args
