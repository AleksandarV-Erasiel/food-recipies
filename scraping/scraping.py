import csv
import re
import sys
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
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

def basicDataTreatment(fData, recipeLinkList, recipeType, i):
    recipeUrl = recipeLinkList[i]
    page = urlopen(recipeUrl)
    
    urlData = urlparse(recipeUrl)
    urlPath = urlData.path.replace('.', '/').split('/')
    recipeUri = urlPath[2].split('_', 1)[1]

    html = page.read().decode("iso8859-1")
    soup = BeautifulSoup(html, "html.parser")
    soupCode = soup.encode('iso8859-1')

    recipeTitle = soup.select('h1.itJBWW')[0].text.strip()
    totalPreparationTime = soup.select('p.RCP__sc-1qnswg8-1.iDYkZP')[0].text.strip()
    difficulty = soup.select('p.RCP__sc-1qnswg8-1.iDYkZP')[1].text.strip()
    priceRange = soup.select('p.RCP__sc-1qnswg8-1.iDYkZP')[2].text.strip()
    defaultNumberOfPeopleForRecipe = soup.select('span.SHRD__sc-w4kph7-4.hYSrSW')[0].text.strip()
    preparationTime = soup.select('span.SHRD__sc-10plygc-0.bzAHrL')[1].text.strip()
    restingTime = soup.select('span.SHRD__sc-10plygc-0.bzAHrL')[2].text.strip()
    cookingTime = soup.select('span.SHRD__sc-10plygc-0.bzAHrL')[3].text.strip()
    autherName = soup.select('div.RCP__sc-ox3jb6-5.fwQMuu')[0].text.strip()
    note = soup.select('span.SHRD__sc-10plygc-0.jHwZwD')[0].text.strip()

    fData.write("mm:recipes-list mm:recipe-{} <{}> .\n".format(recipeUri, recipeUrl))

    fData.write("<{}> mm:class--component--{} mm:component .\n".format(recipeUrl, recipeUri))
    fData.write("<{}> mm:class--tool--{} mm:tool .\n".format(recipeUrl, recipeUri))
    fData.write("<{}> mm:class--step--{} mm:step .\n".format(recipeUrl, recipeUri))
    fData.write("<{}> mm:class--comment--{} mm:comment .\n".format(recipeUrl, recipeUri))
    
    fData.write("<{}> mm:recipe-title \"{}\" .\n".format(recipeUrl, recipeTitle))
    fData.write("<{}> mm:recipe-type \"{}\" .\n".format(recipeUrl, recipeType))
    fData.write("<{}> mm:total-preparation-time \"{}\" .\n".format(recipeUrl, totalPreparationTime))
    fData.write("<{}> mm:difficulty \"{}\" .\n".format(recipeUrl, difficulty))
    fData.write("<{}> mm:price-range \"{}\" .\n".format(recipeUrl, priceRange))
    fData.write("<{}> mm:default-number-of-people-for-recipe \"{}\" .\n".format(recipeUrl, defaultNumberOfPeopleForRecipe))
    fData.write("<{}> mm:preparation-time \"{}\" .\n".format(recipeUrl, preparationTime))
    fData.write("<{}> mm:resting-time \"{}\" .\n".format(recipeUrl, restingTime))
    fData.write("<{}> mm:cooking-time \"{}\" .\n".format(recipeUrl, cookingTime))
    fData.write("<{}> mm:auther-name \"{}\" .\n".format(recipeUrl, autherName))
    fData.write("<{}> mm:note \"{}\" .\n".format(recipeUrl, note))

    print(i, recipeTitle)

def recipeDataParser(usefulData):
    soup = usefulData["soup"]
    recipeTitleList = usefulData["recipeTitleList"]
    recipeLinkList = usefulData["recipeLinkList"]
    #driver = usefulData["driver"]
    fData = usefulData["fData"]
    recipeType = usefulData["recipeType"]
    for i in range(0, len(recipeLinkList)):
        stepCounter = 0
        basicDataTreatment(fData, recipeLinkList, recipeType, i)

def driverInitializer():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome(ChromeDriverManager().install())
    return driver

def extractedRecipeSaver(recipeType, recipeTitleList, recipeLinkList):
    with open("scraping/url-extraction/url-extraction-{}.txt".format(recipeType), "w") as f:
        for i in range(0, len(recipeTitleList)) :
            f.write(recipeTitleList[i]+";"+recipeLinkList[i]+"\n")
    print(recipeType)

def recipeTitleParser(soup, recipeTitleList):
    for recipeTitle in soup.find_all("h4", "recipe-card__title") :
        recipeTitleList.append(recipeTitle.text.strip())
    return recipeTitleList

def recipeLinkParser(soup, recipeLinkList):
    for recipeLink in soup.find_all("a", "recipe-card-link") :
        recipeLinkList.append(recipeLink.get('href'))
    return recipeLinkList


def recipeUrlParser(recipeType):
    usefulPackage = dict()
    recipeTitleList, recipeLinkList = [], []

    urlPage = "https://www.marmiton.org/recettes/index/categorie/{}?rcp=0".format(recipeType)
    page = urlopen(urlPage)
    html = page.read().decode("iso8859-1")
    soup = BeautifulSoup(html, "html.parser")
    soupCode = soup.encode('iso8859-1')

    recipeTitleList = recipeTitleParser(soup, recipeTitleList)
    recipeLinkList = recipeLinkParser(soup, recipeLinkList)
    extractedRecipeSaver(recipeType, recipeTitleList, recipeLinkList)
    # TODO: use the drive at the right place - useless here
    driver = 0#driverInitializer()
    usefulPackage["soup"], usefulPackage["recipeTitleList"], usefulPackage["recipeLinkList"], usefulPackage["driver"] = soup, recipeTitleList, recipeLinkList, driver
    return usefulPackage

def recipesScraping(recipeTypeList):
    with open("scraping/fData2.txt", "w") as fData:
        usefulData = {'fData': fData}
        fData.write("@prefix mm: <http://mamarmite.com/> .\n@prefix dc: <http://purl.org/dc/elements/1.1> .\n\nmm:index dc:creator <http://vasiljevic.alwaysdata.net/> .\nmm:index dc:language \"fr\" .\n<http://vasiljevic.alwaysdata.net/> mm:name \"Aleksandar VASILJEVIC\" .\nmm:index mm:recipes mm:recipes-list .\n\n")
        for recipeType in recipeTypeList :
            usefulData["recipeType"] = recipeType
            usefulRecipeUrlPackage = recipeUrlParser(recipeType)
            usefulData["soup"] = usefulRecipeUrlPackage["soup"]
            usefulData["recipeTitleList"] = usefulRecipeUrlPackage["recipeTitleList"]
            usefulData["recipeLinkList"] = usefulRecipeUrlPackage["recipeLinkList"]
            recipeDataParser(usefulData)

def saveDatabaseData(dbList):
    with open('scraping/ingredients_list.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            dbList.append(row[2])
            line_count += 1

def main():
    ingredientsNameDatabaseList = []
    recipeTypeList = ["aperitif-ou-buffet","entree","plat-principal","dessert"]

    saveDatabaseData(ingredientsNameDatabaseList)
    recipesScraping(recipeTypeList)

main()
