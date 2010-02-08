import sys
def main(argv):
	input_filename = argv[0]
	with file(input_filename,'rb') as f:
		data = f.read(4096)
		while data != "":
			sys.stdout.write(data.replace("\0",""))
			data = f.read(4096)
	

if __name__ == "__main__":
	sys.exit(main(sys.argv[1:])) # slice this filename off args