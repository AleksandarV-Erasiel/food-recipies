import csv
import re
import sys
import time
import unicodedata
from difflib import SequenceMatcher
from random import randint
from re import sub
from urllib.parse import urlparse
from urllib.request import urlopen

import unidecode
from bs4 import BeautifulSoup
from pattern.text.fr import singularize
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
# Load selenium components
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

def remove_accents(text):
    return unidecode.unidecode(text).replace('a(c)', 'e').replace('ass', 'c').replace('a"', 'e').replace('ac/', 'a').replace('aa', 'e').replace("a(r)", "i").replace("a>>", "u")

def snake_case_v2(s):
    s = s.replace(' ', '-').replace('\'', '').replace('à', 'a').replace('ç', 'c').replace('é', 'e').replace('è', 'e').replace('(', '').replace(')', '').replace(',', '').replace(';', '').replace('+', '').replace('.', '').replace('/', '-').replace('!', '').replace('?', '')
    k = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-"
    getVals = list(filter(lambda x: x in k, s))
    result = "".join(getVals)
    return result

def extractIngredientsData():
    ingredientsList = []
    with open("scraping\ingredientWithNutritionalValueToExtract.txt", "r") as nutriFile:
        lines = nutriFile.readlines()
        for line in lines:
            ingredientsList.append(line.strip())
    return ingredientsList

def main():    
    ingredientsNutriList = extractIngredientsData()
    

    nutriDataNameList = []
    nutriDataValueList = []
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://ciqual.anses.fr/")
    switchFrench = driver.find_element(By.ID, "fr-switch")
    switchFrench.click()
    time.sleep(2)
    inputElement = driver.find_element(By.ID, "champ-recherche")
    for ingredient in ingredientsNutriList:
        nutriDataNameList.clear()
        nutriDataValueList.clear()
        inputElement.clear()
        inputElement.send_keys("{}".format(ingredient))
        inputElement.send_keys(Keys.ENTER)
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        #tables = soup.find_all("table", {"class":"table table-striped"})
        numberOfTable = len(soup.find_all("table"))
        if(numberOfTable == 0): 
            continue
        if(numberOfTable == 1):
            table = soup.find("table")
        else:
            table = soup.select("table")[0]
        print(f'----------------------------------------------\n{ingredient}')
        time.sleep(5)
        dataList = table.find_all("td")
        for i, data in enumerate(dataList, start=0):
            if i%5 == 0:
                nutriDataNameList.append(data.text.strip())
                continue
            if (i-1)%5 == 0:
                nutriDataValueList.append(data.text.strip())
                continue
        time.sleep(5)
        # TODO: ULTRA IMPORTANT: in the main file we are not inserting directly ingredient - we are doing ingredient.replace('"', "'").replace("\n", "").replace("\t", "").replace("\r", "") : Verify if it change anything :p
        with open("scraping/nutriData.txt", "a", encoding="utf-8") as nutriData:
            for i in range(0,len(nutriDataNameList)):
                # TODO: change the second modifier and put the URI instead of the ingredient name (or maybe not because we don't want to have a different ID with every recipe)
                nutriData.write("mm:{}-{} rdf:type mm:nutritional-properties .\n".format(snake_case_v2(remove_accents(ingredient)), snake_case_v2(remove_accents(nutriDataNameList[i]))))
                nutriData.write("mm:{} mm:nutritional-prop mm:{}-{} .\n".format(snake_case_v2(remove_accents(ingredient)), snake_case_v2(remove_accents(ingredient)), snake_case_v2(remove_accents(nutriDataNameList[i]))))
                nutriData.write("mm:{}-{} mm:nutri-name \"{}\" .\n".format(snake_case_v2(remove_accents(ingredient)), snake_case_v2(remove_accents(nutriDataNameList[i])), nutriDataNameList[i]))
                nutriData.write("mm:{}-{} mm:nutri-value \"{}\" .\n".format(snake_case_v2(remove_accents(ingredient)), snake_case_v2(remove_accents(nutriDataNameList[i])), nutriDataValueList[i]))
        time.sleep(3)

    driver.close()
    
main()