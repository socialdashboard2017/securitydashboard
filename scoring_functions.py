import os
import os.path
import requests
from bs4 import BeautifulSoup

def getpage(alist):
  #return [ urllib.request.urlopen(url) for url in alist  ]
  return [ requests.get(url).text for url in alist  ]

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