# -*- coding: utf-8 -*-
import urllib.request
import re
import lxml
import requests


from models_blogs import vulns_blogs

from flask import Flask, request, flash, url_for, redirect, render_template, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from sqlalchemy import exists
import scoring_functions

import telegrambot


app = Flask(__name__)

app.config.from_object('config.BaseConfig')

db = SQLAlchemy(app)

db.create_all()


import datetime

now = datetime.datetime.now()

mylist = ['http://seclists.org/fulldisclosure/', 'https://googleprojectzero.blogspot.it/', 'http://www.securityfocus.com/vulnerabilities', 'https://www.rapid7.com/db/modules', 'https://cxsecurity.com/exploit/', 'https://packetstormsecurity.com/files/tags/exploit/']

##TEST
'''
class vulns(db.Model):
	id = db.Column('vuln_id', db.Integer, primary_key=True)
	name = db.Column(db.String(500))
	date = db.Column(db.String(500))
	my_cve = db.Column(db.String(50))
	score = db.Column(db.String(500))
	source = db.Column(db.String(500))


	def __init__(self, name, date, my_cve, score, source):
		self.name = name
		self.date = date
		self.my_cve = my_cve
		self.score = score
		self.source = source
'''
##FINE TEST




def getpage(alist):
  #return [ urllib.request.urlopen(url) for url in alist  ]
  return [ requests.get(url).text for url in alist  ]

allhtml = getpage(mylist)
# allhtml = []
from bs4 import BeautifulSoup
bsObj = []

for idx, url in enumerate(allhtml):
  #print (el)
	if idx != 2: #---------------------------------------------------------el != 2
		bsObj.append(BeautifulSoup(url, 'html.parser'))
	else:
		bsObj.append(BeautifulSoup(url, 'html.parser'))
		
def packetstorm():
  #get dates of vulnerabilities
	pageDates = bsObj[5].findAll("dd", {'class': 'datetime'})
	#print(pageDates)
	#get names of vulnerabilities
	pageNames = bsObj[5].findAll('dt')[:-4]

	#print(pageNames)	
	#pageScore = bsObj[0].findAll(text = re.compile('Med.')) ----------------------------------
	#print(pageScore)
	#('label-label danger', 'label label-warning', 'label label-success')
  
	dates = []
	vulnNames = []
	vulnScores = []
	
	###################### realDic = { 'Data': [ [Names], [score] ] }
	
	for date in pageDates:
		x = date.get_text()[7:-6]
		dates.append(x.replace('  ', ' 0'))
	#print(dates)
	#print (listDate)
	#print (str(listDate))
	for vuln in pageNames:
		vulnNames.append(str(vuln))
	#print(vulnNames)
		
	for score in pageNames: #------------------------------------------ in pageScore!!
		vulnScores.append(score.get_text())	

	length = [ dates[i] == dates [i+1] for i in range(len(dates)-1) ]
	
	x = []
	for index,item in enumerate(length):
		if item == False:
			x.append(index)
		
	return dates, vulnNames, vulnScores, length, x #dictionary and all vulnerabilities
packetstorm = packetstorm()[0:5]



def rapid7():
  #get dates of vulnerabilities
	pageDates = bsObj[3].findAll(text = re.compile('Disclosed: '))
	#print(pageDates)
	#get names of vulnerabilities
	pageNames = bsObj[3].findAll("a", {'href': lambda x: x and x.startswith('/db/modules/')})
	#print(pageNames)
	
	dates = []
	vulnNames = []
	vulnScores = []
	
	###################### realDic = { 'Data': [ [Names], [score] ] }
	
	for date in pageDates:
		dates.append(str((re.split (',' , date[11:]))[0]))
	#print(dates)
	#print (listDate)
	#print (str(listDate))
	for vuln in pageNames:
		vulnNames.append(str(vuln))
		
	for score in pageNames: #------------------------------------------ in pageScore!!
		vulnScores.append(score.get_text())	
	length = [ dates[i] == dates [i+1] for i in range(len(dates)-1) ]

	x = []
	for index,item in enumerate(length):
		if item == False:
			x.append(index)
		
	return dates, vulnNames, vulnScores, length, x #dictionary and all vulnerabilities
