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
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

commentAuthorNameList, commentAuthorNoteList, commentAuthorInformationList, commentAuthorDateList = [], [], [], []
ingredientsNameDatabaseList = []
ingredientsSimilarityList = []
ingredientsNameSaver = []

with open('scraping/ingredients_list.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        ingredientsNameDatabaseList.append(row[2])
        line_count += 1

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def findIngredientSimilarity(ingredient):
    choosedIngredient = ""
    similarityRatio = 0
    ingredientFound = 0
    for ingredientDB in ingredientsNameDatabaseList :
        if (ingredient+" ") in ingredientDB:
            choosedIngredient = ingredientDB
            ingredientFound = 1
        else:
            if ingredientFound == 1:
                break
            similarity = similar(ingredient, ingredientDB)
            if (similarity > similarityRatio and similarity > 0.666):
                similarityRatio = similarity
                choosedIngredient = ingredientDB
    ingredientsSimilarityList.append(choosedIngredient)
    #print(ingredient+"\t-\t"+choosedIngredient+"\n")
    return choosedIngredient

def funidecode(s):
    return unidecode.unidecode(s)

def removeEverythingThatIsntChar(s):
    regex = re.compile('[^a-zA-Z]')
    return regex.sub('', s)

def commentsDataExtraction():
    for commentAuthorName in soup.find_all("p", "MuiTypography-root MuiTypography-h6"):
        commentAuthorName = commentAuthorName.text.strip()
        if (commentAuthorName == ""):
            commentAuthorName = "Inconnu"
        commentAuthorNameList.append(funidecode(commentAuthorName))

    for commentAuthorNote in soup.find_all("span", "SHRD__sc-10plygc-0 jHwZwD"):
        commentAuthorNote = commentAuthorNote.text.strip()
        if (commentAuthorNote == ""):
            commentAuthorNote = "Inconnu"
        commentAuthorNoteList.append(funidecode(commentAuthorNote))
    
    for commentAuthorInformation in soup.find_all("p", "SHRD__sc-10plygc-0 bzAHrL"):
        commentAuthorInformation = commentAuthorInformation.text.strip()
        if (commentAuthorInformation == ""):
            commentAuthorInformation = "Inconnu"
        commentAuthorInformationList.append(funidecode(commentAuthorInformation).replace("\n", "").replace("\t", "").replace("\r", "").replace('"', "'"))

    for commentAuthorDate in soup.find_all("p", "MuiTypography-root MuiTypography-body2"):
        commentAuthorDate = commentAuthorDate.text.strip()
        if (commentAuthorDate == ""):
            commentAuthorDate = "Inconnu"
        commentAuthorDateList.append(funidecode(commentAuthorDate))

def commentsDataFileWriter():
    # fCommentsData.write("{}\n".format(str(commentAuthorInformationList)))
    for i in range(0, len(commentAuthorNameList)):
        print("\n")
        #print(commentAuthorInformationList[i].encode("utf-8"))
        commentAuthorName = commentAuthorNameList[i].replace('"', "'")
        commentAuthorInformation = commentAuthorInformationList[i].replace("\n", "").replace("\t", "").replace("\r", "").replace('"', "'")
        #print(commentAuthorInformation)
        fData.write("mm:comment-{}-{} rdf:type mm:comment .\n".format(recipeUri, i))
        fData.write("<{}> mm:comment mm:comment-{}-{} .\n".format(recipeUrl, recipeUri, i))
        fData.write("mm:comment-{}-{} mm:author-name \"{}\" .\n".format(recipeUri, i, commentAuthorName))
        fData.write("mm:comment-{}-{} mm:note \"{}\" .\n".format(recipeUri, i, commentAuthorNoteList[i]))
        fData.write("mm:comment-{}-{} mm:information \"{}\" .\n".format(recipeUri, i, commentAuthorInformation))
        fData.write("mm:comment-{}-{} mm:date \"{}\" .\n".format(recipeUri, i, commentAuthorDateList[i]))

def findReferencedIngredients(ingredient):
    choosedIngredient = ""
    similarityRatio = 0
    ingredientFound = 0
    for ingredientDB in ingredientsNameSaver:
        if (ingredient+" ") in ingredientDB:
            choosedIngredient = ingredientDB
            ingredientFound = 1
        else:
            if ingredientFound == 1:
                break
            similarity = similar(ingredient, ingredientDB)
            #print("{} - {} - {}".format(ingredient, ingredientDB, similarity))
            if (similarity > similarityRatio):
                similarityRatio = similarity
                choosedIngredient = ingredientDB
    #print("{} - {}\n".format(ingredient, choosedIngredient))
    return choosedIngredient

def snake_case(s) :
    return '-'.join(
        sub('([A-Z\u00C0-\u024F\u1E00-\u1EFF][a-z\u00C0-\u024F\u1E00-\u1EFF]+)', r' \1',
        sub('([A-Z\u00C0-\u024F\u1E00-\u1EFF]+)', r' \1',
        s.replace('\'', '').replace('à', 'a').replace('ç', 'c').replace('é', 'e').replace('è', 'e').replace('(', '').replace(')', '').replace(',', '').replace(';', '').replace('+', '').replace('.', '').replace('/', '-').replace('!', '').replace('?', ''))).split()).lower()

def snake_case_v2(s):
    s = s.replace(' ', '-').replace('\'', '').replace('à', 'a').replace('ç', 'c').replace('é', 'e').replace('è', 'e').replace('(', '').replace(')', '').replace(',', '').replace(';', '').replace('+', '').replace('.', '').replace('/', '-').replace('!', '').replace('?', '')
    k = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-"
    getVals = list(filter(lambda x: x in k, s))
    result = "".join(getVals)
    return result

def remove_accents(text):
    return unidecode.unidecode(text).replace('A(c)', 'e').replace('ASS', 'c').replace('A"', 'e').replace('AC/', 'a').replace('Aa', 'e').replace("A(r)", "i").replace("A>>", "u")

def comment_weight_eval(text):
    weight = 0
    return weight

def stringNumberSeparator(s) :
    text=""
    numbers=""
    res=[]
    s = unidecode.unidecode(s)
    s = s.replace("1a2", "}").replace("A ", "{").replace(".{.", "]")
    for i in s:
        if(i == "}"):
            numbers+="une demi"
            continue
        if(i == "{"):
            numbers+=""
            continue
        if(i == "]"):
            text+=".a."
            continue
        if(i.isdigit() or i == "/"):
            numbers+=i
        else:
            text+=i
    res.append(text)
    res.append(numbers)
    return res

recipeTypeList = ["aperitif-ou-buffet","entree","plat-principal","dessert"]
recipeCounter = 0

ingredientRepetitionData = []
numberOfRepeatedIngredient = []
ingredientsListForRepeatition = []
ingredientsToSearchNutritionalValues = []

fData = open("scraping/fData2.txt", mode="w", encoding="utf-8")

fData.write("@prefix mm: <http://mamarmite.com/> .\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n\n")

for recipeType in recipeTypeList :
    urlPage = "https://www.marmiton.org/recettes/index/categorie/{}?rcp=0".format(recipeType)
    page = urlopen(urlPage)
    html = page.read().decode("iso8859-1")
    #html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    soupCode = soup.encode('iso8859-1')
    #soupCode = soup.encode('utf-8')

    recipeTitleList, recipeLinkList = [], []

    for recipeTitle in soup.find_all("h4", "recipe-card__title") :
        recipeTitleList.append(recipeTitle.text.strip())

    for recipeLink in soup.find_all("a", "recipe-card-link") :
        recipeLinkList.append(recipeLink.get('href'))

    f = open("scraping/url-extraction/url-extraction-{}.txt".format(recipeType), "w")
    for i in range(0, len(recipeTitleList)) :
        f.write(recipeTitleList[i]+";"+recipeLinkList[i]+"\n")
    f.close()

    print(recipeType)

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome(ChromeDriverManager().install())

    ingredientsIsDefined = []

    for i in range(0, len(recipeLinkList)) :
        stepCounter = 0

        commentAuthorNameList.clear()
        commentAuthorNoteList.clear()
        commentAuthorInformationList.clear()
        commentAuthorDateList.clear()

        recipeUrl = recipeLinkList[i]
        # TODO: remettre recipeUrl pour qu'il parcourt tous les liens
        recipeUrl = "https://www.marmiton.org/recettes/recette_soupe-poireaux-pommes-de-terre_33013.aspx"
        #if (i == 1):
        #    recipeUrl = "https://www.marmiton.org/recettes/recette_mojito-cubain_80528.aspx"
        page = urlopen(recipeUrl)
        
        urlData = urlparse(recipeUrl)
        urlPath = urlData.path.replace('.', '/').split('/')
        completeRecipeUri = urlPath[2].split('_', 1)[1]
        #print("=============================================\n{}".format(recipeUri).split('_', 1)[1])
        recipeUri = completeRecipeUri.split('_', 1)[1]

        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        soupCode = soup.encode('utf-8')

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

        fData.write("<{}> rdf:type mm:recipe .\n".format(recipeUrl))
        
        fData.write("<{}> mm:recipe-title \"{}\" .\n".format(recipeUrl, recipeTitle.replace('"', "'").replace("\n", "").replace("\r", "").replace("\t", "")))
        fData.write("<{}> mm:recipe-type \"{}\" .\n".format(recipeUrl, recipeType))
        fData.write("<{}> mm:total-preparation-time \"{}\" .\n".format(recipeUrl, totalPreparationTime))
        fData.write("<{}> mm:difficulty \"{}\" .\n".format(recipeUrl, difficulty))
        fData.write("<{}> mm:price-range \"{}\" .\n".format(recipeUrl, priceRange))
        fData.write("<{}> mm:default-number-of-people-for-recipe \"{}\" .\n".format(recipeUrl, defaultNumberOfPeopleForRecipe))
        fData.write("<{}> mm:preparation-time \"{}\" .\n".format(recipeUrl, preparationTime))
        fData.write("<{}> mm:resting-time \"{}\" .\n".format(recipeUrl, restingTime))
        fData.write("<{}> mm:cooking-time \"{}\" .\n".format(recipeUrl, cookingTime))
        fData.write("<{}> mm:author-name \"{}\" .\n".format(recipeUrl, autherName))
        fData.write("<{}> mm:average-note \"{}\" .\n".format(recipeUrl, note))

        #commentsDataExtraction()
        #print(commentAuthorNameList)

        print(i, recipeTitle)

        ingredientsName = []
        similarIngredientName = []
        ingredientsQuantity = []
        toolsName = []
        
        instructionList = []
        usedIngredientsPerStep = []
        numberOfIngredientsPerStep = []
        ingredientsOrderList = []
        ingredientsPerStepList = []

        commentsAuthor = []
        commentsNote = []
        commentsInformation = []
        commentsDate = []
        commentsWeight = []

        ingredientsCounter = 0
        toolsCounter = 0
        
        instructionsCounter = 0
        totalUsedIngredientsCounter = 0

        commentsCounter = 0

        while(ingredientsCounter>=0):
            try :
                if(soup.select('span.SHRD__sc-10plygc-0.kWuxfa')[ingredientsCounter].text.strip()) :
                    ingredientsQuantity.append(soup.select('span.SHRD__sc-10plygc-0.epviYI')[ingredientsCounter].text.strip())
                    foundIngredient = soup.select('span.SHRD__sc-10plygc-0.kWuxfa')[ingredientsCounter].text.strip()
                    similarityFound = findIngredientSimilarity(foundIngredient)
                    ingredientsName.append(foundIngredient)
                    similarIngredientName.append(similarityFound)
                    #print(ingredientsName+" - "+similarIngredientName[-1])
                    #print("{} - {}".format(ingredientsName[-1], similarIngredientName[-1]))
                    ingredientsCounter = ingredientsCounter+1
            except :
                ingredientsCounter = -1

        while(toolsCounter>=0):
            try :
                if(soup.select('div.RCP__sc-1641h7i-3.iLcXC')[toolsCounter].text.strip()) :
                    toolsName.append(soup.select('div.RCP__sc-1641h7i-3.iLcXC')[toolsCounter].text.strip())
                    toolsCounter = toolsCounter+1
            except :
                toolsCounter = -1

        for instruction in soup.find_all("p", "RCP__sc-1wtzf9a-3 jFIVDw") :
            instructionList.append(instruction.text.strip().replace('"', "'").replace("\n", "").replace("\t", "").replace("\t", ""))
            instructionsCounter = instructionsCounter+1

        for usedIngredients in soup.find_all("div", "RCP__sc-1wtzf9a-4 WhwEU") :
            totalUsedIngredientsCounter = totalUsedIngredientsCounter+1

        #print(ingredientsName)
        #print(similarIngredientName)
        insertedIngredientName=""
        insertedIngredientQuantity=""
        ingredientsQuantitySeparatorList=""
        for componentCounter in range(0, len(ingredientsName)) :
            try: 
                insertedIngredientName = ingredientsName[componentCounter]
                insertedIngredientQuantity = ingredientsQuantity[componentCounter]
                # way to simplify regroup similarIngredientName[x] and ingredientsName[x] depending of the fact that similarIngredientName is empty or not
                if (similarIngredientName[componentCounter] != "") :
                    insertedIngredientName = similarIngredientName[componentCounter]
                if (insertedIngredientName.endswith("s")):
                    insertedIngredientName = insertedIngredientName[:-1]
                ingredientsQuantitySeparatorList = stringNumberSeparator(insertedIngredientQuantity)
                #print(ingredientsQuantitySeparatorList[1], ingredientsQuantitySeparatorList[0])
                #print(insertedIngredientName)
                ingredientName = insertedIngredientName.replace('"', "'").replace("\n", "").replace("\t", "").replace("\r", "")

                fData.write("mm:component-{}-{} rdf:type mm:component .\n".format(recipeUri, componentCounter))
                fData.write("mm:quantity-{}-{} rdf:type mm:quantity-properties .\n".format(snake_case_v2(remove_accents(insertedIngredientName)), recipeUri))
                fData.write("mm:quantity-{}-{} mm:quantity-value \"{}\" .\n".format(snake_case_v2(remove_accents(insertedIngredientName)), recipeUri, ingredientsQuantitySeparatorList[1]))
                fData.write("mm:quantity-{}-{} mm:mesurement-value \"{}\" .\n".format(snake_case_v2(remove_accents(insertedIngredientName)), recipeUri, ingredientsQuantitySeparatorList[0].strip()))

                ingredient = "mm:{}".format(snake_case_v2(remove_accents(insertedIngredientName)))
                if ingredient not in ingredientsIsDefined :
                    fData.write("{} mm:type mm:ingredient .\n".format(ingredient))
                    fData.write("{} mm:ingredient-name \"{}\" .\n".format(ingredient, ingredientName))
                    ingredientsIsDefined.append(ingredient)

                fData.write("mm:component-{}-{} mm:quantity mm:quantity-{}-{} .\n".format(recipeUri, componentCounter, snake_case_v2(remove_accents(insertedIngredientName)), recipeUri))
                fData.write("mm:component-{}-{} mm:is-a mm:{} .\n".format(recipeUri, componentCounter, snake_case_v2(remove_accents(insertedIngredientName))))
                fData.write("<{}> mm:component mm:component-{}-{} .\n".format(recipeUrl, recipeUri, componentCounter))
                ingredientRepetitionData.append(ingredientName)

            except:
                exception_type, exception_object, exception_traceback = sys.exc_info()
                filename = exception_traceback.tb_frame.f_code.co_filename
                line_number = exception_traceback.tb_lineno

                print("Error writing component :\nName: {}\nQuantity: {}\nRecipe URL: {}".format(insertedIngredientName, ingredientsQuantitySeparatorList, recipeUrl))
                print("Exception type: ", exception_type)
                print("File name: ", filename)
                print("Line number: ", line_number)
                print("\n")
                #exit()
        
        # if (i == 1):
        #     exit()
        # continue
        for toolCounter in range(0, len(toolsName)) :
            try:
                fData.write("<{}> mm:used-tool \"{}\" .\n".format(recipeUrl, toolsName[toolCounter]))
            except:
                a = 1

        for componentCounter in soup.find_all("div", "RCP__sc-1wtzf9a-2 fBqfpG") :
            usedIngredientsPerStep.append(componentCounter)

        for componentCounter in range(0, instructionsCounter) :
            try:
                numberOfIngredientsPerStep.append(str(usedIngredientsPerStep[componentCounter]).count("RCP__sc-1wtzf9a-4 WhwEU"))
            except:
                print('Instructions parkour problem')

        for componentCounter in soup.find_all("img", "bkoLvf", alt=True) :
            ingredientsOrderList.append(str(componentCounter['alt']))

        #print(ingredientsOrderList)
        #print(numberOfIngredientsPerStep)

        ingredientNumber = 0
        stepPosition = 0

        fData.write("mm:step-list-{} rdf:type rdf:Seq .\n".format(recipeUri))
        fData.write("<{}> mm:my-step-list mm:step-list-{} .\n".format(recipeUrl, recipeUri))
        ingredientsNameSaver = ingredientsName
        for stepCounter in range(0, len(instructionList)):
            instruction = instructionList[stepCounter].replace('"', "'").replace("\n", "").replace("\t", "").replace("\r", "")
            # print(instruction.encode("utf-8"))
            # instructionUni = instruction.encode("utf-8")
            # print(unidecode.unidecode(instructionUni))
            #print(unidecode)
            fData.write("mm:step-{}-{} rdf:type mm:step .\n".format(recipeUri, stepCounter))
            fData.write("mm:step-list-{} rdf:_{} mm:step-{}-{} .\n".format(recipeUri, stepCounter+1, recipeUri, stepCounter))
            fData.write("mm:step-{}-{} mm:information \"{}\" .\n".format(recipeUri, stepCounter, instruction))
            if (numberOfIngredientsPerStep[stepCounter] == 0) :
                stepPosition = stepPosition + 1
                continue
            while (numberOfIngredientsPerStep[stepCounter] > 0) :
                try:
                    referencedIngredient = findReferencedIngredients(ingredientsOrderList[ingredientNumber])
                    if (referencedIngredient.endswith("s")):
                        referencedIngredient = referencedIngredient[:-1]
                    ingredient = "mm:{}".format(snake_case_v2(remove_accents(referencedIngredient)))
                    if ingredient not in ingredientsIsDefined :
                        fData.write("{} rdf:type mm:ingredient .\n".format(ingredient, referencedIngredient))
                        fData.write("{} mm:ingredient-name \"{}\" .\n".format(ingredient, referencedIngredient))
                        ingredientsIsDefined.append(ingredient)
                    fData.write("mm:step-{}-{} mm:required-ingredient mm:{} .\n".format(recipeUri, stepCounter, snake_case_v2(remove_accents(referencedIngredient))))
                    ingredientNumber = ingredientNumber + 1
                    numberOfIngredientsPerStep[stepCounter] = numberOfIngredientsPerStep[stepCounter] - 1
                except:
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    filename = exception_traceback.tb_frame.f_code.co_filename
                    line_number = exception_traceback.tb_lineno

                    print("Error writing component :\nName: {}\nQuantity: {}\nRecipe URL: {}".format(insertedIngredientName, ingredientsQuantitySeparatorList, recipeUrl))
                    print("Exception type: ", exception_type)
                    print("File name: ", filename)
                    print("Line number: ", line_number)
                    print("\n")

        driver.get(recipeUrl)
        html = page.read().decode("iso8859-1")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        soupCode = soup.encode('iso8859-1')

        driver.maximize_window()  # For maximizing window
        driver.implicitly_wait(3)  # gives an implicit wait for 20 second

        resultAgreeButton = driver.find_elements(
            By.XPATH, '//*[@id="didomi-notice-agree-button"]/span')
        resultAgreeButtonPresent = len(resultAgreeButton)
        if (resultAgreeButtonPresent > 0):
            driver.find_element(
                By.XPATH, '//*[@id="didomi-notice-agree-button"]/span').click()
            #print("Agree button clicked")

        time.sleep(randint(1, 3))
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(randint(1, 3))

        commentsSection = driver.find_element(
            By.CSS_SELECTOR, "div[class='RCP__sc-2jkou4-1 cqYsJZ']")
        moreButton = commentsSection.find_elements(
            By.CSS_SELECTOR, "span[class='MuiTypography-root MuiTypography-caption']")

        moreButtonPresent = len(moreButton)

        if (moreButtonPresent > 0):
            # Click on the "more" button to show more comments in the pop up window
            #print("Element \"more\" exist")
            moreButtonClicker = commentsSection.find_element(
                By.CSS_SELECTOR, "span[class='MuiTypography-root MuiTypography-caption']")
            driver.execute_script("arguments[0].click();", moreButtonClicker)
            time.sleep(randint(1, 3))

            soup = BeautifulSoup(driver.page_source, "html.parser")
            #soupCode = soup.encode('iso8859-1')
            # TODO: make sure that a commentaire doesn't appear 2x in the same list (like we have done for the ingredients) But nope, bcs it's more complicated than that bcs if I detect a recurrence of the author name for example he will only skip the author name, but not his note, information, etc... bcs some other pp can have the same information, note as the author we are skipping and by doing so we will destroy the "logic" behind our commentaire treatment
            commentsDataExtraction()
            commentAuthorNoteList.pop(0)
            commentsDataFileWriter()
            time.sleep(randint(3, 5))
        else:
            print("Element \"more\" not exist")
            commentsDataExtraction()
            commentAuthorNoteList.pop(0)
            commentsDataFileWriter()
            time.sleep(randint(3, 5))

        #print(commentAuthorNameList)
        # Remove the average recipe note
        #print(commentAuthorNoteList)
        #print(commentAuthorInformationList)
        #print(commentAuthorDateList)

        stepCounter = 0

        #print(ingredientsPerStepList)
        #print(numberOfIngredientsPerStepSave)
        #temp = ingredientsPerStepList.split(',')
        #print(temp)
        #exit

        #try:
        #    fData.write("mm:step mm:property---step--ingredients--{} mm:ingredient-{}".format(recipeUri, ))
        #except:
        #    a = 1
#
        #for x in range(0, len(ingredientsPerStepList)) :
        #    try:
        #        fData.write("mm:step mm:step-ingredients-{} \"{}\" .\n".format(x, ingredientsPerStepList[x]))
        #        stepCounter = stepCounter+1
        #    except:
        #        a = 1

        print()

        recipeCounter = recipeCounter+1
        break
    driver.close()
    break
    
    #res = {}
    #for i in ingredientsSimilarityList:
    #    res[i] = ingredientsSimilarityList.count(i)
    #print("Size of the table estimating similar ingredients {}".format(len(ingredientsSimilarityList)))
    #print(res)

for i in ingredientRepetitionData:
    if i not in ingredientsListForRepeatition:
        ingredientsListForRepeatition.append(i)
        numberOfRepeatedIngredient.append(ingredientRepetitionData.count(i))

print("------------------------------\nIngredients list to search for nutritional value:")
with open("scraping/ingredientWithNutritionalValueToExtract.txt", mode="w", encoding="utf-8") as nutriFile :
    for i in range(0,len(ingredientsListForRepeatition)):
        #print("{} - {}".format(remove_accents(ingredientsListForRepeatition[i]), numberOfRepeatedIngredient[i]))
        if (numberOfRepeatedIngredient[i] > 3):
            ingredientsToSearchNutritionalValues.append(remove_accents(ingredientsListForRepeatition[i]))
            print(remove_accents(ingredientsListForRepeatition[i]))
            nutriFile.write("{}\n".format(remove_accents(ingredientsListForRepeatition[i])))


fData.close()
