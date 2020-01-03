from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

class QuercusPage:
    def __init__(self, driver):
        self.driver = driver

    def goto_page(self):
        self.driver.get('https://q.utoronto.ca/')

    def login(self, username, password):
        self.driver.find_element_by_xpath('//*[@id="username"]').send_keys(username)
        self.driver.find_element_by_xpath('//*[@id="password"]').send_keys(password)
        self.driver.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/form/button').click()

    def enter_course_evals(self):
        self.driver.find_element_by_xpath('//*[@id="context_external_tool_2015_menu_item"]/a').click()
        self.driver.find_element_by_xpath('//*[@id="wiki_page_show"]/div[2]/div/p[4]/a').click()
    
    def select_school_of_social_work_course_evals(self):
        self.__select_course_evals__(1)

    def select_engineering_graduate_course_evals(self):
        self.__select_course_evals__(2)

    def select_engineering_undergraduate_course_evals(self):
        self.__select_course_evals__(3)

    def select_arts_and_science_undergraduate_course_evals(self):
        self.__select_course_evals__(4)

    def select_faculty_of_information_course_evals(self):
        self.__select_course_evals__(5)

    def select_utm_course_evals(self):
        self.__select_course_evals__(6)

    def select_utsc_course_evals(self):
        self.__select_course_evals__(7)

    def __select_course_evals__(self, num):
        WebDriverWait(self.driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="tool_content"]')))

        self.driver.find_element_by_xpath('//*[@id="launcherElements"]/table/tbody/tr[' + str(num) + ']/td/a').click()
        self.driver.switch_to.window(self.driver.window_handles[1])