rapid7 = rapid7()[0:5]
# rapid7 = [rapid7()[0], rapid7()[1], rapid7()[2], rapid7()[3], rapid7()[4]]


def securityfocus():
  
  #get dates of vulnerabilities

	pageDates = bsObj[2].findAll("span", {'class': 'date'})
	
	#get names of vulnerabilities
  
	#pageNames = bsObj[2].findAll("span", {'class': 'headline'})
	
	pageNames = bsObj[2].findAll("a", {"href": lambda x: x and x.startswith('/bid/')})
	pageNames = pageNames[::2]
	
	#for name in str(pageNames):
		#name = name.replace('<span', ' ')
		#name = name.replace('</span>', ' ')
	
	#pageNames_Links = []
	
	#for name, link in zip(pageNames, pageLinks):
		#pageNames_Links.append(str(str(link) + str(name)))
	
	#print (alist[0])

  
	dates = []
	vulnNames = []
	vulnScores = []
	
	###################### realDic = { 'Data': [ [Names], [score] ] }
	
	for date in pageDates:
		dates.append(date.get_text()[-5:])	
	
	
	#print (listDate)
	
	#print (str(listDate))
	
	for vuln in pageNames:
		vulnNames.append(str(vuln))
	
		
	for score in pageNames: #------------------------------------------ in pageScore!!
		vulnScores.append(score.get_text())	

	
	length = [ dates[i] == dates [i+1] for i in range(len(dates)-1) ]
	

	x = []
	for index,item in enumerate(length):
		if item == False:
			x.append(index)
		
	return dates, vulnNames, vulnScores, length, x #dictionary and all vulnerabilities
securityfocus = securityfocus()[0:5]
# securityfocus = [securityfocus()[0], securityfocus()[1], securityfocus()[2], securityfocus()[3], securityfocus()[4]]




### realDic = { 'date': [ [names], [scores] ] }


### date -> elemento della lista settata dates

### names -> sottolista con elenco dei nomi relativi a date (len)

### allNames -> lista contenente le sottoliste names 

### score -> lista (MANCA)

### vulNames -> lista contenente tutte le vulnerabilita


# vulnNames -> get_text() 




#vulnScores = ['1', '1', '2', '1', '3', '1']
#vulnNames = ['a', 'b', 'c', 'd', 'e', 'f']
#allNames = [['a'], ['b', 'c'], ['d', 'e'], ['f']]
#dates = ['1',   '2',  '2',  '3',   '3', '4']


def fulldisclosure():

	#get dates of vulnerabilities

	pageDates = bsObj[0].findAll("em")
	
	#print vuln

	#get names of vulnerabilities

	pageNames = bsObj[0].findAll("a", {"href": lambda x: x and x.startswith('http://seclists.org/fulldisclosure/20')}) #lambda x:  x and x.startswith
	
	#print (allName)

	dates = []
	vulnNames = []
	vulnScores = []
	
	###################### realDic = { 'Data': [ [Names], [score] ] }
	
	for date in pageDates:
		dates.append(date.get_text()[-7:-1])
	#dates.sort(reverse = True)
		
	#print(dates)
	
	#print (listDate)
	
	#print (str(listDate))
	
	for vuln in pageNames:
		vulnNames.append((str(vuln)).replace('\t', ' '))
		
		
	for score in pageNames: #------------------------------------------ in pageScore!!
		vulnScores.append(vuln.get_text())	

	
	length = [ dates[i] == dates [i+1] for i in range(len(dates)-1) ]

	x = []
	for index,item in enumerate(length):
		if item == False:
			x.append(index)
	
	#print (dates)
	#print (vulnNames)
		
	return dates, vulnNames, vulnScores, length, x #dictionary and all vulnerabilities

fulldisclosure = fulldisclosure()[0:5]
# fulldisclosure = [fulldisclosure()[0], fulldisclosure()[1], fulldisclosure()[2], fulldisclosure()[3], fulldisclosure()[4]]

