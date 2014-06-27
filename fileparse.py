import os
import os.path
import csv
import pandas as pd 
%matplotlib

def cleanUp(strSeries):
	return strSeries.apply(str).apply(str.strip)
	
def checkUp(strSeries):
	return (strSeries.str.contains(' '))

def readFile(filename, strList):
	df = pd.read_csv(filename, error_bad_lines=False)
	df = df.dropna(how='all')
	df.columns = map(str.lower, df.columns)
	categ = df.columns
	valid = []
	for l, t in strList:
		for c in categ:
			if (compare(c, l)):
				categ.remove(c)
				valid.append(c)
				if (t):
					df.c = cleanUp(df.c)
	df.sort(columns=valid, inplace=True)


def compare(inTbl, inList):
	# get rid of all whitespaces
	inList = "".join(inList.split())
	inTbl = "".join(inTbl.split())
	# if too long to begin with
	if (len(inTbl) > (float(len(inList)) + 0.50 * float(len(inList)))):
		return False
	# else start a counter
	ct = 0
	total = len(inList)
	for i in inList:
		if (len(inTbl) == 0):
			break
		if (i in inTbl):
			ct += 1
			pos = inTbl.index(i)
			inTbl = inTbl[:pos] + inTbl[(pos+1):]
	# need at least 83% similar  
	similarity = (float(ct)/float(total) >= 0.83)
	# length should be zero or less than 10%?
	remain = len(inTbl) < (0.10 * float(len(inList)))
	return (similarity & remain)

class fileparse(folder):
	location = "/Users/kathy/Documents/Dropbox/OpenERP/" + folder
	for fn in os.listdir(location):
		fpath = os.path.join(folder, fn)
		if (os.path.isfile(fpath) and fpath.endswith(".csv")):
			with open

