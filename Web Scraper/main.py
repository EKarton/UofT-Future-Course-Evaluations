import time
import os

import csv

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

from quercus_page import QuercusPage
from course_evals_page import CourseEvalsPage

def main():
    # Load credentials from the .env file
    load_dotenv()
    utorid = os.getenv("UTOR_ID")
    password = os.getenv("PASSWORD")

    browser = None

    try:
        chrome_options = Options()  
        chrome_options.add_argument("--headless")  

        browser = webdriver.Chrome(executable_path='chromedriver', options=chrome_options)
        browser.implicitly_wait(10)

        quercus_page = QuercusPage(browser)
        quercus_page.goto_page()
        quercus_page.login(utorid, password)
        quercus_page.enter_course_evals()
        quercus_page.select_arts_and_science_undergraduate_course_evals()

        course_evals_page = CourseEvalsPage(browser)
        course_evals_page.set_max_pages(100)

        cur_page = 0
        max_pages = course_evals_page.get_max_pages()

        print(course_evals_page.get_headers())

        with open("raw-data.csv", "w") as dump_file:
            evals_writer = csv.writer(dump_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            # Get the headers
            headers = course_evals_page.get_headers()
            evals_writer.writerow(headers)

            # Get the evals
            while cur_page < max_pages:
                print('Currently at page', cur_page + 1)
                evaluations = course_evals_page.get_evaluations()
                print(evaluations)

                print('Dumping to a file')
                for evaluation in evaluations:
                    evals_writer.writerow(evaluation)
                print('Finished dumping to a file')

                course_evals_page.goto_next_page()
                cur_page += 1


    except Exception as error:
        print("ERROR AT", time.ctime())
        browser.quit()
        raise error

    finally:
        print("Finished")
        browser.quit() 

if __name__ == "__main__":
    main()