def get_link(string, source):
	
	name_link = []
	
	if 'href' in string:

		string = string.replace('><span', ' ').replace('</span>', ' ')
		temp0 = string.split('<a')[1]
		temp0 = temp0.split('>')[1]
		temp0 = temp0.split('</a')[0]
		name_link.append(temp0)
		temp = string.split('href="')[1]
		temp = temp.split('"')[0]

		if source == 'rapid7':
			name_link.append('https://www.rapid7.com' + temp)
		if source == 'packetstorm':
			name_link.append('https://www.packetstormsecurity.com' + temp)
		if source == 'securityfocus':
			name_link.append('http://www.securityfocus.com' + temp)
		if source == 'fulldisclosure':
			name_link.append('' + temp)
	else:
		name_link.append(string)
		name_link.append('')
	return name_link

import itertools


def allNames_f(function):
	allNames = [ [] for i in range(len(set(function[0]))) ]
	j = 1
	if function[4] == []:
			allNames = function[1]
	else:
		for (index_x,element_x),i in itertools.product(enumerate(function[4]), range(len(function[3])-1)):	

			#print(str(index_x) + ' PRIMA')
			#print((index_x+1) <= (len(x)))
			
			if function[3][i] == False and allNames[index_x] == [] and allNames[index_x + 1] == []:
			
				if element_x == 0:
					allNames[index_x].append(function[1][element_x])		
			
				elif ( (index_x) <= (len(function[4])-1) ):		
					#print(' DOPO') #str(index_x) +

					allNames[index_x] = (function[1][ j - 1 : (element_x + 1) ])
				if( (index_x + 2) > (len(function[4])) ):
					allNames[index_x + 1] = (function[1][ element_x + 1: ])

				j = element_x + 2

	return allNames


#print(allNames_f(cxsecurity)) -----------------------------------------------



def allScores_f(function):
	allScores = [ [] for i in range(len(set(function[0]))) ]
	j = 1
	if function[4] == []:
		allNames = function[2]
	else:
		for (index_x,element_x),i in itertools.product(enumerate(function[4]), range(len(function[3])-1)):	

			#print(str(index_x) + ' PRIMA')
			#print((index_x+1) <= (len(x)))
	
			if function[3][i] == False and allScores[index_x] == [] and allScores[index_x + 1] == []:
	
				if element_x == 0:
					allScores[index_x].append(function[2][element_x])		
			
				elif ( (index_x) <= (len(function[4])-1) ):		
					#print(' DOPO') #str(index_x) +

					allScores[index_x] = (function[2][ j - 1 : (element_x + 1) ])
				if( (index_x + 2) > (len(function[4])) ):
					allScores[index_x + 1] = (function[2][ element_x + 1: ])

				j = element_x + 2

	return allScores



#	 dates, vulnNames, vulnScores, length, x 
def namesScores_f(function):
	namesScores = [ [] for i in range(len(set(function[0]))) ]
	if function[4] == []:
		namesScores = [function[1], function[2]]
	else:
		for names, scores, i in zip(allNames_f(function), allScores_f(function), range(len(set(function[0]))) ):
			namesScores[i] = names,scores
	return namesScores
	

#print(namesScores_f(projectZero)) #-------------------------------
#print(namesScores_f(securityfocus)) #-----------------------------------------



def prettydate(date):
	
	date = date.replace('January', '01')
	date = date.replace('Jan', '01')
	
	date = date.replace('February', '02')
	date = date.replace('Feb', '02')
	
	date = date.replace('March', '03')
	date = date.replace('Mar', '03')
	
	date = date.replace('April', '04')
	date = date.replace('Apr', '04')
	
	date = date.replace('May', '05')
	
	date = date.replace('June', '06')
	date = date.replace('Jun', '06')
	
	date = date.replace('July', '07')
	date = date.replace('Jul', '07')
	
	date = date.replace('August', '08')
	date = date.replace('Aug', '08')
	
	date = date.replace('September', '09')
	date = date.replace('Sep', '09')
	
	date = date.replace('October', '10')
	date = date.replace('Oct', '10')
	
	date = date.replace('November', '11')
	date = date.replace('Nov', '11')
	
	date = date.replace('December', '12')
	date = date.replace('Dec', '12')
	
	date = date.replace('-', ' ')
	date = date.replace('e', '')
		
	return date
	
def prettydates(function):
	dates = []
	for date in function[0]:
		#print(date.split(' ')[0])
		prettydate(date)
		dates.append(date)
	return sorted(set(dates), reverse = True)

#print (prettydate(cxsecurity))

