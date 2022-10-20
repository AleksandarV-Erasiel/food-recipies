import time

from urllib.request import urlopen

# Load selenium components
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from random import randint

from bs4 import BeautifulSoup

recipeTypeList = ["aperitif-ou-buffet", "entree", "plat-principal", "dessert"]
recipeCounter = 0

for recipeType in recipeTypeList:
    urlPage = "https://www.marmiton.org/recettes/index/categorie/{}?rcp=0".format(
        recipeType)
    page = urlopen(urlPage)
    html = page.read().decode("iso8859-1")
    soup = BeautifulSoup(html, "html.parser")
    soupCode = soup.encode('iso8859-1')

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome(ChromeDriverManager().install())

    recipeTitleList, recipeLinkList = [], []

    for recipeTitle in soup.find_all("h4", "recipe-card__title"):
        recipeTitleList.append(recipeTitle.text.strip())

    for recipeLink in soup.find_all("a", "recipe-card-link"):
        recipeLinkList.append(recipeLink.get('href'))

    print(recipeType)

    for i in range(0, len(recipeLinkList)):
        recipeUrl = recipeLinkList[i]
        driver.get(recipeUrl)
        html = page.read().decode("iso8859-1")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        soupCode = soup.encode('iso8859-1')

        commentAuthorList = []

        recipeTitle = soup.select('h1.itJBWW')[0].text.strip()

        for commentAuthor in soup.find_all("p", "MuiTypography-root MuiTypography-h6"):
            commentAuthorList.append(commentAuthor.text.strip())

        print(commentAuthorList)

        print("\n********************************\n")
        print(i, recipeTitle)

        driver.maximize_window()  # For maximizing window
        driver.implicitly_wait(3)  # gives an implicit wait for 20 second

        resultAgreeButton = driver.find_elements(
            By.XPATH, '//*[@id="didomi-notice-agree-button"]/span')
        resultAgreeButtonPresent = len(resultAgreeButton)
        if (resultAgreeButtonPresent > 0):
            driver.find_element(
                By.XPATH, '//*[@id="didomi-notice-agree-button"]/span').click()
            print("Agree button clicked")
        #commentAuthorList = []
        # for commentAuthor in soup.find_all("p", "RCP__sc-ico2un-4 eMjDsn"):
        #    commentAuthorList.append(commentAuthor.text.strip())
        # print(commentAuthorList)

        time.sleep(randint(2, 4))
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(randint(2, 4))

        commentsSection = driver.find_element(
            By.CSS_SELECTOR, "div[class='RCP__sc-2jkou4-1 cqYsJZ']")
        moreButton = commentsSection.find_elements(
            By.CSS_SELECTOR, "span[class='MuiTypography-root MuiTypography-caption']")

        moreButtonPresent = len(moreButton)
        print(moreButtonPresent)
        if (moreButtonPresent > 0):
            print("Element \"more\" exist")
            moreButtonClicker = commentsSection.find_element(
                By.CSS_SELECTOR, "span[class='MuiTypography-root MuiTypography-caption']")
            driver.execute_script("arguments[0].click();", moreButtonClicker)
            time.sleep(randint(2, 4))
        else:
            print("Element \"more\" not exist")

    driver.close()
