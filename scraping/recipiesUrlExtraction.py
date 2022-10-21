from urllib.request import urlopen

from bs4 import BeautifulSoup

from re import sub
import re
import unicodedata
import unidecode
import csv
from urllib.parse import urlparse
from difflib import SequenceMatcher
from pattern.text.fr import singularize
import sys

ingredientsNameList = []
ingredientsSimilarityList = []
ingredientsNameSaver = []

with open('scraping/ingredients_list.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        ingredientsNameList.append(row[2])
        line_count += 1

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def findIngredientSimilarity(ingredient):
    choosedIngredient = ""
    similarityRatio = 0
    ingredientFound = 0
    for ingredientDB in ingredientsNameList :
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
        s.replace('\'', '').replace('à', 'a').replace('ç', 'c').replace('é', 'e').replace('è', 'e').replace('(', '').replace(')', '').replace(',', '').replace(';', '').replace('+', ''))).split()).lower()

def remove_accents(text):
    return unidecode.unidecode(text).replace('A(c)', 'e').replace('ASS', 'c').replace('A"', 'e').replace('AC/', 'a').replace('Aa', 'e').replace("A(r)", "i").replace("A>>", "u")

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

fData = open("scraping/fData.txt", "w")

fData.write("@prefix mm: <http://mamarmite.com/> .\n@prefix dc: <http://purl.org/dc/elements/1.1> .\n\nmm:index dc:creator <http://vasiljevic.alwaysdata.net/> .\nmm:index dc:language \"fr\" .\n<http://vasiljevic.alwaysdata.net/> mm:name \"Aleksandar VASILJEVIC\" .\nmm:index mm:recipes mm:recipes-list .\n\n")

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

    for i in range(0, len(recipeLinkList)) :
        stepCounter = 0

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
            instructionList.append(instruction.text.strip())
            instructionsCounter = instructionsCounter+1

        for usedIngredients in soup.find_all("div", "RCP__sc-1wtzf9a-4 WhwEU") :
            totalUsedIngredientsCounter = totalUsedIngredientsCounter+1

        #print(ingredientsName)
        #print(similarIngredientName)
        insertedIngredientName=""
        insertedIngredientQuantity=""
        ingredientsQuantitySeparatorList=""
        for x in range(0, len(ingredientsName)) :
            try: 
                insertedIngredientName = ingredientsName[x]
                insertedIngredientQuantity = ingredientsQuantity[x]
                # way to simplify regroup similarIngredientName[x] and ingredientsName[x] depending of the fact that similarIngredientName is empty or not
                if (similarIngredientName[x] != "") :
                    insertedIngredientName = similarIngredientName[x]
                if (insertedIngredientName.endswith("s")):
                    insertedIngredientName = insertedIngredientName[:-1]
                ingredientsQuantitySeparatorList = stringNumberSeparator(insertedIngredientQuantity)
                #print(ingredientsQuantitySeparatorList[1], ingredientsQuantitySeparatorList[0])
                #print(insertedIngredientName)
                fData.write("mm:component mm:property---ingredient--quantity--properties--{} mm:ingredient-quantity-{} .\n".format(snake_case(remove_accents(insertedIngredientName)), snake_case(remove_accents(insertedIngredientName))))
                fData.write("mm:component mm:property---ingredient--name--{} mm:ingredient-{} .\n".format(snake_case(remove_accents(insertedIngredientName)), snake_case(remove_accents(insertedIngredientName))))
                fData.write("mm:ingredient-{} mm:name \"{}\" .\n".format(snake_case(remove_accents(insertedIngredientName)), insertedIngredientName))
                fData.write("mm:ingredient-quantity-{} mm:quantity \"{}\" .\n".format(snake_case(remove_accents(insertedIngredientName)), ingredientsQuantitySeparatorList[1]))
                fData.write("mm:ingredient-quantity-{} mm:mesurement-value \"{}\" .\n".format(snake_case(remove_accents(insertedIngredientName)), ingredientsQuantitySeparatorList[0].strip()))
            except:
                exception_type, exception_object, exception_traceback = sys.exc_info()
                filename = exception_traceback.tb_frame.f_code.co_filename
                line_number = exception_traceback.tb_lineno

                print("Error writing component :\nName: {}\nQuantity: {}\nRecipe URL: {}".format(insertedIngredientName, ingredientsQuantitySeparatorList, recipeUrl))
                print("Exception type: ", exception_type)
                print("File name: ", filename)
                print("Line number: ", line_number)

                #exit()
                    

        for x in range(0, len(toolsName)) :
            try:
                fData.write("mm:tool mm:tool-name-{} \"{}\" .\n".format(x, toolsName[x]))
            except:
                a = 1

        for x in soup.find_all("div", "RCP__sc-1wtzf9a-2 fBqfpG") :
            usedIngredientsPerStep.append(x)

        for x in range(0, instructionsCounter) :
            try:
                numberOfIngredientsPerStep.append(str(usedIngredientsPerStep[x]).count("RCP__sc-1wtzf9a-4 WhwEU"))
            except:
                print('Instructions parkour problem')

        for x in soup.find_all("img", "bkoLvf", alt=True) :
            ingredientsOrderList.append(str(x['alt']))

        #print(ingredientsOrderList)
        #print(numberOfIngredientsPerStep)

        ingredientNumber = 0
        stepCounter = 0

        ingredientsNameSaver = ingredientsName
        for i in range(0, len(instructionList)) :
            value = ""
            firstValue = numberOfIngredientsPerStep[i]
            if (numberOfIngredientsPerStep[i] == 0) :
                ingredientsPerStepList.append("")
                stepCounter = stepCounter + 1
                continue
            while (numberOfIngredientsPerStep[i] > 0) :
                referencedIngredient = findReferencedIngredients(ingredientsOrderList[ingredientNumber])
                if (referencedIngredient.endswith("s")):
                    referencedIngredient = referencedIngredient[:-1]
                #print(ingredientsOrderList[ingredientNumber]+" - "+referencedIngredient)
                #TODO: add a triplet from mm:ingredient-{snake_case(remove_accents(referencedIngredient))} to the name of the ingredient [see test with aperol and deau-petillante] MISSING NAME
                fData.write("mm:step mm:property---step--ingredients--{}-{} mm:ingredient-{} .\n".format(recipeUri, i, snake_case(remove_accents(referencedIngredient))))
                if (numberOfIngredientsPerStep[i] == firstValue) :
                    value = "{}".format(ingredientsOrderList[ingredientNumber])
                else :
                    value = "{},{}".format(value, ingredientsOrderList[ingredientNumber])
                ingredientNumber = ingredientNumber+1
                numberOfIngredientsPerStep[i] = numberOfIngredientsPerStep[i]-1
            ingredientsPerStepList.append(value)

        try:
            fData.write("mm:step mm:property---step--instructions--{} mm:instructions-{} .\n".format(recipeUri, recipeUri))
        except:
            a=1

        stepCounter = 0

        for x in range(0, len(instructionList)) :
            try:
                #fData.write("mm:step mm:property---step--instructions--{}-{} mm:instructions-{} .\n".format(recipeUri, stepCounter, recipeUri))
                fData.write("mm:instructions-{} mm:information-{} \"{}\" .\n".format(recipeUri, stepCounter, instructionList[x]))
                #fData.write("mm:step mm:step-instructions-{} \"{}\" .\n".format(x, instructionList[x]))
                stepCounter = stepCounter+1
            except:
                a=1

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
    
    #res = {}
    #for i in ingredientsSimilarityList:
    #    res[i] = ingredientsSimilarityList.count(i)
    #print("Size of the table estimating similar ingredients {}".format(len(ingredientsSimilarityList)))
    #print(res)

fData.close()