def reverse_prettydate(date):
	
	#print (date)
	date = prettydate(date)
	#print (date)
	
	edate = date.split(' ')[1]
	bdate = date.split(' ')[0]
	bdate = bdate.replace('01', 'Jan')
	bdate = bdate.replace('02', 'Feb')
	bdate = bdate.replace('03', 'Mar')
	bdate = bdate.replace('04', 'Apr')
	bdate = bdate.replace('05', 'May')
	bdate = bdate.replace('06', 'Jun')
	bdate = bdate.replace('07', 'Jul')
	bdate = bdate.replace('08', 'Aug')
	bdate = bdate.replace('09', 'Sep')
	bdate = bdate.replace('10', 'Oct')
	bdate = bdate.replace('11', 'Nov')
	bdate = bdate.replace('12', 'Dec')
	
	date = bdate + ' ' + edate
	
	return date

def cve(name):
  if 'CVE-' in name:
    cve_vuln = name.split('CVE')[1]
    cve_vuln = 'CVE' + cve_vuln.split(' ')[0]
    cve_vuln = cve_vuln.replace(']', '')
  else:
    cve_vuln = ''
  
  return (cve_vuln)

'''
def get_cvss(cve_vuln):
	
	if cve_vuln != '':
		if os.path.isfile("caches/"+cve_vuln):
			print (cve_vuln + " retrieved from cache...")
			with open("caches/"+cve_vuln,'r') as f:
				return f.read()
		link = []
		#x = str('https://nvd.nist.gov/vuln/detail/CVE-' + cve_vuln)
		x = str('https://nvd.nist.gov/vuln/detail/' + cve_vuln)
		link.append(x) 
		page = getpage(link)		
		bs4Obj = BeautifulSoup(page[0], 'html.parser')
		vuln_score = bs4Obj.find("a", {'href': lambda x: x and x.startswith('/vuln-metrics/cvss/v3-calculator?name')})
		
		if vuln_score is None:
			vuln_score = 'Awaiting Analysis'
			print ('Awaiting Analysis for ' + cve_vuln)

		else:
			vuln_score = vuln_score.get_text()
			vuln_score = vuln_score.replace('\r', '')
			vuln_score = vuln_score.replace('\n', '')
			vuln_score = vuln_score.replace(' ', '')
			with open("caches/"+cve_vuln, 'w') as f:
				f.write(vuln_score)
		return vuln_score


def cvss_scoring(cvss):
	cvss = str(cvss)

	if cvss in ["%.1f" % round((x / float(10)), 1) for x in range(0, 40, 1)]:
		vuln_score = 1 #'Low' + ' (' + cvss + ')'

	elif cvss in ["%.1f" % round((x / float(10)), 1) for x in range(40, 70, 1)]:
		vuln_score = 4 #'Medium' + ' (' + cvss + ')'
			
	elif cvss in ["%.1f" % round((x / float(10)), 1) for x in range(70, 90, 1)]:
		vuln_score = 7 #'High' + ' (' + cvss + ')'

	elif cvss in ["%.1f" % round((x / float(10)), 1) for x in range(90, 100, 1)]:
		vuln_score = 10 #'Critical' + ' (' + cvss + ')'
			
	return vuln_score

def none_cvss_scoring(name):
	
	name = (str(name)).lower()
	
	if any(el in name for el in ['rce','authenticat', 'remote', 'injection', 'vodafone']):
		vuln_score = 10 #'Critical'
		#print (vuln_score)
			
	elif any(el in name for el in ['xss','cross site scripting','cross-site scripting','encryption','cypher','crypto','input validation','traversal','session','permission','privileges','resource','ddos', 'denial of service','url redirection','hard-coded','hard coded']):
		vuln_score = 7 #'High'
		#print(vuln_score)

	elif any(el in name for el in ['csrf','improper','leak','ssrf']):
		vuln_score = 4 #'Medium'
			
	else:
		vuln_score = 1 #'Low'
		
	return vuln_score


def scoring (cve_vuln, name):
	cvss = get_cvss(cve_vuln)
	if str(cvss) != 'Awaiting Analysis' and cvss != None:
		vuln_score = cvss_scoring(cvss)
	else:
		vuln_score = none_cvss_scoring(name)
	#	if cvss == 'Awaiting Analysis':
	#		vuln_score = vuln_score + ' (' + str(cvss) + ')'
	return (vuln_score)
'''


