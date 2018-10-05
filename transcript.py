import requests
import getpass
from lxml import html
import re
#from pprint import pprint
import datetime
import time
import argparse

# College names and codes pulled from the CunyFirst website
college_codes = {'BAR01': 'Baruch College', 'BMC01': 'Borough of Manhattan CC', 'BCC01': 'Bronx CC', 'BKL01': 'Brooklyn College', 'CTY01': 'City College', 'CSI01': 'College of Staten Island', 'GRD01': 'Graduate Center', 'NCC01': 'Guttman CC', 'HOS01': 'Hostos CC', 'HTR01': 'Hunter College', 'JJC01': 'John Jay College', 'KCC01': 'Kingsborough CC', 'LAG01': 'LaGuardia CC', 'LEH01': 'Lehman College', 'MHC01': 'Macaulay Honors College', 'MEC01': 'Medgar Evers College', 'NYT01': 'NYC College of Technology', 'QNS01': 'Queens College', 'QCC01': 'Queensborough CC', 'SOJ01': 'School of Journalism', 'SLU01': 'School of Labor&Urban Studies', 'LAW01': 'School of Law', 'MED01': 'School of Medicine', 'SPS01': 'School of Professional Studies', 'SPH01': 'School of Public Health', 'UAPC1': 'University Processing Center', 'YRK01': 'York College'}


def login(session,username,password):
	print('[DEBUG] Logging in...')
	session.get('https://home.cunyfirst.cuny.edu')

	# Log in by posting to the url that accepts the username and password
	url = 'https://ssologin.cuny.edu/oam/server/auth_cred_submit'
	data = {
		'usernameH': f'{username}@login.cuny.edu',
		'username': username,
		'password': password,
		'submit': ''
	}
	# post the data to the url
	r = session.post(url,data=data)

	# url is the main index, the purpose of this get is to redirect us to allow us to validate the credentials
	url = 'https://hrsa.cunyfirst.cuny.edu/psc/cnyhcprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL?FolderPath=PORTAL_ROOT_OBJECT.HC_SSS_STUDENT_CENTER&IsFolder=false&IgnoreParamTempl=FolderPath%2cIsFolder&PortalActualURL=https%3a%2f%2fhrsa.cunyfirst.cuny.edu%2fpsc%2fcnyhcprd%2fEMPLOYEE%2fHRMS%2fc%2fSA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL&PortalContentURL=https%3a%2f%2fhrsa.cunyfirst.cuny.edu%2fpsc%2fcnyhcprd%2fEMPLOYEE%2fHRMS%2fc%2fSA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL&PortalContentProvider=HRMS&PortalCRefLabel=Student%20Center&PortalRegistryName=EMPLOYEE&PortalServletURI=https%3a%2f%2fhome.cunyfirst.cuny.edu%2fpsp%2fcnyepprd%2f&PortalURI=https%3a%2f%2fhome.cunyfirst.cuny.edu%2fpsc%2fcnyepprd%2f&PortalHostNode=EMPL&NoCrumbs=yes&PortalKeyStruct=yes'
	
	r = session.get(url)	# get the url
	
	tree = html.fromstring(r.text)	# parse the html DOM

	encquery = tree.xpath('//*[@name="enc_post_data"]/@value')[0]	# get the first validation hash

	url = 'https://ssologin.cuny.edu/obrareq.cgi'					# set the url
	data = {
		'enc_post_data' : encquery
	}

	r = session.post(url,data=data)									# post the hash to the site

	tree = html.fromstring(r.text)									# parse the html DOM
	encreply = tree.xpath('//*[@name="enc_post_data"]/@value')[0]	# get the second validation hash

	url = 'https://hrsa.cunyfirst.cuny.edu/obrar.cgi'				# set the url
	data = {
		'enc_post_data' : encreply
	}
	r = session.post(url,data=data)									# post the hash to the site

	# set the url to the main index of cunyfirst

	url = 'https://hrsa.cunyfirst.cuny.edu/psc/cnyhcprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL?FolderPath=PORTAL_ROOT_OBJECT.HC_SSS_STUDENT_CENTER&IsFolder=false&IgnoreParamTempl=FolderPath%2cIsFolder&PortalActualURL=https%3a%2f%2fhrsa.cunyfirst.cuny.edu%2fpsc%2fcnyhcprd%2fEMPLOYEE%2fHRMS%2fc%2fSA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL&PortalContentURL=https%3a%2f%2fhrsa.cunyfirst.cuny.edu%2fpsc%2fcnyhcprd%2fEMPLOYEE%2fHRMS%2fc%2fSA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL&PortalContentProvider=HRMS&PortalCRefLabel=Student%20Center&PortalRegistryName=EMPLOYEE&PortalServletURI=https%3a%2f%2fhome.cunyfirst.cuny.edu%2fpsp%2fcnyepprd%2f&PortalURI=https%3a%2f%2fhome.cunyfirst.cuny.edu%2fpsc%2fcnyepprd%2f&PortalHostNode=EMPL&NoCrumbs=yes&PortalKeyStruct=yes'
	r = session.get(url)											# navigate to main index
	print('[DEBUG] Successfully logged in!')
	return r


