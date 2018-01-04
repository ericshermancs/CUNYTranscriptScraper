#!/usr/bin/env python3
import os, sys, getpass, time, datetime, pip
from zipfile import ZipFile
from io import BytesIO
from urllib.request import urlopen

def install(package):
	if __name__ == '__main__':
		pip.main(['install', package])

try:
	import requests
except:
	install('requests')
	import requests

try:
	from splinter import Browser
except:
	install('splinter')
	from splinter import Browser

try:
	from selenium.webdriver.chrome.options import Options
except:
	install('selenium')
	from selenium.webdriver.chrome.options import Options
if sys.platform == 'linux' or sys.platform == 'linux2':
	try:
		from pyvirtualdisplay import Display
	except:
		install('pyvirtualdisplay')
		from pyvirtualdisplay import Display


def init_browser():
	working_directory = os.getcwd()
	chrome_options = Options()
	#chrome_options.add_argument("--headless")
	chrome_options.add_argument("--window-size=600,500")
	
	chrome_options.add_experimental_option('prefs', {
    "plugins.plugins_list": [{"enabled":False,"name":"Chrome PDF Viewer"}],
    "download": {
        "prompt_for_download": False,
        "default_directory"  : working_directory # i think chrome automatically makes this directory when saving?
	    }
	})

	browser = Browser('chrome', options=chrome_options, headless=False)
	return browser

def login(browser):
	print('Visiting homepage...')
	browser.visit("http://home.cunyfirst.cuny.edu")
	
	username_field = browser.find_by_id(id='CUNYfirstUsernameH').first
	password_field = browser.find_by_id(id='CUNYfirstPassword').first

	creds = []

	if not os.path.isfile('credentials.txt'):
		print('FOR AUTOMATIC LOGIN, PLEASE ENTER YOUR CREDENTIALS IN credentials.txt')
		creds.append(input('Username: ').strip())
		creds.append(getpass.getpass('Password: ').strip())
	else:
		with open('credentials.txt','r+') as f:
			for line in f:
				creds.append(line.strip())

	if '@login.cuny.edu' not in username:
		creds[0] += '@login.cuny.edu' #so user doesn't have to worry about whether to enter it or not
	username_field.type(creds[0])
	password_field.type(creds[1])
	print('Logging in...')
	submit_login = browser.find_by_id(id='submit').first
	submit_login.click()
	if browser.url == 'https://ssologin.cuny.edu/unrecognized-credentials.html?p_error_code=OAM-5':
		print('Invalid credentials. Exiting program...')
		exit(0)
	browser.visit("http://home.cunyfirst.cuny.edu") # sometimes there are weird errors


def navigate(browser):
	print('Visiting \"Student Center\"...')
	browser.click_link_by_text('Student Center')
	while browser.is_element_not_present_by_id('ptifrmtgtframe'): # wait for frame
		time.sleep(.1)

	with browser.get_iframe('ptifrmtgtframe') as frame:
		print('Visiting \"My Academics\"...')
		frame.click_link_by_text('My Academics')

		while frame.is_element_not_present_by_text('View my unofficial transcript'): #wait for it to show up
			time.sleep(.1)
		print('Visiting \"View my unofficial transcript\"...')
		frame.click_link_by_text('View my unofficial transcript') 

		while frame.is_element_not_present_by_id('SA_REQUEST_HDR_INSTITUTION'):
			time.sleep(.1)
		print("Entering transcript request...")
		acad_inst = frame.find_by_id('SA_REQUEST_HDR_INSTITUTION').first


		cuny_college_codes = {
		'Baruch College' : 'BAR01',
		'Borough of Manhattan CC' : 'BMC01',
		'Bronx CC' : 'BCC01',
		'Brooklyn College' : 'BKL01',
		'CUNY School of Law' : 'LAW01',
		'CUNY School of Medicine' : 'MED01',
		'Cuny School of Public Health' : 'SPH01',
		'City College' : 'CTY01',
		'College of Staten Island' : 'CSI01',
		'Guttman CC' : 'NCC01',
		'Hostos CC' : 'HOS01',
		'Hunter College' : 'HTR01',
		'John Jay College' : 'JJC01',
		'Kingsborough CC' : 'KCC01',
		'LaGuardia CC' : 'LAG01',
		'Lehman College' : 'LEH01',
		'Medgar Evers College' : 'MEC01',
		'NYC College of Technology' : 'NYT01',
		'Queens College' : 'QNS01',
		'Queensborough CC' : 'QCC01',
		'School of Professional Studies' : 'SPS01',
		'The Graduate Center' : 'GRD01',
		'University Admissions' : 'UAPC1',
		'York College' : 'YRK01'
		}

		acad_inst.select('QNS01') # change based on cuny


		while True:
			try:
				rep_type = frame.find_by_id('DERIVED_SSTSRPT_TSCRPT_TYPE3').first
				rep_type.select('STDNT')
				break
			except:
				pass
		print('Selecting \"View Report\"...')
		time.sleep(2)
		while True:
			try:
				frame.click_link_by_id('GO')
			except:
				break
			time.sleep(.1)

