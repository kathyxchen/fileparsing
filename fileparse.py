import os
import os.path
import csv
import pandas as pd 
%matplotlib

from itertools import groupby as g
def common(l):
  return max(g(sorted(l)), key=lambda(x, v):(len(list(v)),-l.index(x)))[0]

def cleanUp(strSeries):
	return strSeries.apply(str).apply(str.strip)

def findPartNum(word):
	num = ''.join(x for x in word if x.isdigit())
	cutoff = ((float(len(num))/float(len(word))) >= 0.55)
	return (len(word) >= 8) and cutoff

import numpy as np
def corresPrice(categList, df, infoDict, priceCol, fromCol):
	if (len(priceCol) > 0 and len(infoDict) == 1):
		print "acc cp 1"
		priceCol = [x for x in priceCol if not pd.isnull(x)]
		if (len(priceCol) > 1):
			infoDict[infoDict.keys()[0]][1] = common(priceCol) 
		elif (len(priceCol) == 1):
			infoDict[infoDict.keys()[0]][1] = priceCol[0]
		return infoDict
	elif (len(priceCol) > 0 and len(infoDict) > 1):
		print "acc cp 2"
		for k, v in infoDict.iteritems():
			for x in categList:
				df[x] = df[x].apply(str.upper)
				arr = (df[x].str.contains(k))
				if any(arr):
					for idx, i in enumerate(arr):
						if i: 
							v[1] = (priceCol[idx])
							break
					break
			if (pd.isnull(v[1]) or v[1] == 'NaN'):
				v[1] = 0.0
		return infoDict
	else:
		return infoDict

def prodInfo(mergedSet, prodInfoDict):
	if (len(mergedSet) == 0):
		return prodInfoDict
	else:
		# go through each string in the set
		# split the words into a list
		des = mergedSet.pop().split()
		pos = -1
		inDict = False
		for idx, w in enumerate(des):
			# check for part num not already in list
			if (findPartNum(w)):
				pos = idx
				inDict = (w in prodInfoDict)
				break
		if (pos >= 0 and (not inDict)):
			# remove the part number from the des list
			partNum = des.pop(idx)
			prodInfoDict[partNum] = [(' '.join(des)), 0.0]
		elif (pos < 0 and (not inDict)): 
			name = ' '.join(des)[:128]
			prodInfoDict[name] = [(' '.join(des)), 0.0]
		return prodInfo(mergedSet, prodInfoDict)

def merged(l1, l2):
	merged = []
	for idx, s in enumerate(l1):  
		if (s != ' ' or l2[idx] != ' '):    
			if l2[idx] in s: 
				merged.append(s)
			elif s in l2[idx]: 
				merged.append(l2[idx])
			else: 
				merged.append(l2[idx] + ' ' + s)
	return merged

def findProduct(fromList):
	if ('production' in fromList):
		return fromList.index('production')
	elif ('part #' in fromList):
		return fromList.index('part #')
	else: 
		return -1

def findPrice(fromList, fromCol, df):
	if (('sales price unit' in fromList) and ('quote price unit' in fromList)):
		si = fromList.index('sales price unit')
		qi = fromList.index('quote price unit')
		spu = df[fromCol[si]].tolist()
		qpu = df[fromCol[qi]].tolist()
		merged = []
		for idx, x in enumerate(spu):
			if pd.isnull(x):
				x = ' ' 
		for idx, x in enumerate(qpu):
			if pd.isnull(x):
				x = ' ' 
		for idx, s in enumerate(spu):
			if (s != ' ' and qpu[idx] != ' '):
				merged.append(max(s, qpu[idx]))
			elif (s != ' '):
				merged.append(s)
			else:
				merged.append(qpu[idx])
		return merged
	elif ('sales price unit' in fromList):
		return df[fromCol[fromList.index('sales price unit')]]
	elif ('quote price unit' in fromList):
		return df[fromCol[fromList.index('quote price unit')]]
	else:
		return []

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
	return (similarity and remain)

def replacement(lt):
	for idx, item in enumerate(lt):
		if item == 'nan':
			lt[idx] = ' '
	return lt

def findInfo(fromList, fromCol, df, priceCol):
	n = findProduct(fromList)
	if (n >= 0 and ('description' in fromList)):
		print "acc 1"
		d = fromList.index('description')
		categ = [fromCol[d], fromCol[n]]
		dSer = replacement(df[fromCol[d]].tolist())
		nSer = replacement(df[fromCol[n]].tolist())
		m = merged(dSer, nSer)
		# get rid of duplicates
		m = [x.upper() for x in m]
		mergedSet = set(m) 
		result = prodInfo(mergedSet, {})
		return corresPrice(categ, df, result, priceCol, fromCol)
	elif ('description' in fromList):
		print "acc 2"
		categ = [fromCol[d]]
		d = fromList.index('description')
		dSer = df[fromCol[d]][~df[fromCol[d]].str.contains('nan')].tolist()
		result = prodInfo(set(dSer), {})
		return corresPrice(categ, df, result, priceCol, fromCol) 
	elif (n >= 0):
		print "acc 3"
		categ = [fromCol[n]]
		nSer = df[fromCol[n]][~df[fromCol[n]].str.contains('nan')].tolist()
		result = prodInfo(set(nSer), {})
		return corresPrice(categ, df, result, priceCol, fromCol)
	else:
		print "acc 4"
		return {}

def readFile(filename, strList, csvDF, idx):
	print filename
	df = pd.read_csv(filename, error_bad_lines=False, skiprows=idx)
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
	#colNum = findPrice(fromList, fromCol, df)
	#infoDict = findInfo(fromList, fromCol, df, colNum)
	priceCol = findPrice(fromList, fromCol, df)
	infoDict = findInfo(fromList, fromCol, df, priceCol)
	dfList = []
	for k, v in infoDict.iteritems():
		k = k.replace(',',';')
		v[0] = v[0].replace(',',';')
		dfList.append({'Product Name': k, 'Description': v[0], 'Price': v[1]})
	newDF = pd.DataFrame(dfList)
	return pd.concat([newDF, csvDF])
	#return newDF
	#pd.DataFrame.append(csvDF, newDF)
	#return csvDF

def fileparse(folder):
	testDF = pd.DataFrame(columns = ['Product Name', 'Description', 'Price'])
	location = "/Users/kathy/Documents/Dropbox/OpenERP/" + folder
	for fn in os.listdir(location):
		fpath = os.path.join(folder, fn)
		if (os.path.isfile(fpath) and fpath.endswith(".csv")):
			with open(fpath, 'rU') as csvfile:
				print csvfile   
				rder = csv.reader(csvfile)
				fstRow = (rder.next()[0] == '')
				boolList = []
				for row in rder:
					boolList.append(''.join(row) == '')
				idx = [(id + 1) for id, i in enumerate(boolList) if i]
				if (fstRow):
					ids = [0] + idx
				strList = [('part #', True), ('description', True), ('production', True), ('sales price unit', False), ('quote price unit', False)]
				testDF = readFile(fpath, strList, testDF, idx)
	testDF.index = range(0, len(testDF.index))
	testDF.to_csv('/Users/kathy/Documents/Dropbox/OpenERP/testProd.csv')
	return testDF

testDF = pd.DataFrame(columns = ['Product Name', 'Description', 'Price'])
strList = [('part #', True), ('description', True), ('production', True), ('sales price unit', False), ('quote price unit', False)]
filename = 'Magnetic Divert Controller.csv'
test = readFile(filename, strList, testDF, [])
test
fileparse("DematicProdHist")