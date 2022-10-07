from urllib.request import urlopen

from bs4 import BeautifulSoup

from re import sub

def snake_case(s) :
    return '-'.join(
        sub('([A-Z\u00C0-\u024F\u1E00-\u1EFF][a-z\u00C0-\u024F\u1E00-\u1EFF]+)', r' \1',
        sub('([A-Z\u00C0-\u024F\u1E00-\u1EFF]+)', r' \1',
        s.replace('\'', '').replace('à', 'a').replace('ç', 'c').replace('é', 'e').replace('è', 'e'))).split()).lower()

print(snake_case("glaçon d'eau pétillante"))

def stringNumberSeparator(s) :
    text=""
    numbers=""
    res=[]
    for i in s:
        if(i.isdigit()):
            numbers+=i
        else:
            text+=i
    res.append(text)
    res.append(numbers)
    return res

recipeTypeList = ["aperitif-ou-buffet","entree","plat-principal","dessert"]
recipeCounter = 0

fData = open("fData.txt", "w")

fData.write("@prefix mm: <http://mamarmite.com/> .\n@prefix dc: <http://purl.org/dc/elements/1.1> .\n\nmm:index dc:creator <http://vasiljevic.alwaysdata.net/> .\nmm:index dc:language \"fr\" .\n<http://vasiljevic.alwaysdata.net/> mm:name \"Aleksandar VASILJEVIC\" .\nmm:index mm:recipes mm:recipes-list .\n")

for recipeType in recipeTypeList :
    urlPage = "https://www.marmiton.org/recettes/index/categorie/{}?rcp=0".format(recipeType)
    page = urlopen(urlPage)
    html = page.read().decode("iso8859-1")
    soup = BeautifulSoup(html, "html.parser")
    soupCode = soup.encode('iso8859-1')

    recipeTitleList, recipeLinkList = [], []

    for recipeTitle in soup.find_all("h4", "recipe-card__title") :
        recipeTitleList.append(recipeTitle.text.strip())

    for recipeLink in soup.find_all("a", "recipe-card-link") :
        recipeLinkList.append(recipeLink.get('href'))

    f = open("url-extraction/url-extraction{}.txt".format(recipeType), "w")
    for i in range(0, len(recipeTitleList)) :
        f.write(recipeTitleList[i]+";"+recipeLinkList[i]+"\n")
    f.close()

    print(recipeType)

    classComponentCounter = 0
    classToolCounter = 0
    classStepCounter = 0
    classCommentCounter = 0

    for i in range(0, len(recipeLinkList)) :
        recipeUrl = recipeLinkList[i]
        page = urlopen(recipeUrl)
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

        fData.write("mm:recipes-list mm:recipe-{} <{}> .\n".format(recipeCounter, recipeUrl))

        fData.write("<{}> mm:class--component--{} mm:component .\n".format(recipeUrl, classComponentCounter))
        fData.write("<{}> mm:class--tool--{} mm:tool .\n".format(recipeUrl, classToolCounter))
        fData.write("<{}> mm:class--step--{} mm:step .\n".format(recipeUrl, classStepCounter))
        fData.write("<{}> mm:class--comment--{} mm:comment .\n".format(recipeUrl, classCommentCounter))
        
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
                    ingredientsName.append(soup.select('span.SHRD__sc-10plygc-0.kWuxfa')[ingredientsCounter].text.strip())
                    ingredientsCounter = ingredientsCounter+1
            except :
                ingredientsCounter = -1
                #print('Ingredients extracted from the input document\n')

        while(toolsCounter>=0):
            try :
                if(soup.select('div.RCP__sc-1641h7i-3.iLcXC')[toolsCounter].text.strip()) :
                    toolsName.append(soup.select('div.RCP__sc-1641h7i-3.iLcXC')[toolsCounter].text.strip())
                    toolsCounter = toolsCounter+1
            except :
                toolsCounter = -1
                #print('Tools extracted from the input document\n')

        for instruction in soup.find_all("p", "RCP__sc-1wtzf9a-3 jFIVDw") :
            #print(instructionsCounter, instruction.text.strip())
            instructionList.append(instruction.text.strip())
            instructionsCounter = instructionsCounter+1

        for usedIngredients in soup.find_all("div", "RCP__sc-1wtzf9a-4 WhwEU") :
            totalUsedIngredientsCounter = totalUsedIngredientsCounter+1

        #print(instructionsCounter, totalUsedIngredientsCounter)

        for x in range(0, len(ingredientsName)) :
            try: 
                fData.write("mm:component mm:property---ingredient--quantity--properties--{} mm:ingredient-quantity-{} .\n".format(x, x))
                fData.write("mm:component mm:property---ingredient--name--{} mm:ingredient-{} .\n".format(snake_case(ingredientsName[x]), snake_case(ingredientsName[x])))
                
                ingredientsQuantitySeparatorList = stringNumberSeparator(ingredientsQuantity[x])

                fData.write("mm:ingredient-quantity-{} mm:quantity \"{}\" .\n".format(x, ingredientsQuantitySeparatorList[1]))
                fData.write("mm:ingredient-quantity-{} mm:mesurement-value \"{}\" .\n".format(x, ingredientsQuantitySeparatorList[0].strip()))
                fData.write("mm:ingredient-{} mm:name \"{}\" .\n".format(snake_case(ingredientsName[x]), ingredientsName[x]))
            except:
                a = 1

        for x in range(0, len(toolsName)) :
            try:
                #print(toolsName[x])
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

        ingredientNumber = 0

        for i in range(0, len(instructionList)) :
            value = ""
            firstValue = numberOfIngredientsPerStep[i]
            if (numberOfIngredientsPerStep[i] == 0) :
                ingredientsPerStepList.append("")
                continue
            while (numberOfIngredientsPerStep[i] > 0) :
                #ingredientsPerStepList.append(ingredientsOrderList[ingredientNumber])
                if (numberOfIngredientsPerStep[i] == firstValue) :
                    value = "{}".format(ingredientsOrderList[ingredientNumber])
                else :
                    value = "{},{}".format(value, ingredientsOrderList[ingredientNumber])
                ingredientNumber = ingredientNumber+1
                numberOfIngredientsPerStep[i] = numberOfIngredientsPerStep[i]-1
            ingredientsPerStepList.append(value)

        #print(ingredientsPerStepList)

        for x in range(0, len(instructionList)) :
            try:
                fData.write("mm:step mm:step-instructions-{} \"{}\" .\n".format(x, instructionList[x]))
            except:
                a=1

        for x in range(0, len(ingredientsPerStepList)) :
            try:
                #print(toolsName[x])
                fData.write("mm:step mm:step-ingredients-{} \"{}\" .\n".format(x, ingredientsPerStepList[x]))
            except:
                a = 1

        print()

        recipeCounter = recipeCounter+1

fData.close()
