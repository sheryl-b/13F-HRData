#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests

from datetime import datetime 
import time

from selenium import webdriver


# In[ ]:


from selenium.webdriver.chrome.options import Options
options = Options()
options.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"
#driver = webdriver.Chrome(chrome_options=options, executable_path="E:/chromedriver.exe", )


# In[ ]:


pd.set_option('display.float_format', lambda x:'%.2f' % x)
today = pd.to_datetime("today").strftime("%Y%m%d")

# Folders and links
directory = r'E:\01.0 Corporation\2023\01.0 Investing\1.0 Hedge Funds\\'
chrome_path = r"E:\chromedriver.exe"
#chrome_path = r"C:\Users\gs\Desktop\chrome-win32\chrome-win32\chrome.exe"


# In[ ]:


# This functions uses filing date and convertes it into date of the month end for which 13F was filed
def date_calc(frame):
    if frame['MONTH'] <= 3:
        s = frame['YEAR'] - 1
        s = "% s" % s
        return s + "-12-31"
    elif frame['MONTH'] <= 6:
        s = frame['YEAR']
        s = "% s" % s
        return s + "-03-31"
    elif frame['MONTH'] <= 9:
        s = frame['YEAR']
        s = "% s" % s
        return s + "-06-30"
    else: 
        s = frame['YEAR']
        s = "% s" % s
        return s + "-09-30"


# In[ ]:


# Create DataFrame for use later in the sections
df_personal = pd.read_csv(directory)
df_master = pd.DataFrame()

# Create an array to loop through List of CIK
iD = ['1649339']
# Scion: 1649339
#783412	DAILY JOURNAL CORP
#1067983	BERKSHIRE HATHAWAY INC


# In[ ]:


df_personal.info()


# In[ ]:


type(iD)


# In[ ]:


for i, check in enumerate(iD):
    url = "https://www.sec.gov/cgi-bin/browse-edgar?CIK={}&owner=exclude&action=getcompany&type=13F-HR".format(check)
    print(url)


# 	2017-02-14 
#     
# CAS Investment Partners - 	2018-02-14 - Error out of range
# Conifer Management, L.L.C.- 2020-02-14
# Dorsey Asset Management - 	2017-01-17

# In[ ]:


# Loop through the CIK list one by one to create a final Dataframe
i=0

url = ""

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}


driver = webdriver.Chrome(chrome_options=options,executable_path=chrome_path)

for i, check in enumerate(iD):
    url = ""
    df_filings = pd.DataFrame()
    
    #if i<1: # Remove after testing
    url = "https://www.sec.gov/cgi-bin/browse-edgar?CIK={}&owner=exclude&action=getcompany&type=13F-HR".format(check)
    driver.get(url)
    time.sleep(2)
    #response = requests.get(url, headers= headers)
    #time.sleep(10)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    tags = soup.findAll('a', id="documentsbutton")

    # Get filling dates
    #url = "https://www.sec.gov/cgi-bin/browse-edgar?CIK={}&owner=exclude&action=getcompany&type=13F-HR".format(check)
    #time.sleep(5)
    #df_filings = pd.read_html(response.text)
    df_filings = pd.read_html(driver.page_source)
    time.sleep(2)
    df_filings = df_filings[-1]
    dt = df_filings['Filing Date']


    # List for all urls and their filing date
    days_url = []
    filingDT = []

    # Specify based on how many links need to be downloaded
    j = 0
    for j in range(3): 
        days_url.append('https://www.sec.gov'+tags[j]['href'])
        filingDT.append(dt[j])
    print(days_url)
    
    #days_url = days_url[6:]
    #filingDT = filingDT[6:]
    
    k = 0
    for k, item in enumerate(days_url):
        
        print(item)
    
        driver.get(item)
        #index = pd.read_html(item)
        index = pd.read_html(driver.page_source)
        time.sleep(2)
        index = index[0]
        index = index[(index['Document'].str.contains('.html')) & (index['Type'].str.contains('INFORMATION TABLE'))]
        try:
            index = index['Document'].iloc[0]
        except:
            index = ''
        index = index.replace('html','xml')
        s = item.replace(item.rsplit('/', 1)[-1],'xslForm13F_X01/')
        s = s+index
        s = "% s" % s
        print(s)
        # Create a DataFrame for each run and append to the df_master
        DF_13F = pd.DataFrame()         #Reset DataFrame for each run
        #time.sleep(2)
        #response3 = requests.get(s, headers= headers)
        #DF_13F = pd.read_html(s)
        driver.get(s)
        time.sleep(2)
        DF_13F = pd.read_html(driver.page_source)
        DF_13F = DF_13F[-1]
        DF_13F = DF_13F.iloc[2:]
        new_header = DF_13F.iloc[0]
        DF_13F.columns = new_header
        DF_13F = DF_13F.iloc[1:]
        DF_13F['CIK'] = check
        DF_13F['FILING_DATE'] = filingDT[k]
        df_master = df_master.append(DF_13F)

print('COMPLETED!') 


# In[ ]:


driver.close()


# In[ ]:


df_master


# In[ ]:


df_master.to_csv(directory+today+'masterfindings.csv', index = False)

