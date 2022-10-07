from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", chrome_options=options)

url = "https://www.marmiton.org/recettes/recette_caviar-d-aubergines_17847.aspx"
page = urlopen(url)
html = page.read().decode("iso8859-1")
soup = BeautifulSoup(html, "html.parser")
soupCode = soup.encode('iso8859-1')
#print(soupCode)
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

#ingredients = soup.find_all('span.SHRD__sc-10plygc-0.kWuxfa')
ingredientsName = []
ingredientsQuantity = []
toolsName = []
commentsAuthor = []
commentsNote = []
commentsInformation = []
commentsDate = []
commentsWeight = []

ingredientsCounter = 0
toolsCounter = 0
commentsCounter = 0

while(ingredientsCounter>=0 & toolsCounter>=0 & commentsCounter>=0):
    try :
        if(soup.select('span.SHRD__sc-10plygc-0.kWuxfa')[ingredientsCounter].text.strip()) :
            ingredientsName.append(soup.select('span.SHRD__sc-10plygc-0.kWuxfa')[ingredientsCounter].text.strip())
            ingredientsQuantity.append(soup.select('span.SHRD__sc-10plygc-0.epviYI')[ingredientsCounter].text.strip())
            ingredientsCounter = ingredientsCounter+1
    except :
        ingredientsCounter = -1
        print('Ingredients extracted from the input document\n')

    try :
        if(soup.select('div.RCP__sc-1641h7i-3.iLcXC')[toolsCounter].text.strip()) :
            toolsName.append(soup.select('div.RCP__sc-1641h7i-3.iLcXC')[toolsCounter].text.strip())
            toolsCounter = toolsCounter+1
    except :
        toolsCounter = -1
        print('Tools extracted from the input document\n')

    try:
        if(soup.select('div.RCP__sc-ico2un-1.bHWTUL.RCP__sc-1ijs2qz-0.elAXdq')[commentsCounter].text.strip()) :
            commentsAuthor.append(soup.select('p.MuiTypography-root.MuiTypography-h6')[commentsCounter].text.strip())
            commentsNote.append(soup.select('span.SHRD__sc-10plygc-0.jHwZwD')[commentsCounter].text.strip())
            commentsInformation.append(soup.select('p.SHRD__sc-10plygc-0.bzAHrL')[commentsCounter].text.strip())
            commentsDate.append(soup.select('p.MuiTypography-root.MuiTypography-body2')[commentsCounter].text.strip())
            commentsCounter = commentsCounter+1
    except :
        commentsCounter = -1
        print('Comments extracted from the input document\n')

for x in range(0, len(ingredientsName)) :
    try: 
        print(ingredientsQuantity[x], ingredientsName[x])
    except:
        print('')

for x in range(0, len(toolsName)) :
    try:
        print(toolsName[x])
    except:
        print('')

for x in range(0, len(commentsAuthor)) :
    try:
        print(commentsAuthor[x])
        print(commentsDate[x])
        print(commentsNote[x])
        print(commentsInformation[x])
        print('\n')
    except:
        print('aa')

print('\n================================')
print('recipeTitle', recipeTitle)
print('totalPreparationTime', totalPreparationTime)
print('difficulty', difficulty)
print('priceRange', priceRange)
print('defaultNumberOfPeopleForRecipe', defaultNumberOfPeopleForRecipe)
print('preparationTime', preparationTime)
print('restingTime', restingTime)
print('cookingTime', cookingTime)
print('autherName', autherName)
print('note', note)

#print(recipeTitle +'|'+ totalPreparationTime+'|'+difficulty+'|'+priceRange+'|'+defaultNumberOfPeopleForRecipe+'|'+preparationTime+'|'+restingTime+'|'+cookingTime+'|'+autherName+'|'+note)