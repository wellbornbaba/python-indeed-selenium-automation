from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import threading
import os
import pandas as pd

keywords = 'students' #keywords to search for
location = 'usa' #location to search in
no_of_pages = 50 #number of pages you want to parse NOTE it has to be in 10, 20, 30 and so on
savefilename = 'JobResults' #name of excel/html sheet you want to save with with no extension
savepath_to = os.path.join(os.getcwd(), savefilename)

class IndeedAutomation():

	def __init__(self,  keywords, location, no_of_pages, savepath_to):
		self.browser = webdriver.Chrome('driver/chromedriver.exe')
		self.keywords = keywords
		self.location = location
		self.pageto_scrap = no_of_pages
		# do the processing
		t1 = threading.Thread(name='Start Automation', target=self.run)
		t1.start()

	def run(self):
		pages = []
		keywords = self.keywords.replace(' ', '+')
		location = self.location.replace(' ', '+')

		try:
			count = 0
			tablecount = 1
			table = ''
			xls = pd.DataFrame(columns=['Job Title', 'Company Name', 'Address', 'Links'])
			data = {}
			#get the pages to process done and store in pages
			while count < self.pageto_scrap:
				url = f'https://www.indeed.com/jobs?q={keywords}&l={location}&start={count}'
				pages.append(url)
				count += 10

			#start processing of all the pages each
			for page in pages:
				self.browser.get(page)
				#print(page)
				#wait for the browser page to load
				wait = WebDriverWait(self.browser, 5)
				#wait until the target class is loaded and found
				wait.until(EC.presence_of_element_located((By.ID, 'resultsCol')))
				#if successfully loaded store it to pagecontents variable
				pagecontents = self.browser.find_elements_by_id('resultsCol')
				for itemlists in pagecontents:
					for itemdiv in itemlists.find_elements_by_css_selector('div.jobsearch-SerpJobCard'):
						titlediv = itemdiv.find_elements_by_css_selector('div.title')[0]
						jobtitle = titlediv.find_elements_by_css_selector('a')[0].get_attribute('title')
						joblink = titlediv.find_elements_by_css_selector('a')[0].get_attribute('href')
						locationss = itemdiv.find_elements_by_css_selector('div.sjcl')[0]

						try:
						    jobcompanyname = locationss.find_element_by_class_name('turnstileLink').text
						except:
							jobcompanyname = locationss.find_element_by_class_name('company').text

						jobaddress = locationss.find_element_by_class_name('location').text

						data['Address'] = jobaddress
						data['Job Title'] = jobtitle
						data['Company Name'] = jobcompanyname
						data['Links'] = joblink

						table += f'<tr><td>{tablecount}</td><td>{jobtitle}</td><td>{jobcompanyname}</td><td>{jobaddress}</td><td><a href="{joblink}" target="_blank">{joblink}</a></td><tr>'

						#let start processing
						xls = xls.append(data, ignore_index=True)
						xls.index += 1
						tablecount +=1

				basename = os.path.splitext(savepath_to)[0]
				#save as excel
				xls.to_excel(basename + '.xlsx')
				#save as html
			html = '''<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.3/css/bootstrap.min.css"  >
<title>Result Found</title>
</head>
<body>
<div class="container">
  <h3>Result Found </h2>
  <table class="table table-striped table-sm table-hover table-responsive">
  <thead class="thead-light">
  <tr>
     <th>#</th>
     <th>Job Title</th>
      <th>Company Name</th>
      <th> Address </th>
	  <th>Links</th>
    </tr>
  </thead>
  <tbody>'''
			html += table
			html +='''</tbody>
</table>

</div>
</body>
</html>'''
			#save html file
			try:
				dfileToSave = basename + '.html'
				with open(dfileToSave, 'w', encoding='utf-8') as fp:
					fp.write(html.replace('\r\n', '\n'))
					fp.close()  # clean up

			except Exception:
				print('Error occurred can not save html file')

		except TimeoutException:
			print('time out')

		finally:
			self.browser.quit()


if __name__ == '__main__':
	IndeedAutomation(keywords, location, no_of_pages, savepath_to)