def is_ascii(s):
	return all(ord(c) < 128 for c in s)

def noise(mylist, source):
	
	if any(is_ascii(el)==False for el in mylist):
		no_noise = mylist

	else:
		#print(mylist)
		alist = []
		no_noise = []
		#get el with cve
		for el in mylist:
			#print (el)
			#el.split(',')
			if 'CVE-' in el:
				name = str( get_link (el, source))
				name = eval(name)
				#name = name.split(',')
				#name = name[0][2:-1]
				# same length and startswith the same four twelve
				alist.append(name[0])
			else:
				alist.append(el)
		#print(alist)	
		alist.sort(key=len, reverse=True)
		#print(alist)

		if len(mylist) > 1:
	
			length = [ (len(alist[i]) == len(alist [i+1])) and (alist[i][:4] == alist[i+1][:4]) for i in range(len(alist)-1) ]
	
			if (len(alist[-2]) == len(alist [-1])) and (alist[-2][:4] == alist[-1][:4]):
				length.append(True)
			else:
				length.append(False)
			#print(length)

		else:
			length = [False]


		x = []
		for index,item in enumerate(length):
			if item == False:
				x.append(index)
			
		#print(x)
	
		for index in x:
			no_noise.append(alist[index])

		#print (x)
		#print('X NOISE')
		
	return no_noise



def noise_scores(mylist, x):

	#print(mylist)
	no_noise = mylist

	if len(mylist) > 1:

		no_noise = []
		#alist = []
		#print(x)
		for pos in x:
			#print (pos)
			no_noise.append(str(mylist[int(float(pos))]))

	return no_noise

def realDict_f(function):
	realDict = {}
	if function == 'projectZero':
		realDict[function[0]] = namesScores_f(function) #----------------------------------------------- just one element instead of two!!!!
	elif function[4] == []:
		
		mylist = prettydates(function)

		#for date, el in zip(prettydates(function), namesScores_f(function)):
			#print(date)
			#print(function()[0])

		realDict[reverse_prettydate(mylist[0])] = namesScores_f(function) #el
	else:
		for date,el in zip(prettydates(function), namesScores_f(function)): #		for date,el in zip(sorted(set(function[0])), namesScores_f(function)):
			#print (date)
			#print ('\n')
			realDict[reverse_prettydate(date)] = el
	return realDict


def save_scraped():
	past = db.session.query(vulns_blogs.name)
	mypast = [el.name for el in past]
	body = [str(mypast)[1:-1].replace('"', '')]
	real_past = []
	for el in body:
		if el:
			real_past.append(str(el[0]))

	i = 0
	print (repr(real_past))
	for dictionary in allDict:
		for key, value in dictionary.items():
			names = value[0]
			scores = value[1]
			for vname, vscore in zip(names, scores):
				if (vname in real_past) == False:
					ascore = str(scoring_functions.scoring(cve(vscore), vname))
					if not ascore.startswith('Low'):
						temp = allSource[i]
						vuln_object = vulns_blogs(name = str(get_link(vname, temp)), date = (key + ' ' + str(now.year)), my_cve = cve(vname), score = ascore, source = temp)
						exists = db.session.query(vulns_blogs).filter_by(name = str(get_link(vname, temp)), date = (key + ' ' + str(now.year)), my_cve = cve(vname), score = ascore, source = temp).first() is not None
						#exists=False
						if exists == False:
							if (int(ascore) == 10):
								final_name = []
								final_name.append(vname)
								final_name.append(temp)
								single_vuln = {'name': get_link(vname, temp) ,'score': ascore,'url': temp,'date':datetime.datetime.now(),'cve': cve(vname),'source': temp}
								secbot = telegrambot.BotHandler("351082352:AAHLBZW4ObbsMVHh4lrcwZOVHmvKsfyM59E")
								secbot.push_update(db,single_vuln)
							db.session.add(vuln_object)
		i += 1

	db.session.commit()


allDict = [realDict_f(fulldisclosure), realDict_f(rapid7), realDict_f(securityfocus), realDict_f(packetstorm)]
allSource = ['fulldisclosure', 'rapid7', 'securityfocus', 'packetstorm']
