import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pyautogui
from tkinter import filedialog, Tk
import tkinter.messagebox as tm
import os
from urllib.request import urlopen
import pandas as pd
import numpy as np
import requests
import csv
import datetime

import login

# pyinstaller --onefile --windowed --icon=app.ico scrapejob_v07.py

class EasyApplyBot:

    MAX_APPLICATIONS = 3000

    def __init__(self,username,password, language, position, location): #, resumeloctn):

        dirpath = os.getcwd()
        #print("current directory is : " + dirpath)
        #print(dirpath + "\chromedriver.exe")
        #foldername = os.path.basename(dirpath)
        #print("Directory name is : " + foldername)

        self.language = language
        self.options = self.browser_options()
        #self.browser = webdriver.Chrome(chrome_options=self.options)
        #self.browser = webdriver.Chrome(executable_path = "C:/chromedriver_win32/chromedriver.exe")
        self.browser = webdriver.Chrome(chrome_options=self.options, executable_path = dirpath + "\chromedriver.exe")
        self.start_linkedin(username,password)


    def browser_options(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("user-agent=Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393")
        #options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        #options.add_argument('--disable-gpu')
        #options.add_argument('disable-infobars')
        options.add_argument("--disable-extensions")
        return options

    def start_linkedin(self,username,password):
    #    self.browser.get("https://linkedin.com/uas/login")
    #def login(driver): #, username, password):
        print("\nLogging in.....\n \nPlease wait :) \n ")
        self.browser.get("https://www.linkedin.com/")
        try:
            user_field = self.browser.find_element_by_class_name("login-email")
            pw_field = self.browser.find_element_by_class_name("login-password")
            login_button = self.browser.find_element_by_id("login-submit")
            user_field.send_keys(username)
            user_field.send_keys(Keys.TAB)
            time.sleep(1)
            pw_field.send_keys(password)
            time.sleep(1)
            login_button.click()
        except TimeoutException:
            print("TimeoutException! Username/password field or login button not found on glassdoor.com")

    def wait_for_login(self):
        if language == "en":
             title = "Sign In to LinkedIn"
        elif language == "es":
             title = "Inicia sesión"
        elif language == "pt":
             title = "Entrar no LinkedIn"

        time.sleep(1)

        while True:
            if self.browser.title != title:
                print("\nStarting LinkedIn bot\n")
                break
            else:
                time.sleep(1)
                print("\nPlease Login to your LinkedIn account\n")

    def fill_data(self):
        self.browser.set_window_size(0, 0)
        self.browser.set_window_position(2000, 2000)
        os.system("reset")

        self.position = position
        self.location = "&location=" + location
        #self.resumeloctn = resumeloctn
        #print(self.resumeloctn)

    def start_apply(self):
        self.fill_data()
        self.applications_loop()

    def applications_loop(self):

        list1=pd.DataFrame(columns=['time', 'url', 'position', 'Company', 'location','date', 'description',
                            'Seniority level', 'Industry', 'Employment type', 'Job function', 'Company Info'], index=np.arange(0,10000) )

        count_application = 1
        count_job = 0
        jobs_per_page = 0

        os.system("reset")

        print("\nLooking for jobs.. Please wait..\n")

        self.browser.set_window_position(0, 0)
        self.browser.maximize_window()
        self.browser, _ = self.next_jobs_page(jobs_per_page)
        print("\nLooking for jobs.. Please wait..\n")

        submitButton = self.browser.find_element_by_class_name("jobs-search-dropdown__trigger-icon")
        submitButton.click()
        submitButton = self.browser.find_element_by_class_name("jobs-search-dropdown__option")
        submitButton.click()

        while count_application < self.MAX_APPLICATIONS:
            # sleep to make sure everything loads, add random to make us look human.
            time.sleep(random.uniform(3.5, 6.9))
            self.load_page(sleep=1)
            page = BeautifulSoup(self.browser.page_source, 'lxml')

            jobs = self.get_job_links(page)

            if not jobs:
                print("Jobs not found")
                break

            for job in jobs:

                count_job += 1
                job_page = self.get_job_page(job)

                #position_number = str(count_job + jobs_per_page)
                position_number = str(count_application)
                print(f"\nPosition {position_number}:\n {self.browser.title} \n") # {string_easy} \n")

                now = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                list1.iloc[count_job,0] = str(now)
                list1.iloc[count_job,1] = ('https://www.linkedin.com'+job)

                #Title, Company, temp = self.browser.title.split('|')
                #list1.iloc[count_job,1] = Title
                #list1.iloc[count_job,2] = Company

                #button view more
                try :
                    self.browser.find_element_by_class_name('view-more-icon').click()
                    self.load_page(sleep=1)
                except:
                    print('******* Job not valid *******\n')

                soup = BeautifulSoup (self.browser.page_source,"lxml")

                #Title, Company, location and date
                findall = soup.find("div", {"class": 'jobs-details-top-card__content-container mt6 pb5'})
                try:
                    list1.iloc[count_job,2] = findall.find("h1").text.strip()
                    list1.iloc[count_job,3] = findall.find("h3").text.strip().split('\n')[1].strip()
                except:
                    list1.iloc[count_job,2] = None
                    list1.iloc[count_job,3] = None

                try:
                    span = findall.find("span", {"class": 'jobs-details-top-card__bullet'})
                    list1.iloc[count_job,4] = span.text.strip()
                except:
                    list1.iloc[count_job,4] = None

                try:
                    span = findall.find("span", string = 'Posted Date')
                    list1.iloc[count_job,5] = span.nextSibling.strip()
                except:
                    list1.iloc[count_job,5] = None


                # job description
                findall = soup.find("div", {"class": "jobs-box__html-content jobs-description-content__text t-14 t-black--light t-normal"})

                try:
                    span=findall.find('span')
                    description = span.text.strip()
                    list1.iloc[count_job,6] = description
                except:
                    list1.iloc[count_job,6] = None

                # Job details
                findall = soup.findAll("div", {"class": 'jobs-box__group'})

                for div in findall:

                    try:
                        text = div.text.strip().split('\n')

                        if text [0] == 'Seniority Level' :
                            list1.iloc[count_job,7] = div.find('p').text.strip().replace('\n', ', ')
                        if text [0] == 'Industry' :
                            list1.iloc[count_job,8] = div.find('ul').text.strip().replace('\n', ', ')
                        if text [0] == 'Employment Type' :
                            list1.iloc[count_job,9] = div.find('p').text.strip().replace('\n', ', ')
                        if text [0] == 'Job Functions' :
                            list1.iloc[count_job,10] = div.find('ul').text.strip().replace('\n', ', ')
                    except:
                        list1.iloc[count_job,7] = None
                        list1.iloc[count_job,8] = None
                        list1.iloc[count_job,9] = None
                        list1.iloc[count_job,10] = None



                # company description
                try:
                    findall = self.browser.find_element_by_id('company-description-text')
                    description = findall.text.strip()
                    list1.iloc[count_job,11] = description
                except:
                    list1.iloc[count_job,11] = None

                # write to file
                data = list1.iloc[count_job,:]
                with open('output.csv', 'a', newline='') as f:
                    try:
                        writer = csv.writer(f)
                        writer.writerow(data)
                        print('Job added to output.csv')
                    except:
                        print('*** Ooopss, NOT able to write job to output, sorry :(')
                #list1.to_csv("output.csv", encoding=None, index=False)
                #writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')
                #list1.to_excel(writer,'Sheet1')
                #print(list1)
                #writer.save()

                count_application = count_application + 1

                if count_application % 20 == 0:
                    print('\n\n****************************************\n\n')
                    print('Time for a nap - see you in 10 min..')
                    print('\n\n****************************************\n\n')
                    time.sleep (600)

                if count_job == len(jobs):
                    jobs_per_page = jobs_per_page + 25
                    count_job = 0
                    print('\n\n****************************************\n\n')
                    print('Going to next jobs page, YEAAAHHH!!')
                    print('\n\n****************************************\n\n')
                    self.avoid_lock()
                    self.browser, jobs_per_page = self.next_jobs_page(jobs_per_page)



        self.finish_apply()

    def get_job_links(self, page):
        links = []
        for link in page.find_all('a'):
            url = link.get('href')
            if url:
                if '/jobs/view' in url:
                    links.append(url)
        return set(links)

    def get_job_page(self, job):
        root = 'www.linkedin.com'
        if root not in job:
            job = 'https://www.linkedin.com'+job
        self.browser.get(job)
        self.job_page = self.load_page(sleep=0.5)
        return self.job_page

    def got_easy_apply(self, page):
        button = page.find("button", class_="jobs-s-apply__button js-apply-button")
        return len(str(button)) > 4

    def get_easy_apply_button(self):
        button_class = "jobs-s-apply--top-card jobs-s-apply--fadein inline-flex mr2 jobs-s-apply ember-view"
        button = self.job_page.find("div", class_=button_class)
        return button

    def easy_apply_xpath(self):
        button = self.get_easy_apply_button()
        button_inner_html = str(button)
        list_of_words = button_inner_html.split()
        next_word = [word for word in list_of_words if "ember" in word and "id" in word]
        ember = next_word[0][:-1]
        xpath = '//*[@'+ember+']/button'
        return xpath

    def click_button(self, xpath):
        triggerDropDown = self.browser.find_element_by_xpath(xpath)
        time.sleep(0.5)
        triggerDropDown.click()
        time.sleep(1)

    def load_page(self, sleep=1):
        scroll_page = 0
        while scroll_page < 4000:
            self.browser.execute_script("window.scrollTo(0,"+str(scroll_page)+" );")
            scroll_page += 200
            time.sleep(sleep)

        if sleep != 1:
            self.browser.execute_script("window.scrollTo(0,0);")
            time.sleep(sleep * 3)

        page = BeautifulSoup(self.browser.page_source, "lxml")
        return page

    def avoid_lock(self):
        x, _ = pyautogui.position()
        pyautogui.moveTo(x+200, None, duration=1.0)
        pyautogui.moveTo(x, None, duration=0.5)
        pyautogui.keyDown('ctrl')
        pyautogui.press('esc')
        pyautogui.keyUp('ctrl')
        time.sleep(0.5)
        pyautogui.press('esc')

    def next_jobs_page(self, jobs_per_page):
        self.browser.get(
            #"https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=" +
            "https://www.linkedin.com/jobs/search/?keywords=" +
            self.position + self.location + "&start="+str(jobs_per_page))
        self.avoid_lock()
        self.load_page()
        return (self.browser, jobs_per_page)

    def finish_apply(self):
        self.browser.close()


if __name__ == '__main__':

    print("\nLet's scrape some jobs!\n")

    app = login.LoginGUI()
    app.mainloop()

    #get user info info
    username=app.frames["StartPage"].username
    password=app.frames["StartPage"].password
    language=app.frames["PageOne"].language
    position=app.frames["PageTwo"].position
    location_code=app.frames["PageThree"].location_code
    if location_code == 1:
        location=app.frames["PageThree"].location
    else:
        location = app.frames["PageFour"].location
    resumeloctn=app.frames["PageFive"].resumeloctn

    print  ("\nUsername:  "+ username,
            "\nPassword:  "+ password,
            "\nLanguage:  "+ language,
            "\nPosition:  "+ position,
            "\nLocation:  "+ location)

    # username = ''
    # password = ''
    # language = ''
    # position = ''
    # location = ''

    #start bot
    bot = EasyApplyBot(username,password, language, position, location) #, resumeloctn)
    bot.start_apply()
