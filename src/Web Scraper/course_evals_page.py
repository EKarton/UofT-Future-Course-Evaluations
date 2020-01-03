import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

class CourseEvalsPage():

    def __init__(self, driver):
        self.driver = driver

    def goto_next_page(self):
        print("Going to next page")
        self.driver.find_element_by_xpath('//*[@id="fbvGridPagingContentHolderLvl1"]/table/tbody/tr/td[6]/input').click()
        time.sleep(3)

    def set_page_number(self, page_num):
        print("Jumping to page", page_num)
        self.driver.find_element_by_xpath('//*[@id="gridPaging__getFbvGrid"]').send_keys(Keys.BACKSPACE)
        self.driver.find_element_by_xpath('//*[@id="gridPaging__getFbvGrid"]').send_keys(str(page_num))
        self.driver.find_element_by_xpath('//*[@id="gridPaging__getFbvGrid"]').send_keys(Keys.ENTER)
        time.sleep(3)

    def get_cur_page_num(self):
        print("Getting page number")
        return int(self.driver.find_element_by_xpath('//*[@id="gridPaging__getFbvGrid"]').text)

    def get_max_pages(self):
        print("Getting max pages")
        return int(self.driver.find_element_by_xpath('//*[@id="fbvGridPagingContentHolderLvl1"]/table/tbody/tr/td[5]').text)

    def set_max_pages(self, max_pages):
        print("Setting max pages to", max_pages)
        element = self.driver.find_element_by_xpath('//*[@id="fbvGridPageSizeSelectBlock"]/select')
        Select(element).select_by_visible_text(str(max_pages))
        time.sleep(3)

    def get_headers(self):
        print("Getting headers")

        html_string = self.driver.page_source
        html_source = BeautifulSoup(html_string, 'lxml')

        header_element = html_source.find("tr", { "class" : "gHeader" })
        cell_elements = header_element.find_all("th")

        header = []
        for cell in cell_elements:
            header.append(cell.get_text())

        return header

        # header_elements = self.driver.find_element_by_xpath('//*[contains(@class, \'gHeader\')]')
        # cell_elements = header_elements.find_elements_by_tag_name('th')

        # header = []
        # for cell in cell_elements:
        #     header.append(cell.text)

        # return header

    def get_evaluations(self):
        print("Getting evaluations")

        # Parse the HTML (faster than using Selenium) (1 seconds)
        html_string = self.driver.page_source
        html_source = BeautifulSoup(html_string, 'lxml')

        rows_with_data = html_source.find_all("tr", { "class" : "gData" })
        datapoints = []

        for row in rows_with_data:
            cells = row.find_all("td")

            datapoint = []
            for cell in cells:
                datapoint.append(cell.get_text())

            datapoints.append(datapoint)

        return datapoints

        # Using standard Selenium XPATHS (slow!) (12 seconds)
        # rows_with_data = self.driver.find_elements_by_xpath('//*[contains(@class, \'gData\')]')

        # datapoints = []

        # for row in rows_with_data:
        #     cells = row.find_elements_by_tag_name('td')

        #     datapoint = []
        #     for cell in cells:
        #         datapoint.append(cell.text)

        #     datapoints.append(datapoint)

        # return datapoints

