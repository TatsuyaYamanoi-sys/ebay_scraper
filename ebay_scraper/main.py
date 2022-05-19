import os
from time import sleep

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

"""
【website】ebay (検索ワード = nike)
【url】https://directshop.qoo10.jp/shop/itms?sk_idx=0&q=nike&locatedIn=&sk=nike
【query_options】
    location: 出品元（国）
    q: 検索KW 
    sk: 検索KW
    page: ページネイション
【memo】
    商品一覧はjsでレンダリングしている.(bsではスクレイピング不可. seleniumかrequests-htmlを使用)
    "次へ"を押すと, 前ページの最後の商品が一番上に含まれる.
     - よって, 1P48件Hitするがユニークな商品は2P以降47件
【reference】
・dockerでselenium
https://qiita.com/ryoheiszk/items/93b2d52eec370c09a22e
https://qiita.com/KWS_0901/items/5076a2f4cff544505c5d
https://ja.stackoverflow.com/questions/75662/docker-compose%E4%B8%8A%E3%81%A7selenium%E3%82%92%E5%8B%95%E3%81%8B%E3%81%99%E3%81%A8%E3%82%A8%E3%83%A9%E3%83%BC%E3%81%8C%E7%99%BA%E7%94%9F%E3%81%99%E3%82%8B

"""

# options = Options()
# options.add_argument('--headless')        # ヘッドレスモード時, driverのoptionsに渡す.
# driver = webdriver.Chrome(executable_path="C:\Users\user\Desktop\div\__on_going\ebay_scraper\chromedriver",
#     options=options
# )

driver = webdriver.Remote(
    # command_executor=os.environ['SELENIUM_URL'],
    command_executor='http://172.17.0.2:4444/wd/hub',
    desired_capabilities=DesiredCapabilities.CHROME.copy()
)       # <- docker

driver.implicitly_wait(15)

# class FailedScrapingException(Exception):
#     pass

class EbayScraper:
    url = "https://directshop.qoo10.jp/shop/itms?sk_idx=0&q=nike&locatedIn=&sk=nike"

    def __init__(self, driver):
        self.driver = driver

        self.page_num = 1
        self.product_num = 1
        self.product_titles = []
        self.product_urls = []
        self.error_msg = ''
        self.detail_df = pd.DataFrame(columns=['name', 'price', 'place', 'url'])

        self.driver.get(self.url)

    def set_page_product_list(self):
        try:
            WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.list_info > div.r_area > a')))
            sleep(2)
            elems = self.driver.find_elements(By.CSS_SELECTOR, 'div.list_info > div.r_area > a')
            for i, elem in enumerate(elems):
                print('page_product_num: ', i + 1)       # debug
                self.product_titles.append(elem.text)
                self.product_urls.append(elem.get_attribute("href"))
                print('product_num: ', len(self.product_urls))       # debug
                # print('title: ', elem.text)
                # print('URL: ', elem.get_attribute("href"))

        except Exception as e:
            self.error_msg = 'ページ情報の取得に失敗しました。\n' + str(e)
            print(self.error_msg)
            driver.quit()

    def set_all_product_list(self):
        try:
            self.set_page_product_list()
            while self.page_num < 2:
                WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.CLASS_NAME, 'next')))
                next_link = self.driver.find_element(By.CLASS_NAME, 'next')
                if next_link:
                    next_link.click()
                    self.page_num += 1
                    self.set_page_product_list()
                    
                else:
                    break

        except Exception as e:
            self.error_msg = '全件情報の取得に失敗しました。\n' + str(e)
            print(self.error_msg)
            driver.quit()

    def set_product_detail_list(self):
        try:
            for i, product_url in enumerate(self.product_urls):
                if i < 5:
                    self.driver.get(product_url)
                    WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.prod_area > div.r_area')))
                    parent_elem = self.driver.find_element(By.CSS_SELECTOR, 'div.prod_area > div.r_area')
                    title = parent_elem.find_element(By.CSS_SELECTOR, 'h1#item_title_org')
                    price = parent_elem.find_element(By.CSS_SELECTOR, 'span.BDsaleAmount')
                    place = parent_elem.find_element(By.CSS_SELECTOR, 'li.bd_on > dl > dd > p')
                    detail_ser = pd.Series({
                            'name': title.text, 
                            'price': price.text, 
                            'place': place.text, 
                            'url': product_url
                        }, name=i)
                    print(detail_ser)       # debug
                    self.detail_df = pd.concat([self.detail_df, pd.DataFrame(detail_ser).T])
                    

        except Exception as e:
            self.error_msg = '詳細情報の取得に失敗しました。\n' + str(e)
            print(self.error_msg)
            driver.quit()

    def get_product_list(self):
        product_list_data = {title: url for title, url in zip(self.product_titles, self.product_urls)}
        return product_list_data

    @property
    def product_detail(self):
        pass

    def write_to_csv(self, data):
        pass


es = EbayScraper(driver)
es.set_all_product_list()
sleep(.5)
es.set_product_detail_list()
print(es.detail_df)

# for i, (title, url) in enumerate(es.get_product_list_data().items()):
#     i += 1
#     print('number: ', i)
#     print('title: ', title)
#     print('url: ', url)

print(len(es.get_product_list()))   # debug
print(len(es.product_titles))   # debug


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