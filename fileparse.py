import os
import os.path
import csv
import pandas as pd 
%matplotlib

# convert to string & get rid of trailing whitespaces
def cleanUp(strSeries):
	return strSeries.apply(str).apply(str.strip)

# check if line still contains spaces after the cleanUp
def checkUp(strSeries):
	return (strSeries.str.contains(' '))

def readFile(filename, strList):
	df = pd.read_csv(filename, error_bad_lines=False)
	df = df.dropna(how='all')
	df.columns = map(str.lower, df.columns)
	categ = df.columns
	fromCol = []
	fromList = []
	for l, t in strList:
		for c in categ:
			if (compare(c, l)):
				categ.remove(c)
				# only append the ones from strList that are present 
				# in the df.columns series
				fromCol.append(c)
				fromList.append(l)
				if (t):
					df[c] = cleanUp(df[c])
	if (len(fromCol) > 0): 
		df.sort(columns=fromCol, inplace=True)


def findAll(listOfLists, fromList):
	solution = []
	for l in listofLists:
		pos = len(solution)
		solution.append([])
		for i in l:
			if i in fromList:
				solution[pos].append(fromList.index(i))
	return solution

# assumption that the length of these lists are > 0 
def findDesc(fromList, fromCol, df):
	fp = findProduct(fromList)
	if (fp >= 0 & ('description' in fromList)):
		d = fromList.index('description')
		dSer = df[fromCol[d]][~df[fromCol[d]].str.contains('nan')].tolist()
		fpSer = df[fromCol[fp]][~df[fromCol[fp]].str.contains('nan')].tolist()
		if (len(dSer) == 0 & len(fpSer) == 0):
			return None
		elif (len(dSer) == 0):
			checkDup(fpSer)
		elif (len(fpSer) == 0):
			checkDup(dSer)
		else:
			checkDup(fpSer)
			checkDup(dSer)


def checkDup(list):



def findProduct(fromList):
	if ('production' in fromList):
		return fromList.index('production')
	elif ('part #' in fromList):
		return fromList.index('part #')
	else: 
		return -1

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

