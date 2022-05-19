import os

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.expected_conditions import presence_of_element_located

"""
【website】ebay 
【queryoptions】
    location: 出品元（国）
    q: 検索KW 
    sk: 検索KW
    page: ページネイション
【memo】
    商品一覧はjsでレンダリングしている.(bsではスクレイピング不可. seleniumかrequests-htmlを使用)

【reference】
・dockerでselenium
https://qiita.com/ryoheiszk/items/93b2d52eec370c09a22e
https://qiita.com/KWS_0901/items/5076a2f4cff544505c5d
https://ja.stackoverflow.com/questions/75662/docker-compose%E4%B8%8A%E3%81%A7selenium%E3%82%92%E5%8B%95%E3%81%8B%E3%81%99%E3%81%A8%E3%82%A8%E3%83%A9%E3%83%BC%E3%81%8C%E7%99%BA%E7%94%9F%E3%81%99%E3%82%8B

"""
url = "https://www.google.com/"
# url = "https://directshop.qoo10.jp/shop/itms?sk_idx=0&q=nike&locatedIn=&sk=nike"
# driver = webdriver.Chrome(executable_path="C:\Users\user\Desktop\div\__on_going\ebay_scraper\chromedriver")

driver = webdriver.Remote(
    # command_executor=os.environ['SELENIUM_URL'],
    command_executor='http://172.17.0.3:4444/wd/hub',
    desired_capabilities=DesiredCapabilities.CHROME.copy()
)       # <- docker
# 暗黙的な待機処理
# タイムアウト時: NoSuchElementException
driver.implicitly_wait(10)

driver.get(url)

send_key = driver.find_element(By.NAME, 'q').send_keys('Selenium' + Keys.RETURN)

first_result = driver.find_element(By.CSS_SELECTOR, 'h3')
print(first_result.get_attribute("textContent"))

driver.quit()


# url = "https://directshop.qoo10.jp/shop/itms?sk_idx=0&q=nike&locatedIn=&sk=nike"

# res = requests.get(url)
# bs = BeautifulSoup(res.text, 'html.parser')

# cards = bs.select('div')
# title = []
# product_page_url = []

# print(cards[2])
# for card in cards:
#     title.append(card.contents[0])
#     product_page_url.append(card.attrs['href'])

# print(title)
# print(product_page_url)