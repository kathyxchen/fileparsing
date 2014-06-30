import os
import os.path
import csv
import pandas as pd 
%matplotlib

# used in readFile
# convert to string & get rid of trailing whitespaces
def cleanUp(strSeries):
	return strSeries.apply(str).apply(str.strip)

#strList is a list of tuples with fields that should be type
# string marked as True.
def readFile(filename, strList, csvDF):
	df = pd.read_csv(filename, error_bad_lines=False)
	df = df.dropna(how='all')
	# if the first line is a header--
	# could replace this with a function that checked 
	# that the majority of rows were unnamed.
	if (df.columns[0] == 'Unnamed: 0'):
		df.iloc[0] = map(str.lower, df.iloc[0])
		df.columns = df.iloc[0]
	categ = df.columns
	fromCol = []
	fromList = []
	for l, t in strList:
		for c in categ:
			if (compare(c, l)):
				# only append the ones from strList that are present 
				# in the df.columns series
				fromCol.append(c)
				fromList.append(l)
				if (t):
					df[c] = cleanUp(df[c])
	if (len(fromCol) > 0): 
		df.sort(columns=fromCol[0], inplace=True)
		# this only works b/c I know the first one will be assigned type string.
		# could make a function that identifies this in case my argument is ordered differently.
		df = df[~df[fromCol[0]].str.contains(fromCol[0])]
	colNum = findPrice(fromList, fromCol, df)
	infoDict = findInfo(fromList, fromCol, df, colNum)
	for k in infoDict:
		row = ""
		for v in infoDict[k]:
			row = row + "%s, " %(v)
		pd.concate(csvDF, row)
	return csvDF

# if i ever wanted to try a gen case
def findAll(listOfLists, fromList):
	solution = []
	for l in listofLists:
		pos = len(solution)
		solution.append([])
		for i in l:
			if i in fromList:
				solution[pos].append(fromList.index(i))
	return solution

# used in prodInfo
def findPartNum(word):
	num = ''.join(x for x in word if x.isdigit())
	cutoff = ((float(len(num))/float(len(word))) >= 0.6)
	return (len(word) >= 8) & cutoff

# assumption that the length of these lists are > 0 
def findInfo(fromList, fromCol, df, colNum):
	n = findProduct(fromList)
	if (n >= 0 & ('description' in fromList)):
		categ = [fromCol[d], fromCol[n]]
		d = fromList.index('description')
		dSer = df[fromCol[d]][~df[fromCol[d]].str.contains('nan')].tolist()
		nSer = df[fromCol[n]][~df[fromCol[n]].str.contains('nan')].tolist()
		merged = merged(dSer, nSer)
		# get rid of duplicates
		mergedSet = set(merged) 
		result = prodInfo(mergedSet)
		return corresPrice(categ, df, result, colNum)
	elif ('description' in fromList):
		categ = [fromCol[d]]
		d = fromList.index('description')
		dSer = df[fromCol[d]][~df[fromCol[d]].str.contains('nan')].tolist()
		result = prodInfo(set(dSer))
		return corresPrice(categ, df, result, colNum) 
	elif (n >= 0):
		categ = [fromCol[n]]
		nSer = df[fromCol[n]][~df[fromCol[n]].str.contains('nan')].tolist()
		result = prodInfo(set(nSer))
		return corresPrice(categ, df, result, colNum)
	else:
		return {}

# used in findInfo
def corresPrice(categList, df, infoDict, colNum):
	if (colNum >= 0):
		for k in infoDict:
			for x in categList:
				arr = (df[x].str.contains(infoDict[k]))
				if any(arr):
					for idx, i in enumerate(arr):
						if i: 
							infoDict[k] = (infoDict[k], (df.iloc[i][colNum]))
						break
				break
		return infoDict
	else:
		return infoDict

# used in findInfo
def prodInfo(mergedSet):
	prodInfo = {}
	for px, s in enumerate(mergedSet):
		# go through each string in the set
		# split the words into a list
		des = mergedSet.pop().split()
		pos = -1
		inDict = False
		for idx, w in enumerate(des):
			# check for part num not already in list
			if (findPartNum(w)):
				pos = idx
				inDict = (w in prodInfo)
				break
		if (pos >= 0 & (not inDict)):
			# remove the part number from the des list
			prodInfo[des.pop(idx)] = (' '.join(des))
		else: 
			name = ' '.join(des)[:128]
			prodInfo[name] = (' '.join(des))
	return prodInfo

# used in findInfo
def merged(dList, pList):
	merged = []
	for idx, s in enumerate(dList):
    	if pList[idx] in s: 
        	merged.append(s)
    	elif s in pList[idx]: 
        	merged.append(pList[idx])
    	else: 
        	merged.append(pList[idx] + ' ' + s)
    return merged

# used in findInfo
def findProduct(fromList):
	if ('production' in fromList):
		return fromList.index('production')
	elif ('part #' in fromList):
		return fromList.index('part #')
	else: 
		return -1

# used in readFile
def findPrice(fromList, fromCol, df):
	if (('sales price unit' in fromList) & ('quote price unit' in fromList)):
		si = fromList.index('sales price unit')
		qi = fromList.index('quote price unit')
		sales = len(df[fromCol[si]].dropna())
		quote = len(df[fromCol[qi]].dropna())
		if (sales >= quote):
			return si
		else:
			return qi	
	elif ('sales price unit' in fromList):
		return fromList.index('sales price unit')
	elif ('quote price unit' in fromList):
		return fromList.index('quote price unit')
	else:
		return -1

# used in readFile
def compare(inTbl, inList):
	# get rid of all whitespaces
	inList = "".join(inList.split()).lower()
	inTbl = "".join(inTbl.split()).lower()
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

