from bs4 import BeautifulSoup
import json
import logging
import os
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


# Initialize logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.ERROR)

driver = webdriver.Chrome()

driver.implicitly_wait(5)

url = "https://uniecampus.coursecatalogue.cineca.it/corsi/2022/10031/insegnamenti/9999?schemaid=3165"

# Initialize the Chrome driver

wait_time = 1800 # wait time in seconds

wait = WebDriverWait(driver, wait_time) # Extract the text within a div with the class 'my-class' with explicit wait

file_location = os.path.abspath("index.html")

# url = input("No canonical link or meta tag found.\nPaste the url below: ")

# # Open the local index.html file
# try:

#     with open(file_location, encoding='ISO-8859-1') as f:
#         contents = f.read()
#     soup = BeautifulSoup(contents, 'lxml')

#     # Try to get canonical url
#     canonical_link = soup.find("link", rel="canonical")

#     if canonical_link:
#         url = canonical_link.get("href")
#         print("Canonical link found: ",url)
#     else:
#         meta_url = soup.find("meta",  property="og:url")
#         if meta_url:
#             url = meta_url.get("content")
#             print("og:url meta tag found: ",url)
#         elif not url:
#             print("No og:url meta tag found")
#             url = None
#         if not url:

#             try:
#                 url = input("No canonical link or meta tag found.\nPaste the url below: ")
#             except Exception as e:
#                 logging.error(f"Error in getting url from user: {e}")

# except Exception as e:
#     logging.error(f"Error in extracting url from index.html: {e}")

# Open the url
try:
    driver.get(url)
    print("URL Loaded:",url)

    # Check for JavaScript errors
    for entry in driver.get_log('browser'):
        logging.error(f"JavaScript error on page load: {entry}")

except Exception as e:
    logging.error(f"Error opening url: {e}")

print("Page loaded:",driver.title)

# Take the class name of the div from file
class_name = None

try:
    with open("classe.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        class_name = data.get("class", None)  # use "None" as a default if "class" key is not in the dictionary
        print("Class name found in classe.json: ",class_name)
except Exception as e:
    logging.error(f"Error loading class name from classe.json: {e}")

elements_list = []  # list to hold all the elements found

anno = 'u-titoletto u-color-links u-font-text ng-binding ng-scope'
tipologia = "u-color-text-light u-titoletto u-font-text ng-binding"
insegnamento = "card-insegnamento-header"
anno_di_offerta = "ng-binding"
cfu = "card-insegnamento-cfu ng-binding ng-scope"
ore = "card-insegnamento-ore ng-binding ng-scope"
ciclo = "card-insegnamento-footer2 ng-scope"

class_list = [anno, tipologia, insegnamento, anno_di_offerta, cfu, ore, ciclo]

dict_keys = {
    anno: "Anno",
    tipologia: "Tipologia",
    insegnamento: "Insegnamento",
    anno_di_offerta: "Anno di offerta",
    cfu: "CFU",
    ore: "Ore",
    ciclo: "Ciclo"
}

try:
    divs = driver.find_element(By.CLASS_NAME, class_name.replace(".",""))

    # Accessing each div and all the nested elements for their tag names
    try:
        print("Entering the block to log element data")  # Debug statement

        for div in divs:
            for element in div.find_elements(By.XPATH, ".//*"):
                try:
                    tag = element.tag_name
                    classname = element.get_attribute("class")
                    text = element.text.strip() if element.text else None

                    # print(f"Found element - Tag: {tag}, Class: {classname}, Text: {text}")  # print the element data

                    with open('elements_data.txt', 'w') as f:
                        f.write(f"Tag: {tag}, Class: {classname}, Text: {text}\n")

                except Exception as e:
                    print(f"Error accessing element data: ", e)
                    logging.error(f"Error accessing element data: {e}")

    except Exception as e:
        logging.error(f"Error producing list of tags: {e}")
        print(f"Error producing list of tags: {e}")  # Debug statement


    # Accessing each div and all the nested elements for their tag names
    for div in divs:
        element_found = {}

        for el in class_list:
            while True:
                try:
                    print(f"Looking for element with class: {el}")  # Added log
                    element = div.find_element(By.CLASS_NAME, el)
                    value = element.text.strip() if element.text else None
                    element_found[dict_keys.get(el)] = value
                    print(f"Found {dict_keys.get(el)} : {value}")  # print to check if the elements are being processed
                    break
                except NoSuchElementException:
                    print(f"No element with class {el} found.")
                    logging.error(f"No element with class {el} found.")
                    time.sleep(1)  # wait a bit before trying again
                except Exception as e:
                    print(f"Error extracting element with class {el}: ", e)
                    logging.error(f"Error extracting element with class {el}: {e}")
                    break

except Exception as e:
    logging.error(f"Error extracting text: {e}")
    print(f"Error extracting text: {e}")  # Debug statement


# Write elements found to a file
try:
    with open('elements_list.txt', 'w') as f:
        f.write(f"{elements_list}")
    print("Elements written to 'elements_list.txt'")
except Exception as e:
    logging.error(f"Error writing to file: {e}")

driver.quit()

# Write div text to an Excel file
try:
    df = pd.DataFrame(elements_list)
    df.to_excel("text.xlsx", index=False)
    print("Elements written to 'text.xlsx'")
except Exception as e:
    logging.error(f"Error writing to Excel file: {e}")