def navigate(session, school):
	print('[DEBUG] Beginning navigation to transcript section...')
	# go to transcript request page without properly navigating, throw an error and get the values of the hidden form
	url = 'https://hrsa.cunyfirst.cuny.edu/psc/cnyhcprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_TSRQST_UNOFF.GBL?Page=SSS_TSRQST_UNOFF&Action=A&EMPLID=&TargetFrameName=None'
	r = session.get(url)
	#print(r.text)
	tree = html.fromstring(r.text)					# parse the html DOM
	data = {}										# store the key-value pairs for the form here
	for el in tree.xpath('//input'):
		# iterate through the hidden form
		name = ''.join(el.xpath('./@name'))
		value = ''.join(el.xpath('./@value'))
		#print(name,value)
		data[name] = value
	
	# manually make some changes to the form
	data['ICAJAX'] = '1'
	data['ICNAVTYPEDROPDOWN'] = '1'
	data['ICYPos'] = '144'
	data['ICStateNum'] = '1'
	data['ICAction'] = 'DERIVED_SSS_SCR_SSS_LINK_ANCHOR4'
	data['ICBcDomData'] = 'C~HC_SSS_STUDENT_CENTER~EMPLOYEE~HRMS~SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL~UnknownValue~Student Center~UnknownValue~UnknownValue~https://home.cunyfirst.cuny.edu/psp/cnyepprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL~UnknownValue'
	data['DERIVED_SSS_SCL_SSS_MORE_ACADEMICS'] = '9999'
	data['DERIVED_SSS_SCL_SSS_MORE_FINANCES'] = '9999'
	data['CU_SF_SS_INS_WK_BUSINESS_UNIT'] = school
	data['DERIVED_SSS_SCL_SSS_MORE_PROFILE'] = '9999'

	# set url to student center menu
	url = 'https://hrsa.cunyfirst.cuny.edu/psc/cnyhcprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL'
	r = session.post(url,data=data)					# post data to student center menu
	print('[DEBUG] 1/5 requests completed...')

	# navigate to the academics page
	session.get('https://hrsa.cunyfirst.cuny.edu/psc/cnyhcprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_MY_ACAD.GBL?Page=SSS_MY_ACAD&Action=U&ExactKeys=Y&TargetFrameName=None')
	
	# modify form for next stage
	data['ICStateNum'] = '3'
	data['ICAction'] = 'DERIVED_SSSACA2_SS_UNOFF_TRSC_LINK'
	data['ICYPos'] = '95'
	data['DERIVED_SSTSNAV_SSTS_MAIN_GOTO$7$'] = '9999'
	data['DERIVED_SSTSNAV_SSTS_MAIN_GOTO$8$'] = '9999'

	# go to transcript request page by posting data saying we want to go
	r = session.post(url, data = data)
	print('[DEBUG] 2/5 requests completed...')

	url = re.search(r'document\.location=\'(https://hrsa.cunyfirst.cuny.edu/psc/cnyhcprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_TSRQST_UNOFF\.GBL\?Page=SSS_TSRQST_UNOFF&Action=A&EMPLID=\d+&TargetFrameName=None)',r.text).group(1)

	session.get(url)			# actually go to transcript request page


	# modify the form data to say we declared a college to pick from
	data['ICStateNum'] = '5'
	data['ICAction'] = 'SA_REQUEST_HDR_INSTITUTION'
	data['SA_REQUEST_HDR_INSTITUTION'] = school
	data['ICYPos'] ='115'
	data['ICBcDomData'] = 'C~HC_SSS_TSRQST_UNOFF_GBL~EMPLOYEE~HRMS~SA_LEARNER_SERVICES.SSS_TSRQST_UNOFF.GBL~UnknownValue~View Unofficial Transcript~UnknownValue~UnknownValue~https://home.cunyfirst.cuny.edu/psp/cnyepprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_TSRQST_UNOFF.GBL~UnknownValue*C~HC_SSS_STUDENT_CENTER~EMPLOYEE~HRMS~SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL~UnknownValue~Student Center~UnknownValue~UnknownValue~https://home.cunyfirst.cuny.edu/psp/cnyepprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL~UnknownValue'
	data['DERIVED_SSTSRPT_TSCRPT_TYPE3'] = ''
	data['ptus_componenturl'] = 'https://hrsa.cunyfirst.cuny.edu/psp/cnyhcprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_TSRQST_UNOFF.GBL'
	#pprint(data)
	# tell it we picked that college
	r = session.post(url,data=data)
	print('[DEBUG] 3/5 requests completed...')
	#pprint(data)
	#print(r.text)

	# tell it we selected "Student Unofficial Transcript"
	data['ICStateNum'] = '6'
	r = session.post(url,data=data)
	print('[DEBUG] 4/5 requests completed...')
	#pprint(data)
	#print(r.text)

	# submit our final request to view report
	data['ICStateNum'] = '7'
	data['ICAction'] = 'GO'
	data['DERIVED_SSTSRPT_TSCRPT_TYPE3'] = 'STDNT'

	r = session.post(url,data=data)
	print('[DEBUG] 5/5 requests completed...')
	print('[DEBUG] Retrieving PDF from URL...')
	#pprint(data)
	#print(r.text)

	# the response contains the url of the transcript. extract with regex
	pdfurl = re.search(r'window.open\(\'(https://hrsa\.cunyfirst\.cuny\.edu/psc/.*\.pdf)',r.text).group(1)

	# get the resource at the extracted url, which is the pdf of the transcript
	r = session.get(pdfurl)
	print('[DEBUG] Successfully retrieved PDF!')
	
	# save the retrieved resource as a pdf on the local machine
	now = datetime.datetime.now()
	timestamp = now.strftime('Transcript_%m-%d-%Y_%H%M.pdf')

	with open(timestamp,'wb') as f:
		f.write(r.content)

	print(f'[DEBUG] Transcript saved as {timestamp}')

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Specify commands for CUNY Transcript Retriever v2.0')
	parser.add_argument('--school',default="QNS01")
	parser.add_argument('--list-codes',action='store_true')
	args = parser.parse_args()


	session = requests.Session()
	print('CUNY Transcript Retriever v2.0 by @ericshermancs')
	if args.list_codes:
		print('LIST OF COLLEGES AND CODES:')
		for code in college_codes:
			print(college_codes[code],':',code)

		exit(0)

	print(f'[DEBUG] College to retrieve transcript from: {college_codes[args.school.upper()]}')
	username = input("Enter username: ")
	password = getpass.getpass("Enter password: ")

	start = time.time()
	login(session,username,password)
	navigate(session,args.school.upper())
	end = time.time()
	print(f'[DEBUG] Program completed in {end-start} seconds')