def renamePDF(browser):
	while not os.path.isfile('SSR_TSRPT.pdf'):
		time.sleep(.1)
	while os.path.getsize('SSR_TSRPT.pdf') == 0:
		time.sleep(.1)
	now = datetime.datetime.now()
	timestamp = now.strftime('Transcript_%m-%d-%Y_%H%M.pdf')
	os.rename('SSR_TSRPT.pdf',timestamp)
	while os.path.getsize(timestamp) == 0:
		time.sleep(.1)
	print('Transcript successfully downloaded as {}'.format(timestamp))



def install_chromedriver(): # untested
	if sys.platform == 'linux' or sys.platform == 'linux2': #linux ftw
		if not os.path.isfile('/usr/bin/chromedriver'):
			print('Chrome driver is missing...')
			print('Downloading chrome driver...')
			zipurl = 'https://chromedriver.storage.googleapis.com/2.34/chromedriver_linux64.zip'
			with urlopen(zipurl) as zipresp:
				with ZipFile(BytesIO(zipresp.read())) as zfile:
					zfile.extractall('/usr/bin')
			print('Done downloading chrome driver')

	elif sys.platform == 'darwin': # mac
		if not os.path.isfile('/usr/bin/chromedriver'):
			print('Chrome driver is missing...')
			print('Downloading chrome driver...')
			zipurl = 'https://chromedriver.storage.googleapis.com/2.34/chromedriver_mac64.zip'
			with urlopen(zipurl) as zipresp:
				with ZipFile(BytesIO(zipresp.read())) as zfile:
					zfile.extractall('/usr/bin')
			print('Done downloading chrome driver')

	elif sys.platform == 'win32':
		if not os.path.isfile(r'C:\Windows\chromedriver.exe'):
			print('Chrome driver is missing...')
			print('Downloading chrome driver...')
			zipurl = 'https://chromedriver.storage.googleapis.com/2.34/chromedriver_win32.zip'
			with urlopen(zipurl) as zipresp:
				with ZipFile(BytesIO(zipresp.read())) as zfile:
					zfile.extractall('C:\Windows')

			print('Done downloading chrome driver')
		
def main():
	if sys.platform == 'linux' or sys.platform == 'linux2':
		display = Display(visible=0,size=(800,1200))
		display.start()

	install_chromedriver()

	browser = init_browser()

	print('CUNY Transcript Web Scraper by @ericshermancs')
	#start = time.time()
	try:
		login(browser)
		navigate(browser)
		renamePDF(browser)
		#end = time.time()
		#print('Execution time:',end-start,'seconds')
	except:
		pass
	try:
		browser.quit()
	except:
		pass
	if sys.platform == 'linux' or sys.platform == 'linux2':
		try:
			display.stop()
		except:
			pass
	

if __name__ == '__main__':
	main()
